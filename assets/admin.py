from django.contrib import admin
from django.utils.html import format_html
from .models import Asset, MaintenanceRecord, AssetCategory


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']


class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    readonly_fields = ['created_at']
    fields = ['maintenance_type', 'status', 'description', 'technician', 'scheduled_date', 'completed_date', 'cost']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_tag', 'name', 'asset_type', 'brand', 'model_name',
        'status_badge', 'condition', 'assigned_to', 'location', 'warranty_status'
    ]
    list_filter = ['status', 'asset_type', 'condition', 'brand']
    search_fields = ['name', 'serial_number', 'asset_tag', 'brand', 'model_name', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MaintenanceRecordInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('name', 'asset_type', 'brand', 'model_name', 'serial_number', 'asset_tag')
        }),
        ('Status e Localização', {
            'fields': ('status', 'condition', 'location', 'assigned_to')
        }),
        ('Especificações Técnicas', {
            'fields': ('operating_system', 'processor', 'ram', 'storage', 'ip_address', 'mac_address'),
            'classes': ('collapse',)
        }),
        ('Informações de Compra', {
            'fields': ('purchase_date', 'warranty_until', 'purchase_value', 'supplier'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'active': '#198754', 'available': '#0d6efd',
            'maintenance': '#ffc107', 'inactive': '#6c757d', 'disposed': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def warranty_status(self, obj):
        valid = obj.is_warranty_valid()
        if valid is None:
            return '—'
        if valid:
            if obj.is_warranty_expiring_soon():
                return format_html('<span style="color:#ffc107">⚠ Expira em breve</span>')
            return format_html('<span style="color:#198754">✓ Válida</span>')
        return format_html('<span style="color:#dc3545">✗ Expirada</span>')
    warranty_status.short_description = 'Garantia'


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ['asset', 'maintenance_type', 'status', 'technician', 'scheduled_date', 'completed_date', 'cost']
    list_filter = ['status', 'maintenance_type']
    search_fields = ['asset__name', 'description', 'technician__username']
