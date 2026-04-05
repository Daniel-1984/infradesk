from django.db import models
from django.contrib.auth.models import User


DOMAIN_CHOICES = [
    ('ERP_PROTHEUS', 'ERP Protheus'),
    ('OFFICE_EXCEL', 'Excel / Office'),
    ('OFFICE_WORD', 'Word / Office'),
    ('DATABASE', 'Banco de Dados'),
    ('WEBSITE', 'Website / Intranet'),
    ('API', 'API / Integração'),
    ('NETWORK', 'Rede / Conectividade'),
    ('ACCESS', 'Acesso / Permissões'),
    ('HARDWARE', 'Hardware'),
    ('PRINTER', 'Impressora / Periférico'),
    ('EMAIL', 'E-mail'),
    ('BACKUP', 'Backup / Storage'),
    ('UNKNOWN', 'Não Identificado'),
]

CONFIDENCE_CHOICES = [
    ('low', 'Baixa'),
    ('medium', 'Média'),
    ('high', 'Alta'),
]

RECURRENCE_LEVEL_CHOICES = [
    ('light', 'Leve'),
    ('medium', 'Moderado'),
    ('critical', 'Crítico'),
]


class PlaybookEntry(models.Model):
    """
    Base de conhecimento técnico por domínio e sintoma.
    Cada entrada representa um padrão de problema com diagnóstico pré-definido.
    """
    domain = models.CharField('Domínio', max_length=30, choices=DOMAIN_CHOICES)
    title = models.CharField('Título do Sintoma', max_length=200)
    keywords = models.TextField(
        'Palavras-chave',
        help_text='Separe por vírgula. Ex: lento,travando,timeout,queda'
    )
    probable_cause = models.TextField('Causa Provável')
    checklist = models.TextField(
        'Checklist Técnico',
        help_text='Uma ação por linha'
    )
    recommended_action = models.TextField('Ação Recomendada')
    priority_hint = models.CharField(
        'Sugestão de Prioridade', max_length=20,
        choices=[('low','Baixa'),('medium','Média'),('high','Alta'),('critical','Crítica')],
        default='medium'
    )
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Entrada do Playbook'
        verbose_name_plural = 'Playbook — Base de Conhecimento'
        ordering = ['domain', 'title']

    def __str__(self):
        return f'[{self.domain}] {self.title}'

    def get_keywords_list(self):
        return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]

    def get_checklist_items(self):
        return [item.strip() for item in self.checklist.splitlines() if item.strip()]


class DiagnosticAnalysis(models.Model):
    """
    Resultado do diagnóstico gerado para um chamado específico.
    Armazena o snapshot da análise no momento em que foi gerada.
    """
    ticket = models.OneToOneField(
        'tickets.Ticket', on_delete=models.CASCADE,
        related_name='diagnostic',
        verbose_name='Chamado'
    )
    domain_detected = models.CharField('Domínio Detectado', max_length=30, choices=DOMAIN_CHOICES, default='UNKNOWN')
    domain_confidence_score = models.IntegerField('Score de Domínio (0-100)', default=0)
    similar_tickets_count = models.IntegerField('Chamados Similares Encontrados', default=0)
    similar_tickets_ids = models.TextField('IDs dos Similares', blank=True, default='')
    recurrence_level = models.CharField(
        'Nível de Reincidência', max_length=20,
        choices=RECURRENCE_LEVEL_CHOICES, null=True, blank=True
    )
    recurrence_count_7d = models.IntegerField('Ocorrências (7 dias)', default=0)
    recurrence_count_15d = models.IntegerField('Ocorrências (15 dias)', default=0)
    recurrence_count_30d = models.IntegerField('Ocorrências (30 dias)', default=0)
    playbook_matched = models.ForeignKey(
        PlaybookEntry, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Playbook Aplicado'
    )
    confidence = models.CharField('Confiança Geral', max_length=10, choices=CONFIDENCE_CHOICES, default='low')
    confidence_percent = models.IntegerField('Confiança (%)', default=0)
    generated_at = models.DateTimeField('Gerado em', auto_now=True)
    notes = models.TextField('Observações do Motor', blank=True)

    class Meta:
        verbose_name = 'Diagnóstico'
        verbose_name_plural = 'Diagnósticos Gerados'

    def __str__(self):
        return f'Diagnóstico #{self.ticket.pk} — {self.domain_detected} ({self.confidence_percent}%)'

    def get_similar_ids_list(self):
        if not self.similar_tickets_ids:
            return []
        return [int(x) for x in self.similar_tickets_ids.split(',') if x.strip().isdigit()]

    def get_recurrence_badge_color(self):
        colors = {'light': 'warning', 'medium': 'orange', 'critical': 'danger'}
        return colors.get(self.recurrence_level, 'secondary')


class RecurrenceAlert(models.Model):
    """
    Alerta gerado quando um padrão de reincidência é detectado.
    Separado do diagnóstico para facilitar consulta rápida no dashboard.
    """
    SCOPE_CHOICES = [
        ('asset', 'Ativo / Equipamento'),
        ('department', 'Setor / Departamento'),
        ('category', 'Categoria'),
        ('domain', 'Domínio Técnico'),
    ]

    scope = models.CharField('Escopo', max_length=20, choices=SCOPE_CHOICES)
    scope_value = models.CharField('Valor do Escopo', max_length=200)
    domain = models.CharField('Domínio', max_length=30, choices=DOMAIN_CHOICES, blank=True)
    level = models.CharField('Nível', max_length=20, choices=RECURRENCE_LEVEL_CHOICES)
    occurrences = models.IntegerField('Ocorrências')
    period_days = models.IntegerField('Período (dias)')
    first_seen = models.DateTimeField('Primeiro Chamado')
    last_seen = models.DateTimeField('Último Chamado')
    is_resolved = models.BooleanField('Resolvido', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Alerta de Reincidência'
        verbose_name_plural = 'Alertas de Reincidência'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.level.upper()}] {self.scope_value} — {self.occurrences}x em {self.period_days}d'
