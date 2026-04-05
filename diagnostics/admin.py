from django.contrib import admin
from django.utils.html import format_html
from .models import PlaybookEntry, DiagnosticAnalysis, RecurrenceAlert


@admin.register(PlaybookEntry)
class PlaybookEntryAdmin(admin.ModelAdmin):
    list_display = ['domain', 'title', 'priority_hint', 'is_active', 'updated_at']
    list_filter = ['domain', 'priority_hint', 'is_active']
    search_fields = ['title', 'keywords', 'probable_cause']
    list_editable = ['is_active']
    ordering = ['domain', 'title']

    fieldsets = (
        ('Identificação', {
            'fields': ('domain', 'title', 'keywords', 'priority_hint', 'is_active')
        }),
        ('Diagnóstico', {
            'fields': ('probable_cause', 'checklist', 'recommended_action')
        }),
    )


@admin.register(DiagnosticAnalysis)
class DiagnosticAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'domain_detected', 'confidence_badge',
        'similar_tickets_count', 'recurrence_level', 'generated_at'
    ]
    list_filter = ['domain_detected', 'confidence', 'recurrence_level']
    search_fields = ['ticket__title', 'ticket__pk']
    readonly_fields = [
        'ticket', 'domain_detected', 'domain_confidence_score',
        'similar_tickets_count', 'similar_tickets_ids',
        'recurrence_level', 'recurrence_count_7d', 'recurrence_count_15d', 'recurrence_count_30d',
        'playbook_matched', 'confidence', 'confidence_percent', 'generated_at', 'notes'
    ]

    def confidence_badge(self, obj):
        colors = {'high': '#198754', 'medium': '#ffc107', 'low': '#6c757d'}
        color = colors.get(obj.confidence, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">'
            '{}%</span>',
            color, obj.confidence_percent
        )
    confidence_badge.short_description = 'Confiança'


@admin.register(RecurrenceAlert)
class RecurrenceAlertAdmin(admin.ModelAdmin):
    list_display = ['scope_value', 'scope', 'level', 'occurrences', 'period_days', 'is_resolved', 'created_at']
    list_filter = ['scope', 'level', 'is_resolved']
    list_editable = ['is_resolved']
    ordering = ['-created_at']
