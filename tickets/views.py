import csv
from itertools import chain as iterchain

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse

from .models import Ticket, TicketComment, TicketAttachment, TicketHistory, Notification
from .forms import TicketForm, TicketAdminForm, TicketCommentForm, TicketFilterForm, TicketAttachmentForm
from diagnostics.services import get_diagnostic_for_ticket


def _log_history(ticket, user, field, old_val, new_val):
    TicketHistory.objects.create(
        ticket=ticket,
        changed_by=user,
        field_changed=field,
        old_value=str(old_val) if old_val else '',
        new_value=str(new_val) if new_val else '',
    )


def _notify(user, ticket, ntype, message):
    Notification.objects.create(user=user, ticket=ticket, type=ntype, message=message)


@login_required
def ticket_list(request):
    is_technician = hasattr(request.user, 'profile') and request.user.profile.is_technician()

    if is_technician:
        tickets = Ticket.objects.select_related('created_by', 'assigned_to', 'asset').all()
    else:
        tickets = Ticket.objects.select_related('created_by', 'assigned_to', 'asset').filter(
            created_by=request.user
        )

    filter_form = TicketFilterForm(request.GET)
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data.get('status'):
            tickets = tickets.filter(status=data['status'])
        if data.get('priority'):
            tickets = tickets.filter(priority=data['priority'])
        if data.get('category'):
            tickets = tickets.filter(category=data['category'])
        if data.get('search'):
            tickets = tickets.filter(
                Q(title__icontains=data['search']) |
                Q(description__icontains=data['search']) |
                Q(pk__icontains=data['search'])
            )

    paginator = Paginator(tickets, 15)
    page = request.GET.get('page')
    tickets_page = paginator.get_page(page)

    context = {
        'tickets': tickets_page,
        'filter_form': filter_form,
        'is_technician': is_technician,
        'total_count': tickets.count(),
    }
    return render(request, 'tickets/list.html', context)


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    is_technician = hasattr(request.user, 'profile') and request.user.profile.is_technician()

    if not is_technician and ticket.created_by != request.user:
        messages.error(request, 'Você não tem permissão para visualizar este chamado.')
        return redirect('tickets:list')

    comment_form = TicketCommentForm()
    attachment_form = TicketAttachmentForm()
    admin_form = None
    if is_technician:
        admin_form = TicketAdminForm(instance=ticket)

    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            comment_form = TicketCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                if not is_technician:
                    comment.is_internal = False
                comment.save()

                # Audit log
                prefix = '[Interno] ' if comment.is_internal else ''
                _log_history(ticket, request.user, 'comment_added', '', f'{prefix}{comment.content[:120]}')

                # Notificar solicitante e atribuído
                if ticket.created_by != request.user and not comment.is_internal:
                    _notify(ticket.created_by, ticket, 'comment',
                            f'Novo comentário no chamado #{ticket.pk}: {comment.content[:80]}')
                if ticket.assigned_to and ticket.assigned_to != request.user:
                    _notify(ticket.assigned_to, ticket, 'comment',
                            f'Novo comentário no chamado #{ticket.pk}: {comment.content[:80]}')

                messages.success(request, 'Comentário adicionado.')
                return redirect('tickets:detail', pk=pk)

        elif 'submit_attachment' in request.POST:
            attachment_form = TicketAttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                att = attachment_form.save(commit=False)
                att.ticket = ticket
                att.uploaded_by = request.user
                att.filename = request.FILES['file'].name
                att.save()
                _log_history(ticket, request.user, 'attachment_added', '', att.filename)
                messages.success(request, f'Arquivo "{att.filename}" anexado.')
                return redirect('tickets:detail', pk=pk)

        elif 'submit_admin' in request.POST and is_technician:
            # Captura valores antigos para audit log
            old_status = ticket.status
            old_priority = ticket.priority
            old_assigned_id = ticket.assigned_to_id

            admin_form = TicketAdminForm(request.POST, instance=ticket)
            if admin_form.is_valid():
                updated = admin_form.save()

                status_map = dict(Ticket.STATUS_CHOICES)
                priority_map = dict(Ticket.PRIORITY_CHOICES)

                if old_status != updated.status:
                    _log_history(ticket, request.user, 'status',
                                 status_map.get(old_status, old_status),
                                 status_map.get(updated.status, updated.status))
                    # Notificar solicitante se status mudou
                    if updated.created_by != request.user:
                        _notify(updated.created_by, updated, 'status_change',
                                f'Status do chamado #{updated.pk} alterado para: {status_map.get(updated.status, updated.status)}')

                if old_priority != updated.priority:
                    _log_history(ticket, request.user, 'priority',
                                 priority_map.get(old_priority, old_priority),
                                 priority_map.get(updated.priority, updated.priority))

                if old_assigned_id != updated.assigned_to_id:
                    old_user = User.objects.filter(pk=old_assigned_id).first()
                    old_name = old_user.get_full_name() if old_user else '—'
                    new_name = updated.assigned_to.get_full_name() if updated.assigned_to else '—'
                    _log_history(ticket, request.user, 'assigned_to', old_name, new_name)

                    if updated.assigned_to and updated.assigned_to != request.user:
                        _notify(updated.assigned_to, updated, 'assigned',
                                f'Chamado #{updated.pk} foi atribuído a você: {updated.title[:60]}')

                messages.success(request, 'Chamado atualizado com sucesso.')
                return redirect('tickets:detail', pk=pk)

    # Timeline unificada: comentários + histórico em ordem cronológica
    comments_qs = ticket.comments.select_related('author').all()
    if not is_technician:
        comments_qs = comments_qs.filter(is_internal=False)

    history_qs = ticket.history.select_related('changed_by').all()

    timeline = sorted(
        [{'type': 'comment', 'obj': c, 'date': c.created_at} for c in comments_qs] +
        [{'type': 'history', 'obj': h, 'date': h.created_at} for h in history_qs],
        key=lambda x: x['date']
    )

    attachments = ticket.attachments.select_related('uploaded_by').order_by('uploaded_at')

    # Diagnóstico (apenas para técnicos)
    diagnostic = None
    if is_technician:
        try:
            diagnostic = get_diagnostic_for_ticket(ticket)
        except Exception:
            diagnostic = None

    context = {
        'ticket': ticket,
        'timeline': timeline,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'attachments': attachments,
        'admin_form': admin_form,
        'is_technician': is_technician,
        'diagnostic': diagnostic,
    }
    return render(request, 'tickets/detail.html', context)


@login_required
def ticket_create(request):
    form = TicketForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            _log_history(ticket, request.user, 'ticket_created', '', f'Chamado #{ticket.pk} criado')
            messages.success(request, f'Chamado #{ticket.pk} aberto com sucesso!')
            return redirect('tickets:detail', pk=ticket.pk)

    return render(request, 'tickets/create.html', {'form': form})


@login_required
def ticket_close(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    is_technician = hasattr(request.user, 'profile') and request.user.profile.is_technician()

    if not is_technician and ticket.created_by != request.user:
        messages.error(request, 'Ação não permitida.')
        return redirect('tickets:list')

    if request.method == 'POST':
        old_status = ticket.status
        ticket.status = 'closed'
        ticket.save()
        _log_history(ticket, request.user, 'status',
                     dict(Ticket.STATUS_CHOICES).get(old_status, old_status), 'Fechado')
        messages.success(request, f'Chamado #{ticket.pk} encerrado.')
        return redirect('tickets:list')

    return render(request, 'tickets/confirm_close.html', {'ticket': ticket})


@login_required
def ticket_export_csv(request):
    is_technician = hasattr(request.user, 'profile') and request.user.profile.is_technician()

    if is_technician:
        tickets = Ticket.objects.select_related('created_by', 'assigned_to', 'asset').all()
    else:
        tickets = Ticket.objects.select_related('created_by', 'assigned_to', 'asset').filter(
            created_by=request.user
        )

    filter_form = TicketFilterForm(request.GET)
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data.get('status'):
            tickets = tickets.filter(status=data['status'])
        if data.get('priority'):
            tickets = tickets.filter(priority=data['priority'])
        if data.get('category'):
            tickets = tickets.filter(category=data['category'])
        if data.get('search'):
            tickets = tickets.filter(
                Q(title__icontains=data['search']) |
                Q(description__icontains=data['search']) |
                Q(pk__icontains=data['search'])
            )

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="chamados.csv"'
    response.write('\ufeff')  # BOM para Excel reconhecer UTF-8

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        '#', 'Título', 'Categoria', 'Prioridade', 'Status',
        'Solicitante', 'Atribuído a', 'Equipamento',
        'Prazo', 'SLA Violado', 'Criado em', 'Resolvido em'
    ])

    for t in tickets:
        writer.writerow([
            t.pk,
            t.title,
            t.get_category_display(),
            t.get_priority_display(),
            t.get_status_display(),
            t.created_by.get_full_name() or t.created_by.username,
            t.assigned_to.get_full_name() if t.assigned_to else '',
            t.asset.name if t.asset else '',
            t.due_date.strftime('%d/%m/%Y') if t.due_date else '',
            'Sim' if t.sla_breached else 'Não',
            t.created_at.strftime('%d/%m/%Y %H:%M'),
            t.resolved_at.strftime('%d/%m/%Y %H:%M') if t.resolved_at else '',
        ])

    return response


@login_required
def ticket_notifications(request):
    notifs = request.user.notifications.select_related('ticket').order_by('-created_at')[:50]
    notifs_list = list(notifs)
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'tickets/notifications.html', {'notifications': notifs_list})
