"""
Funções de similaridade e processamento de texto.
Sem IA — apenas lógica determinística baseada em palavras-chave e interseção de termos.
"""

import re
from collections import Counter


# Palavras irrelevantes que não contribuem para similaridade
STOPWORDS = {
    'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
    'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
    'por', 'para', 'com', 'sem', 'sob', 'sobre', 'entre', 'ate', 'ate',
    'e', 'ou', 'mas', 'se', 'que', 'quando', 'como', 'porque', 'pois',
    'ao', 'aos', 'pelo', 'pela', 'pelos', 'pelas',
    'eu', 'tu', 'ele', 'ela', 'nos', 'eles', 'elas',
    'meu', 'minha', 'seu', 'sua', 'nosso', 'nossa',
    'este', 'esta', 'esse', 'essa', 'aquele', 'aquela',
    'foi', 'era', 'ser', 'estar', 'tem', 'ter', 'vai',
    'nao', 'sim', 'ja', 'so', 'mais', 'muito', 'pouco',
    'todo', 'toda', 'todos', 'todas', 'qualquer',
    'favor', 'obrigado', 'bom', 'boa', 'dia', 'tarde', 'noite',
}


def normalize_text(text):
    """
    Normaliza texto: minúsculas, remove acentos simplificados,
    remove pontuação, retorna lista de tokens limpos.
    """
    if not text:
        return []

    text = text.lower()

    # Troca acentos comuns por versão sem acento
    replacements = {
        'ã': 'a', 'â': 'a', 'á': 'a', 'à': 'a', 'ä': 'a',
        'ê': 'e', 'é': 'e', 'è': 'e', 'ë': 'e',
        'î': 'i', 'í': 'i', 'ì': 'i', 'ï': 'i',
        'õ': 'o', 'ô': 'o', 'ó': 'o', 'ò': 'o', 'ö': 'o',
        'ú': 'u', 'û': 'u', 'ù': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n',
    }
    for accented, plain in replacements.items():
        text = text.replace(accented, plain)

    # Remove tudo que não for letra, número ou espaço
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Tokeniza e filtra stopwords e tokens muito curtos
    tokens = [t for t in text.split() if t not in STOPWORDS and len(t) >= 3]

    return tokens


def compute_similarity(text_a, text_b):
    """
    Calcula similaridade entre dois textos usando Jaccard sobre tokens normalizados.
    Retorna float entre 0.0 e 1.0.

    Jaccard = |A ∩ B| / |A ∪ B|

    Exemplo:
      text_a = "sistema lento travando protheus"
      text_b = "protheus lento queda conexao"
      tokens_a = {sistema, lento, travando, protheus}
      tokens_b = {protheus, lento, queda, conexao}
      intersecao = {lento, protheus} → 2
      uniao = {sistema, lento, travando, protheus, queda, conexao} → 6
      jaccard = 2/6 = 0.333 → 33%
    """
    tokens_a = set(normalize_text(text_a))
    tokens_b = set(normalize_text(text_b))

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b

    return len(intersection) / len(union)


def compute_keyword_overlap(text, keywords_list):
    """
    Verifica quantas palavras-chave da lista aparecem no texto normalizado.
    Retorna (matched_count, total_count, percent).
    """
    if not text or not keywords_list:
        return 0, 0, 0.0

    tokens = set(normalize_text(text))
    normalized_keywords = [normalize_text(k)[0] if normalize_text(k) else k.lower() for k in keywords_list]
    normalized_keywords = [k for k in normalized_keywords if k]

    matched = sum(1 for kw in normalized_keywords if kw in tokens or any(kw in t for t in tokens))
    total = len(normalized_keywords)
    percent = (matched / total * 100) if total > 0 else 0.0

    return matched, total, percent


def extract_keywords(text, top_n=10):
    """
    Extrai as palavras mais relevantes de um texto por frequência.
    Útil para resumir o conteúdo de um chamado.
    """
    tokens = normalize_text(text)
    if not tokens:
        return []

    freq = Counter(tokens)
    return [word for word, _ in freq.most_common(top_n)]


def find_similar_tickets(target_ticket, candidates, min_score=0.15, max_results=5):
    """
    Compara um chamado alvo com uma lista de candidatos.
    Retorna lista de dicts ordenada por score decrescente:
      [{'ticket': obj, 'score': 0.45, 'percent': 45, 'matched_tokens': ['lento', 'protheus']}]

    Estratégia de pontuação:
    - Similaridade Jaccard entre título+descrição (peso 60%)
    - Mesma categoria (+10% bônus)
    - Mesmo ativo vinculado (+15% bônus)
    - Mesmo setor do criador (+10% bônus)
    - Mesmo domínio de categoria (+5% bônus)
    """
    target_text = f"{target_ticket.title} {target_ticket.description}"
    target_tokens = set(normalize_text(target_text))

    results = []

    for candidate in candidates:
        if candidate.pk == target_ticket.pk:
            continue

        candidate_text = f"{candidate.title} {candidate.description}"
        candidate_tokens = set(normalize_text(candidate_text))

        base_score = compute_similarity(target_text, candidate_text)

        # Bônus por mesma categoria
        bonus = 0.0
        if candidate.category == target_ticket.category:
            bonus += 0.10

        # Bônus por mesmo ativo
        if (target_ticket.asset_id and candidate.asset_id and
                target_ticket.asset_id == candidate.asset_id):
            bonus += 0.15

        # Bônus por mesmo setor do criador
        try:
            target_dept = target_ticket.created_by.profile.department_id
            cand_dept = candidate.created_by.profile.department_id
            if target_dept and cand_dept and target_dept == cand_dept:
                bonus += 0.10
        except Exception:
            pass

        final_score = min(base_score + bonus, 1.0)

        if final_score >= min_score:
            matched = target_tokens & candidate_tokens
            results.append({
                'ticket': candidate,
                'score': final_score,
                'percent': round(final_score * 100),
                'matched_tokens': list(matched)[:8],
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]


def classify_domain(title, description):
    """
    Classifica o domínio técnico de um chamado com base em palavras-chave.
    Retorna (domain_code, score_0_to_100).

    Lógica: cada domínio tem uma lista de palavras-chave com peso.
    O domínio com maior soma de pesos ganha.
    """
    DOMAIN_KEYWORDS = {
        'ERP_PROTHEUS': {
            'keywords': [
                'protheus', 'totvs', 'erp', 'datasul', 'sigafin', 'sigaest', 'sigacom',
                'sigamdi', 'sigafat', 'sigaatf', 'top connect', 'appserver', 'dbaccess',
                'smartclient', 'configurador', 'rpo', 'mnt', 'ctb', 'fis', 'pcp',
                'faturamento', 'estoque protheus', 'compras protheus', 'financeiro protheus',
                'nota fiscal', 'nfe', 'sped', 'reinf', 'esocial', 'balancete',
            ],
            'weight': 3,
        },
        'OFFICE_EXCEL': {
            'keywords': [
                'excel', 'planilha', 'xlsx', 'xls', 'macro', 'vba', 'formula',
                'pivot', 'grafico excel', 'tabela dinamica', 'celula', 'aba',
                'calculo', 'funcao excel', 'vlookup', 'procv', 'indice',
            ],
            'weight': 3,
        },
        'OFFICE_WORD': {
            'keywords': [
                'word', 'documento', 'docx', 'doc', 'formatacao', 'modelo word',
                'mala direta', 'sumario', 'cabecalho', 'rodape', 'word travou',
            ],
            'weight': 3,
        },
        'DATABASE': {
            'keywords': [
                'banco de dados', 'database', 'sql', 'oracle', 'mysql', 'postgres',
                'sqlserver', 'mssql', 'query', 'consulta', 'lentidao banco',
                'timeout', 'deadlock', 'lock', 'conexao banco', 'instancia',
                'tablespace', 'log banco', 'backup banco', 'restore', 'dump',
                'stored procedure', 'trigger', 'index', 'fragmentacao',
            ],
            'weight': 3,
        },
        'WEBSITE': {
            'keywords': [
                'site', 'portal', 'intranet', 'website', 'navegador', 'browser',
                'chrome', 'firefox', 'edge', 'pagina', 'url', 'http', 'https',
                'certificado', 'ssl', 'link', 'acesso site', 'login site',
                'formulario web', 'erro 404', 'erro 500', 'pagina nao carrega',
            ],
            'weight': 2,
        },
        'API': {
            'keywords': [
                'api', 'rest', 'webservice', 'soap', 'integracao', 'json', 'xml',
                'endpoint', 'requisicao', 'resposta api', 'token', 'autenticacao api',
                'webhook', 'payload', 'status code', 'timeout api',
            ],
            'weight': 3,
        },
        'NETWORK': {
            'keywords': [
                'rede', 'internet', 'wifi', 'cabeado', 'sem conexao', 'sem internet',
                'ping', 'lentidao rede', 'vpn', 'firewall', 'ip', 'dhcp', 'dns',
                'switch', 'roteador', 'cabo', 'queda rede', 'instabilidade',
                'conectividade', 'acesso remoto', 'rdp', 'teamviewer',
            ],
            'weight': 3,
        },
        'ACCESS': {
            'keywords': [
                'acesso', 'permissao', 'senha', 'login', 'usuario bloqueado',
                'conta bloqueada', 'active directory', 'ad', 'ldap', 'grupo',
                'perfil acesso', 'autorizacao', 'sem permissao', 'negar acesso',
                'redefinir senha', 'trocar senha', 'expirou', 'bloqueado',
            ],
            'weight': 3,
        },
        'HARDWARE': {
            'keywords': [
                'computador', 'notebook', 'desktop', 'tela', 'monitor', 'teclado',
                'mouse', 'nao liga', 'travando', 'reiniciando', 'lento demais',
                'hd', 'ssd', 'memoria ram', 'bateria', 'superaquecendo',
                'barulho hd', 'fonte', 'placa mae', 'processador',
            ],
            'weight': 2,
        },
        'PRINTER': {
            'keywords': [
                'impressora', 'imprimir', 'impressao', 'papel', 'toner', 'cartucho',
                'scanner', 'digitalizacao', 'fila impressao', 'driver impressora',
                'impressora offline', 'nao imprime',
            ],
            'weight': 3,
        },
        'EMAIL': {
            'keywords': [
                'email', 'e-mail', 'outlook', 'gmail', 'caixa entrada', 'envio email',
                'recebimento', 'spam', 'outlook travou', 'configurar email',
                'senha email', 'conta email', 'smtp', 'imap', 'pop3',
            ],
            'weight': 3,
        },
        'BACKUP': {
            'keywords': [
                'backup', 'restore', 'recuperacao', 'arquivo perdido', 'dados perdidos',
                'storage', 'nuvem', 'onedrive', 'sharepoint', 'google drive',
                'nas', 'san', 'backup falhou', 'restaurar arquivo',
            ],
            'weight': 3,
        },
    }

    combined_text = f"{title} {description}".lower()
    tokens = set(normalize_text(combined_text))
    full_text = combined_text

    scores = {}

    for domain, config in DOMAIN_KEYWORDS.items():
        domain_score = 0
        for keyword in config['keywords']:
            kw_normalized = keyword.lower()
            # Verifica presença no texto completo (para frases) e nos tokens
            if kw_normalized in full_text or any(kw_normalized in t for t in tokens):
                domain_score += config['weight']

        if domain_score > 0:
            scores[domain] = domain_score

    if not scores:
        return 'UNKNOWN', 0

    best_domain = max(scores, key=scores.get)
    best_score = scores[best_domain]

    # Normaliza para 0-100: considera 15 como score "máximo esperado" para 100%
    max_expected = 15
    confidence = min(round((best_score / max_expected) * 100), 95)

    return best_domain, confidence
