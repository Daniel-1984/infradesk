from django import forms
from .models import Asset, MaintenanceRecord


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'asset_type', 'brand', 'model_name', 'serial_number',
            'asset_tag', 'status', 'condition', 'location', 'assigned_to',
            'purchase_date', 'warranty_until', 'purchase_value', 'supplier',
            'ip_address', 'mac_address', 'operating_system',
            'processor', 'ram', 'storage', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_tag': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sala 301, Andar 3'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.100'}),
            'mac_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AA:BB:CC:DD:EE:FF'}),
            'operating_system': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Windows 11 Pro'}),
            'processor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Intel Core i7-12700'}),
            'ram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '16 GB DDR4'}),
            'storage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '512 GB SSD NVMe'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Nome / Identificação',
            'asset_type': 'Tipo de Equipamento',
            'brand': 'Marca',
            'model_name': 'Modelo',
            'serial_number': 'Número de Série',
            'asset_tag': 'Nº de Patrimônio',
            'status': 'Status',
            'condition': 'Estado',
            'location': 'Localização',
            'assigned_to': 'Responsável',
            'purchase_date': 'Data de Compra',
            'warranty_until': 'Garantia até',
            'purchase_value': 'Valor de Compra (R$)',
            'supplier': 'Fornecedor',
            'ip_address': 'Endereço IP',
            'mac_address': 'Endereço MAC',
            'operating_system': 'Sistema Operacional',
            'processor': 'Processador',
            'ram': 'Memória RAM',
            'storage': 'Armazenamento',
            'notes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].empty_label = '— Sem responsável —'
        self.fields['assigned_to'].required = False


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['maintenance_type', 'status', 'description', 'technician',
                  'scheduled_date', 'completed_date', 'cost', 'notes']
        widgets = {
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'technician': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'maintenance_type': 'Tipo',
            'status': 'Status',
            'description': 'Descrição',
            'technician': 'Técnico',
            'scheduled_date': 'Data Agendada',
            'completed_date': 'Data de Conclusão',
            'cost': 'Custo (R$)',
            'notes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        self.fields['technician'].queryset = User.objects.filter(
            profile__role__in=['admin', 'technician']
        ).order_by('first_name')
        self.fields['technician'].empty_label = '— Selecione o técnico —'
        self.fields['technician'].required = False


class AssetFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'Todos os Status')] + Asset.STATUS_CHOICES
    TYPE_CHOICES = [('', 'Todos os Tipos')] + Asset.TYPE_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    asset_type = forms.ChoiceField(
        choices=TYPE_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Buscar por nome, série, patrimônio...'
        })
    )
