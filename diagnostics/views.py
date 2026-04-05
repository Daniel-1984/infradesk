from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from tickets.models import Ticket
from .services import run_diagnostic, get_diagnostic_for_ticket, get_similar_tickets_details
from .models import RecurrenceAlert


def _is_technician(user):
    return hasattr(user, 'profile') and user.profile.is_technician()


@login_required
def diagnostic_panel(request, ticket_pk):
    """
    Painel de diagnóstico completo para um chamado.
    Acessível apenas por técnicos.
    """
    if not _is_technician(request.user):
        messages.error(request, 'Acesso restrito a técnicos.')
        return redirect('tickets:detail', pk=ticket_pk)

    ticket = get_object_or_404(Ticket, pk=ticket_pk)
    diagnostic = get_diagnostic_for_ticket(ticket)
    similar_tickets = get_similar_tickets_details(diagnostic)

    checklist_items = []
    if diagnostic.playbook_matched:
        checklist_items = diagnostic.playbook_matched.get_checklist_items()

    context = {
        'ticket': ticket,
        'diagnostic': diagnostic,
        'similar_tickets': similar_tickets,
        'checklist_items': checklist_items,
        'is_technician': True,
    }
    return render(request, 'diagnostics/panel.html', context)


@login_required
def regenerate_diagnostic(request, ticket_pk):
    """
    Força a regeneração do diagnóstico para um chamado.
    POST only.
    """
    if not _is_technician(request.user):
        messages.error(request, 'Acesso restrito a técnicos.')
        return redirect('tickets:detail', pk=ticket_pk)

    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, pk=ticket_pk)
        run_diagnostic(ticket)
        messages.success(request, 'Diagnóstico atualizado com sucesso.')

    return redirect('diagnostics:panel', ticket_pk=ticket_pk)


@login_required
def recurrence_alerts(request):
    """
    Lista os alertas de reincidência ativos para técnicos.
    """
    if not _is_technician(request.user):
        messages.error(request, 'Acesso restrito a técnicos.')
        return redirect('dashboard:index')

    alerts = RecurrenceAlert.objects.filter(is_resolved=False).order_by('-created_at')[:50]

    context = {
        'alerts': alerts,
        'is_technician': True,
    }
    return render(request, 'diagnostics/alerts.html', context)
