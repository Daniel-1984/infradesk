from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket, TicketComment, TicketAttachment, TicketHistory, Notification


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ['author', 'created_at']
    fields = ['author', 'content', 'is_internal', 'created_at']


class TicketHistoryInline(admin.TabularInline):
    model = TicketHistory
    extra = 0
    readonly_fields = ['changed_by', 'field_changed', 'old_value', 'new_value', 'created_at']
    fields = ['changed_by', 'field_changed', 'old_value', 'new_value', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'priority_badge', 'status_badge', 'category',
                    'created_by', 'assigned_to', 'sla_badge', 'created_at', 'is_overdue']
    list_filter = ['status', 'priority', 'category', 'sla_breached', 'created_at']
    search_fields = ['title', 'description', 'created_by__username', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    inlines = [TicketCommentInline, TicketHistoryInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações do Chamado', {
            'fields': ('title', 'description', 'category')
        }),
        ('Classificação', {
            'fields': ('priority', 'status', 'due_date', 'sla_breached')
        }),
        ('Responsáveis', {
            'fields': ('created_by', 'assigned_to', 'asset')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )

    def priority_badge(self, obj):
        colors = {
            'low': '#198754', 'medium': '#ffc107',
            'high': '#dc3545', 'critical': '#212529'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioridade'

    def status_badge(self, obj):
        colors = {
            'open': '#0d6efd', 'in_progress': '#0dcaf0',
            'waiting': '#ffc107', 'resolved': '#198754', 'closed': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def sla_badge(self, obj):
        if obj.sla_breached:
            return format_html('<span style="color:#dc3545;font-weight:700">&#10007; Violado</span>')
        return format_html('<span style="color:#198754">&#10003; OK</span>')
    sla_badge.short_description = 'SLA'

    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Atrasado'


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['content', 'author__username', 'ticket__title']


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'ticket', 'uploaded_by', 'uploaded_at']
    search_fields = ['filename', 'ticket__title']
    readonly_fields = ['uploaded_at']


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'field_changed', 'old_value', 'new_value', 'changed_by', 'created_at']
    list_filter = ['field_changed', 'created_at']
    search_fields = ['ticket__title', 'changed_by__username']
    readonly_fields = ['ticket', 'changed_by', 'field_changed', 'old_value', 'new_value', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'ticket', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['created_at']
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} notificação(ões) marcada(s) como lida(s).')
    mark_as_read.short_description = 'Marcar como lidas'
