from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AssetCategory(models.Model):
    name = models.CharField('Nome', max_length=100)
    icon = models.CharField('Ícone Bootstrap', max_length=50, default='bi-device-hdd')

    class Meta:
        verbose_name = 'Categoria de Ativo'
        verbose_name_plural = 'Categorias de Ativos'
        ordering = ['name']

    def __str__(self):
        return self.name


class Asset(models.Model):
    TYPE_CHOICES = [
        ('laptop', 'Notebook'),
        ('desktop', 'Desktop'),
        ('server', 'Servidor'),
        ('printer', 'Impressora'),
        ('network', 'Equipamento de Rede'),
        ('monitor', 'Monitor'),
        ('phone', 'Telefone / VOIP'),
        ('mobile', 'Smartphone / Tablet'),
        ('other', 'Outro'),
    ]

    STATUS_CHOICES = [
        ('active', 'Em Uso'),
        ('available', 'Disponível'),
        ('maintenance', 'Em Manutenção'),
        ('inactive', 'Inativo'),
        ('disposed', 'Descartado'),
    ]

    CONDITION_CHOICES = [
        ('new', 'Novo'),
        ('good', 'Bom'),
        ('fair', 'Regular'),
        ('poor', 'Ruim'),
    ]

    name = models.CharField('Nome / Identificação', max_length=200)
    asset_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES)
    brand = models.CharField('Marca', max_length=100)
    model_name = models.CharField('Modelo', max_length=200)
    serial_number = models.CharField('Número de Série', max_length=100, unique=True)
    asset_tag = models.CharField('Patrimônio', max_length=50, unique=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='available')
    condition = models.CharField('Estado', max_length=20, choices=CONDITION_CHOICES, default='good')
    location = models.CharField('Localização', max_length=200, blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assets_assigned',
        verbose_name='Responsável'
    )
    purchase_date = models.DateField('Data de Compra', null=True, blank=True)
    warranty_until = models.DateField('Garantia até', null=True, blank=True)
    purchase_value = models.DecimalField('Valor de Compra (R$)', max_digits=12, decimal_places=2, null=True, blank=True)
    supplier = models.CharField('Fornecedor', max_length=200, blank=True)
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    mac_address = models.CharField('Endereço MAC', max_length=17, blank=True)
    operating_system = models.CharField('Sistema Operacional', max_length=100, blank=True)
    processor = models.CharField('Processador', max_length=200, blank=True)
    ram = models.CharField('Memória RAM', max_length=50, blank=True)
    storage = models.CharField('Armazenamento', max_length=100, blank=True)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Cadastrado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Ativo de TI'
        verbose_name_plural = 'Ativos de TI'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.serial_number})'

    def get_status_badge(self):
        badges = {
            'active': 'success',
            'available': 'primary',
            'maintenance': 'warning',
            'inactive': 'secondary',
            'disposed': 'danger',
        }
        return badges.get(self.status, 'secondary')

    def get_type_icon(self):
        icons = {
            'laptop': 'bi-laptop',
            'desktop': 'bi-pc-display',
            'server': 'bi-server',
            'printer': 'bi-printer',
            'network': 'bi-router',
            'monitor': 'bi-display',
            'phone': 'bi-telephone',
            'mobile': 'bi-phone',
            'other': 'bi-device-hdd',
        }
        return icons.get(self.asset_type, 'bi-device-hdd')

    def is_warranty_valid(self):
        if self.warranty_until:
            return timezone.now().date() <= self.warranty_until
        return None

    def is_warranty_expiring_soon(self):
        if self.warranty_until:
            delta = (self.warranty_until - timezone.now().date()).days
            return 0 <= delta <= 30
        return False


class MaintenanceRecord(models.Model):
    TYPE_CHOICES = [
        ('preventive', 'Preventiva'),
        ('corrective', 'Corretiva'),
        ('upgrade', 'Upgrade'),
        ('cleaning', 'Limpeza'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Agendada'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
    ]

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name='Ativo'
    )
    maintenance_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='scheduled')
    description = models.TextField('Descrição')
    performed_by = models.CharField('Realizado por', max_length=200, blank=True)
    technician = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='maintenance_records',
        verbose_name='Técnico Responsável'
    )
    scheduled_date = models.DateField('Data Agendada', null=True, blank=True)
    completed_date = models.DateField('Data de Conclusão', null=True, blank=True)
    cost = models.DecimalField('Custo (R$)', max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Manutenção'
        verbose_name_plural = 'Registros de Manutenção'
        ordering = ['-created_at']

    def __str__(self):
        return f'Manutenção {self.get_maintenance_type_display()} — {self.asset.name}'
