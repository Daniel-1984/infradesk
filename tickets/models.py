from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


SLA_HOURS = {
    'critical': 4,
    'high': 8,
    'medium': 24,
    'low': 72,
}


class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    STATUS_CHOICES = [
        ('open', 'Aberto'),
        ('in_progress', 'Em Andamento'),
        ('waiting', 'Aguardando'),
        ('resolved', 'Resolvido'),
        ('closed', 'Fechado'),
    ]

    CATEGORY_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('network', 'Rede / Conectividade'),
        ('access', 'Acesso / Permissões'),
        ('peripheral', 'Periférico'),
        ('other', 'Outros'),
    ]

    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição')
    priority = models.CharField('Prioridade', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='open')
    category = models.CharField('Categoria', max_length=20, choices=CATEGORY_CHOICES, default='other')
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='tickets_created',
        verbose_name='Aberto por'
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tickets_assigned',
        verbose_name='Atribuído a'
    )
    asset = models.ForeignKey(
        'assets.Asset', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tickets',
        verbose_name='Equipamento'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    resolved_at = models.DateTimeField('Resolvido em', null=True, blank=True)
    due_date = models.DateField('Prazo', null=True, blank=True)
    sla_breached = models.BooleanField('SLA Violado', default=False)

    class Meta:
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} — {self.title}'

    def save(self, *args, **kwargs):
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'resolved':
            self.resolved_at = None

        # SLA auto-check: marca violação se passou do limite por prioridade
        if self.pk and self.created_at and self.status not in ('resolved', 'closed'):
            limit = self.created_at + timedelta(hours=SLA_HOURS.get(self.priority, 24))
            if timezone.now() > limit:
                self.sla_breached = True

        super().save(*args, **kwargs)

    def get_sla_deadline(self):
        """Retorna o datetime limite de SLA baseado na prioridade."""
        if self.created_at:
            return self.created_at + timedelta(hours=SLA_HOURS.get(self.priority, 24))
        return None

    def get_priority_badge(self):
        badges = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark',
        }
        return badges.get(self.priority, 'secondary')

    def get_status_badge(self):
        badges = {
            'open': 'primary',
            'in_progress': 'info',
            'waiting': 'warning',
            'resolved': 'success',
            'closed': 'secondary',
        }
        return badges.get(self.status, 'secondary')

    def is_overdue(self):
        if self.due_date and self.status not in ('resolved', 'closed'):
            return timezone.now().date() > self.due_date
        return False


class TicketComment(models.Model):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Chamado'
    )
    author = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='ticket_comments',
        verbose_name='Autor'
    )
    content = models.TextField('Conteúdo')
    is_internal = models.BooleanField(
        'Nota Interna', default=False,
        help_text='Visível apenas para técnicos e administradores'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['created_at']

    def __str__(self):
        return f'Comentário de {self.author.username} em #{self.ticket.pk}'


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Chamado'
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Enviado por')
    file = models.FileField('Arquivo', upload_to='tickets/attachments/%Y/%m/')
    filename = models.CharField('Nome do Arquivo', max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anexo'
        verbose_name_plural = 'Anexos'

    def __str__(self):
        return self.filename


class TicketHistory(models.Model):
    """Registro de todas as alterações feitas em um chamado."""

    FIELD_LABELS = {
        'status': 'Status',
        'priority': 'Prioridade',
        'assigned_to': 'Atribuído a',
        'asset': 'Equipamento',
        'due_date': 'Prazo',
        'comment_added': 'Comentário adicionado',
        'ticket_created': 'Chamado criado',
        'attachment_added': 'Anexo adicionado',
    }

    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Chamado'
    )
    changed_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name='Alterado por'
    )
    field_changed = models.CharField('Campo Alterado', max_length=50)
    old_value = models.CharField('Valor Anterior', max_length=500, blank=True)
    new_value = models.CharField('Novo Valor', max_length=500, blank=True)
    created_at = models.DateTimeField('Registrado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico'
        verbose_name_plural = 'Histórico de Alterações'
        ordering = ['created_at']

    def __str__(self):
        return f'#{self.ticket.pk} — {self.field_changed} por {self.changed_by.username}'

    def get_field_label(self):
        return self.FIELD_LABELS.get(self.field_changed, self.field_changed)


class Notification(models.Model):
    """Notificações internas para usuários sobre eventos nos chamados."""

    TYPE_CHOICES = [
        ('assigned', 'Chamado Atribuído'),
        ('comment', 'Novo Comentário'),
        ('status_change', 'Status Alterado'),
        ('sla_breach', 'SLA Violado'),
    ]

    TYPE_ICONS = {
        'assigned': 'bi-person-check',
        'comment': 'bi-chat-left-text',
        'status_change': 'bi-arrow-repeat',
        'sla_breach': 'bi-exclamation-triangle',
    }

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuário'
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Chamado'
    )
    type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES)
    message = models.CharField('Mensagem', max_length=300)
    is_read = models.BooleanField('Lida', default=False)
    created_at = models.DateTimeField('Criada em', auto_now_add=True)

    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.type}] {self.user.username}: {self.message[:50]}'

    def get_icon(self):
        return self.TYPE_ICONS.get(self.type, 'bi-bell')
