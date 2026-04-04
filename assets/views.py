from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Asset, MaintenanceRecord
from .forms import AssetForm, MaintenanceForm, AssetFilterForm


def technician_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not (hasattr(request.user, 'profile') and request.user.profile.is_technician()):
            messages.error(request, 'Acesso restrito a técnicos e administradores.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return login_required(wrapper)


@login_required
def asset_list(request):
    assets = Asset.objects.select_related('assigned_to').all()

    filter_form = AssetFilterForm(request.GET)
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data.get('status'):
            assets = assets.filter(status=data['status'])
        if data.get('asset_type'):
            assets = assets.filter(asset_type=data['asset_type'])
        if data.get('search'):
            assets = assets.filter(
                Q(name__icontains=data['search']) |
                Q(serial_number__icontains=data['search']) |
                Q(asset_tag__icontains=data['search']) |
                Q(brand__icontains=data['search']) |
                Q(model_name__icontains=data['search'])
            )

    paginator = Paginator(assets, 12)
    page = request.GET.get('page')
    assets_page = paginator.get_page(page)

    context = {
        'assets': assets_page,
        'filter_form': filter_form,
        'total_count': assets.count(),
    }
    return render(request, 'assets/list.html', context)


@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset.objects.select_related('assigned_to'), pk=pk)
    maintenance_records = asset.maintenance_records.select_related('technician').all()
    open_tickets = asset.tickets.filter(status__in=['open', 'in_progress', 'waiting'])

    maintenance_form = None
    is_technician = hasattr(request.user, 'profile') and request.user.profile.is_technician()

    if is_technician:
        maintenance_form = MaintenanceForm()
        if request.method == 'POST':
            maintenance_form = MaintenanceForm(request.POST)
            if maintenance_form.is_valid():
                record = maintenance_form.save(commit=False)
                record.asset = asset
                record.save()
                if record.status == 'in_progress':
                    asset.status = 'maintenance'
                    asset.save()
                messages.success(request, 'Registro de manutenção adicionado.')
                return redirect('assets:detail', pk=pk)

    context = {
        'asset': asset,
        'maintenance_records': maintenance_records,
        'open_tickets': open_tickets,
        'maintenance_form': maintenance_form,
        'is_technician': is_technician,
    }
    return render(request, 'assets/detail.html', context)


@technician_required
def asset_create(request):
    form = AssetForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            asset = form.save()
            messages.success(request, f'Ativo "{asset.name}" cadastrado com sucesso!')
            return redirect('assets:detail', pk=asset.pk)

    return render(request, 'assets/create.html', {'form': form, 'action': 'Cadastrar'})


@technician_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    form = AssetForm(request.POST or None, instance=asset)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Ativo "{asset.name}" atualizado.')
            return redirect('assets:detail', pk=asset.pk)

    return render(request, 'assets/create.html', {'form': form, 'asset': asset, 'action': 'Editar'})
