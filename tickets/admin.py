from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket, TicketComment, TicketAttachment


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ['author', 'created_at']
    fields = ['author', 'content', 'is_internal', 'created_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'priority_badge', 'status_badge', 'category',
                    'created_by', 'assigned_to', 'created_at', 'is_overdue']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'description', 'created_by__username', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    inlines = [TicketCommentInline]
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

    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Atrasado'


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['content', 'author__username', 'ticket__title']
