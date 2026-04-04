from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket
from assets.models import Asset, MaintenanceRecord


@login_required
def dashboard_index(request):
    is_technician = hasattr(request.user, 'profile') and request.user.profile.is_technician()

    # --- Métricas de chamados ---
    if is_technician:
        tickets_qs = Ticket.objects.all()
    else:
        tickets_qs = Ticket.objects.filter(created_by=request.user)

    tickets_open = tickets_qs.filter(status='open').count()
    tickets_in_progress = tickets_qs.filter(status='in_progress').count()
    tickets_resolved = tickets_qs.filter(status='resolved').count()
    tickets_critical = tickets_qs.filter(priority='critical', status__in=['open', 'in_progress']).count()

    # Últimos 7 dias
    week_ago = timezone.now() - timedelta(days=7)
    tickets_this_week = tickets_qs.filter(created_at__gte=week_ago).count()

    # Chamados recentes
    recent_tickets = tickets_qs.select_related('created_by', 'assigned_to').order_by('-created_at')[:8]

    # Chamados por status (para gráfico)
    tickets_by_status = {
        'open': tickets_qs.filter(status='open').count(),
        'in_progress': tickets_qs.filter(status='in_progress').count(),
        'waiting': tickets_qs.filter(status='waiting').count(),
        'resolved': tickets_qs.filter(status='resolved').count(),
        'closed': tickets_qs.filter(status='closed').count(),
    }

    # Chamados por prioridade
    tickets_by_priority = {
        'low': tickets_qs.filter(priority='low').count(),
        'medium': tickets_qs.filter(priority='medium').count(),
        'high': tickets_qs.filter(priority='high').count(),
        'critical': tickets_qs.filter(priority='critical').count(),
    }

    # --- Métricas de ativos (apenas para técnicos) ---
    assets_total = 0
    assets_active = 0
    assets_maintenance = 0
    assets_inactive = 0
    recent_maintenance = []
    expiring_warranties = []

    if is_technician:
        assets_total = Asset.objects.count()
        assets_active = Asset.objects.filter(status='active').count()
        assets_maintenance = Asset.objects.filter(status='maintenance').count()
        assets_inactive = Asset.objects.filter(status='inactive').count()

        recent_maintenance = MaintenanceRecord.objects.select_related('asset', 'technician').order_by('-created_at')[:5]

        thirty_days = timezone.now().date() + timedelta(days=30)
        expiring_warranties = Asset.objects.filter(
            warranty_until__lte=thirty_days,
            warranty_until__gte=timezone.now().date(),
            status__in=['active', 'available']
        ).order_by('warranty_until')[:5]

        # Top técnicos
        top_technicians = User.objects.filter(
            tickets_assigned__status='resolved'
        ).annotate(
            resolved_count=Count('tickets_assigned', filter=Q(tickets_assigned__status='resolved'))
        ).order_by('-resolved_count')[:5]
    else:
        top_technicians = []

    context = {
        'is_technician': is_technician,
        # Tickets
        'tickets_open': tickets_open,
        'tickets_in_progress': tickets_in_progress,
        'tickets_resolved': tickets_resolved,
        'tickets_critical': tickets_critical,
        'tickets_this_week': tickets_this_week,
        'recent_tickets': recent_tickets,
        'tickets_by_status': tickets_by_status,
        'tickets_by_priority': tickets_by_priority,
        # Assets
        'assets_total': assets_total,
        'assets_active': assets_active,
        'assets_maintenance': assets_maintenance,
        'assets_inactive': assets_inactive,
        'recent_maintenance': recent_maintenance,
        'expiring_warranties': expiring_warranties,
        'top_technicians': top_technicians,
    }
    return render(request, 'dashboard/index.html', context)
