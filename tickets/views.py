from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Ticket, TicketComment
from .forms import TicketForm, TicketAdminForm, TicketCommentForm, TicketFilterForm


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

    comments = ticket.comments.select_related('author').all()
    if not is_technician:
        comments = comments.filter(is_internal=False)

    comment_form = TicketCommentForm()
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
                messages.success(request, 'Comentário adicionado.')
                return redirect('tickets:detail', pk=pk)

        elif 'submit_admin' in request.POST and is_technician:
            admin_form = TicketAdminForm(request.POST, instance=ticket)
            if admin_form.is_valid():
                admin_form.save()
                messages.success(request, 'Chamado atualizado com sucesso.')
                return redirect('tickets:detail', pk=pk)

    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'admin_form': admin_form,
        'is_technician': is_technician,
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
        ticket.status = 'closed'
        ticket.save()
        messages.success(request, f'Chamado #{ticket.pk} encerrado.')
        return redirect('tickets:list')

    return render(request, 'tickets/confirm_close.html', {'ticket': ticket})
