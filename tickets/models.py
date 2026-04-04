from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
        super().save(*args, **kwargs)

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
