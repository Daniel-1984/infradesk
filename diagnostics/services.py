"""
Motor de Diagnóstico de Chamados — InfraDesk
Lógica determinística baseada em regras, histórico e playbook.
Sem IA generativa. Sem RAG. Sem OpenAI.
"""

from django.utils import timezone
from datetime import timedelta

from .models import DiagnosticAnalysis, PlaybookEntry, RecurrenceAlert
from .utils import classify_domain, find_similar_tickets, compute_keyword_overlap


# Thresholds de reincidência
RECURRENCE_LIGHT = 2    # 2 ocorrências → alerta leve
RECURRENCE_MEDIUM = 3   # 3+ → moderado
RECURRENCE_CRITICAL = 5  # 5+ → crítico


def _get_recurrence_level(count):
    if count >= RECURRENCE_CRITICAL:
        return 'critical'
    elif count >= RECURRENCE_MEDIUM:
        return 'medium'
    elif count >= RECURRENCE_LIGHT:
        return 'light'
    return None


def analyze_recurrence(ticket):
    """
    Verifica reincidência do chamado com base em três escopos:
    - mesmo ativo
    - mesmo setor do criador
    - mesma categoria

    Retorna dict com contagens por período e nível de alerta.
    """
    from tickets.models import Ticket

    now = timezone.now()
    result = {
        'count_7d': 0,
        'count_15d': 0,
        'count_30d': 0,
        'level': None,
        'scope': None,
        'scope_value': None,
        'alerts': [],
    }

    base_qs = Ticket.objects.exclude(pk=ticket.pk)

    # --- Escopo 1: Mesmo ativo ---
    if ticket.asset_id:
        for days, field in [(7, 'count_7d'), (15, 'count_15d'), (30, 'count_30d')]:
            since = now - timedelta(days=days)
            count = base_qs.filter(asset=ticket.asset, created_at__gte=since).count()
            if count > result[field]:
                result[field] = count

        max_count = result['count_30d']
        level = _get_recurrence_level(max_count)
        if level:
            result['alerts'].append({
                'scope': 'asset',
                'scope_value': str(ticket.asset),
                'level': level,
                'occurrences': max_count,
            })

    # --- Escopo 2: Mesmo setor ---
    try:
        dept = ticket.created_by.profile.department
        if dept:
            for days, field in [(7, 'count_7d'), (15, 'count_15d'), (30, 'count_30d')]:
                since = now - timedelta(days=days)
                count = base_qs.filter(
                    created_by__profile__department=dept,
                    category=ticket.category,
                    created_at__gte=since
                ).count()
                if count > result[field]:
                    result[field] = count

            max_count = result['count_30d']
            level = _get_recurrence_level(max_count)
            if level:
                result['alerts'].append({
                    'scope': 'department',
                    'scope_value': dept.name,
                    'level': level,
                    'occurrences': max_count,
                })
    except Exception:
        pass

    # --- Escopo 3: Mesma categoria ---
    for days, field in [(7, 'count_7d'), (15, 'count_15d'), (30, 'count_30d')]:
        since = now - timedelta(days=days)
        count = base_qs.filter(category=ticket.category, created_at__gte=since).count()
        # Só atualiza se for maior (para não sobrescrever valores mais altos de outros escopos)
        if field == 'count_7d' and count > result['count_7d']:
            result['count_7d'] = count
        elif field == 'count_15d' and count > result['count_15d']:
            result['count_15d'] = count
        elif field == 'count_30d' and count > result['count_30d']:
            result['count_30d'] = count

    # Define o nível mais grave entre os alertas
    level_priority = {'critical': 3, 'medium': 2, 'light': 1}
    if result['alerts']:
        result['alerts'].sort(key=lambda x: level_priority.get(x['level'], 0), reverse=True)
        worst = result['alerts'][0]
        result['level'] = worst['level']
        result['scope'] = worst['scope']
        result['scope_value'] = worst['scope_value']

    return result


def find_matching_playbook(domain, title, description):
    """
    Busca a entrada de playbook mais relevante para o domínio e texto do chamado.
    Retorna (PlaybookEntry ou None, score_de_match).
    """
    entries = PlaybookEntry.objects.filter(domain=domain, is_active=True)
    if not entries.exists():
        # Tenta sem filtro de domínio se não encontrar para o domínio específico
        entries = PlaybookEntry.objects.filter(is_active=True)

    best_entry = None
    best_score = 0

    combined_text = f"{title} {description}"

    for entry in entries:
        keywords = entry.get_keywords_list()
        matched, total, percent = compute_keyword_overlap(combined_text, keywords)

        if percent > best_score:
            best_score = percent
            best_entry = entry

    # Só retorna se houver match mínimo de 20%
    if best_score < 20:
        return None, 0

    return best_entry, best_score


def calculate_confidence(domain_score, similar_count, recurrence_level, playbook_matched):
    """
    Calcula confiança geral do diagnóstico com base em evidências acumuladas.

    Pesos:
    - Domínio detectado com score alto → até 40 pts
    - Chamados similares encontrados → até 30 pts
    - Reincidência detectada → até 20 pts
    - Playbook com match → 10 pts

    Retorna (percent_0_100, label).
    """
    points = 0

    # Domínio (máx 40)
    points += min(domain_score * 0.4, 40)

    # Similaridade (máx 30) — escala logarítmica suave
    if similar_count >= 5:
        points += 30
    elif similar_count >= 3:
        points += 22
    elif similar_count >= 1:
        points += 12

    # Reincidência (máx 20)
    recurrence_pts = {'critical': 20, 'medium': 14, 'light': 8}
    points += recurrence_pts.get(recurrence_level, 0)

    # Playbook (10 pts)
    if playbook_matched:
        points += 10

    total = round(min(points, 95))  # Nunca 100% — o técnico sempre valida

    if total >= 70:
        label = 'high'
    elif total >= 40:
        label = 'medium'
    else:
        label = 'low'

    return total, label


def run_diagnostic(ticket):
    """
    Função principal do motor de diagnóstico.
    Analisa o chamado e salva/atualiza o DiagnosticAnalysis.

    Retorna o objeto DiagnosticAnalysis gerado.
    """
    from tickets.models import Ticket

    notes_parts = []

    # 1. Classificação de domínio
    domain, domain_score = classify_domain(ticket.title, ticket.description)
    notes_parts.append(f"Domínio detectado: {domain} (score bruto: {domain_score})")

    # 2. Similaridade com chamados anteriores (excluindo o atual)
    resolved_tickets = Ticket.objects.filter(
        status__in=['resolved', 'closed']
    ).exclude(pk=ticket.pk).select_related('created_by', 'created_by__profile', 'asset')

    similar_results = find_similar_tickets(
        target_ticket=ticket,
        candidates=resolved_tickets,
        min_score=0.15,
        max_results=5,
    )

    similar_count = len(similar_results)
    similar_ids = ','.join(str(r['ticket'].pk) for r in similar_results)

    if similar_results:
        top = similar_results[0]
        notes_parts.append(
            f"Chamado mais similar: #{top['ticket'].pk} ({top['percent']}%) "
            f"— tokens comuns: {', '.join(top['matched_tokens'][:5])}"
        )

    # 3. Reincidência
    recurrence = analyze_recurrence(ticket)
    recurrence_level = recurrence['level']

    if recurrence_level:
        notes_parts.append(
            f"Reincidência [{recurrence_level.upper()}]: {recurrence['scope_value']} "
            f"— 7d:{recurrence['count_7d']} | 15d:{recurrence['count_15d']} | 30d:{recurrence['count_30d']}"
        )
    else:
        notes_parts.append("Nenhuma reincidência significativa detectada.")

    # 4. Playbook
    playbook_entry, playbook_score = find_matching_playbook(
        domain, ticket.title, ticket.description
    )

    if playbook_entry:
        notes_parts.append(f"Playbook aplicado: '{playbook_entry.title}' (match: {round(playbook_score)}%)")
    else:
        notes_parts.append("Nenhum playbook com match suficiente (>20%).")

    # 5. Confiança geral
    confidence_percent, confidence_label = calculate_confidence(
        domain_score=domain_score,
        similar_count=similar_count,
        recurrence_level=recurrence_level,
        playbook_matched=playbook_entry,
    )

    # 6. Salva ou atualiza diagnóstico
    diagnostic, _ = DiagnosticAnalysis.objects.update_or_create(
        ticket=ticket,
        defaults={
            'domain_detected': domain,
            'domain_confidence_score': domain_score,
            'similar_tickets_count': similar_count,
            'similar_tickets_ids': similar_ids,
            'recurrence_level': recurrence_level,
            'recurrence_count_7d': recurrence['count_7d'],
            'recurrence_count_15d': recurrence['count_15d'],
            'recurrence_count_30d': recurrence['count_30d'],
            'playbook_matched': playbook_entry,
            'confidence': confidence_label,
            'confidence_percent': confidence_percent,
            'notes': '\n'.join(notes_parts),
        }
    )

    # 7. Cria/atualiza alertas de reincidência
    _save_recurrence_alerts(ticket, recurrence)

    return diagnostic


def _save_recurrence_alerts(ticket, recurrence_data):
    """
    Persiste os alertas de reincidência detectados na análise.
    """
    from tickets.models import Ticket

    for alert_data in recurrence_data.get('alerts', []):
        now = timezone.now()
        since_30d = now - timedelta(days=30)

        # Busca o primeiro chamado do período para registrar first_seen
        qs = Ticket.objects.filter(
            created_at__gte=since_30d,
        ).exclude(pk=ticket.pk).order_by('created_at')

        if alert_data['scope'] == 'asset' and ticket.asset_id:
            qs = qs.filter(asset=ticket.asset)
        elif alert_data['scope'] == 'department':
            try:
                dept = ticket.created_by.profile.department
                qs = qs.filter(created_by__profile__department=dept, category=ticket.category)
            except Exception:
                continue

        first_ticket = qs.first()
        first_seen = first_ticket.created_at if first_ticket else now

        RecurrenceAlert.objects.create(
            scope=alert_data['scope'],
            scope_value=alert_data['scope_value'],
            level=alert_data['level'],
            occurrences=alert_data['occurrences'],
            period_days=30,
            first_seen=first_seen,
            last_seen=now,
            is_resolved=False,
        )


def get_diagnostic_for_ticket(ticket):
    """
    Retorna o diagnóstico existente ou gera um novo.
    Regera automaticamente se o chamado foi atualizado depois do diagnóstico.
    """
    try:
        diagnostic = ticket.diagnostic
        # Regera se o chamado foi atualizado depois do diagnóstico
        if ticket.updated_at > diagnostic.generated_at:
            diagnostic = run_diagnostic(ticket)
        return diagnostic
    except DiagnosticAnalysis.DoesNotExist:
        return run_diagnostic(ticket)


def get_similar_tickets_details(diagnostic):
    """
    Busca os objetos Ticket completos para exibição na tela de diagnóstico.
    """
    from tickets.models import Ticket

    ids = diagnostic.get_similar_ids_list()
    if not ids:
        return []

    tickets = Ticket.objects.filter(pk__in=ids).select_related('created_by', 'assigned_to')

    # Mantém a ordem original (por score)
    ticket_map = {t.pk: t for t in tickets}
    return [ticket_map[i] for i in ids if i in ticket_map]
