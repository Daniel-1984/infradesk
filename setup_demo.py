"""
Script para popular o banco de dados com dados de demonstracao.
Execute com: python manage.py shell < setup_demo.py
Ou: python setup_demo.py (a partir do diretorio do projeto)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'infradesk.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import UserProfile, Department
from assets.models import Asset, MaintenanceRecord
from tickets.models import Ticket, TicketComment


def create_departments():
    depts = [
        ('Tecnologia da Informacao', 'TI'),
        ('Recursos Humanos', 'RH'),
        ('Financeiro', 'FIN'),
        ('Comercial', 'COM'),
        ('Operacões', 'OPS'),
        ('Juridico', 'JUR'),
    ]
    created = []
    for name, code in depts:
        d, _ = Department.objects.get_or_create(code=code, defaults={'name': name})
        created.append(d)
    print(f'  OK {len(created)} departamentos criados')
    return created


def create_users():
    users_data = [
        {
            'username': 'admin',
            'first_name': 'Carlos',
            'last_name': 'Mendes',
            'email': 'admin@infradesk.com.br',
            'password': 'admin123',
            'role': 'admin',
            'dept': 'TI',
            'employee_id': 'EMP001',
            'phone': '(11) 3000-1000',
        },
        {
            'username': 'tecnico',
            'first_name': 'Ana',
            'last_name': 'Silva',
            'email': 'ana.silva@infradesk.com.br',
            'password': 'tecnico123',
            'role': 'technician',
            'dept': 'TI',
            'employee_id': 'EMP002',
            'phone': '(11) 3000-1001',
        },
        {
            'username': 'tecnico2',
            'first_name': 'Rafael',
            'last_name': 'Costa',
            'email': 'rafael.costa@infradesk.com.br',
            'password': 'tecnico123',
            'role': 'technician',
            'dept': 'TI',
            'employee_id': 'EMP003',
            'phone': '(11) 3000-1002',
        },
        {
            'username': 'usuario',
            'first_name': 'Mariana',
            'last_name': 'Oliveira',
            'email': 'mariana.oliveira@infradesk.com.br',
            'password': 'usuario123',
            'role': 'user',
            'dept': 'RH',
            'employee_id': 'EMP010',
            'phone': '(11) 3000-2001',
        },
        {
            'username': 'joao.financeiro',
            'first_name': 'Joao',
            'last_name': 'Pereira',
            'email': 'joao.pereira@infradesk.com.br',
            'password': 'usuario123',
            'role': 'user',
            'dept': 'FIN',
            'employee_id': 'EMP020',
            'phone': '(11) 3000-3001',
        },
        {
            'username': 'lucia.comercial',
            'first_name': 'Lucia',
            'last_name': 'Santos',
            'email': 'lucia.santos@infradesk.com.br',
            'password': 'usuario123',
            'role': 'user',
            'dept': 'COM',
            'employee_id': 'EMP030',
        },
    ]

    created = []
    for data in users_data:
        user, c = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'is_staff': data['role'] == 'admin',
                'is_superuser': data['role'] == 'admin',
            }
        )
        if c:
            user.set_password(data['password'])
            user.save()

        dept = Department.objects.filter(code=data['dept']).first()
        profile = user.profile
        profile.role = data['role']
        profile.department = dept
        profile.phone = data.get('phone', '')
        profile.employee_id = data.get('employee_id', '')
        profile.save()
        created.append(user)

    print(f'  OK {len(created)} usuarios criados')
    return created


def create_assets():
    tech = User.objects.get(username='tecnico')
    usuario = User.objects.get(username='usuario')
    joao = User.objects.get(username='joao.financeiro')

    assets_data = [
        {
            'name': 'NB-MKT-001',
            'asset_type': 'laptop',
            'brand': 'Dell',
            'model_name': 'Latitude 5530',
            'serial_number': 'DELL-5530-A001',
            'asset_tag': 'PAT-00101',
            'status': 'active',
            'condition': 'good',
            'location': 'Comercial -- Mesa 12',
            'assigned_to': usuario,
            'purchase_date': date(2023, 3, 15),
            'warranty_until': date(2026, 3, 15),
            'purchase_value': 5890.00,
            'supplier': 'Dell Brasil',
            'operating_system': 'Windows 11 Pro',
            'processor': 'Intel Core i7-1265U',
            'ram': '16 GB DDR4',
            'storage': '512 GB SSD NVMe',
            'ip_address': '192.168.1.101',
        },
        {
            'name': 'NB-FIN-002',
            'asset_type': 'laptop',
            'brand': 'Lenovo',
            'model_name': 'ThinkPad E15',
            'serial_number': 'LNV-E15-B002',
            'asset_tag': 'PAT-00102',
            'status': 'active',
            'condition': 'good',
            'location': 'Financeiro -- Mesa 5',
            'assigned_to': joao,
            'purchase_date': date(2023, 6, 10),
            'warranty_until': date(2026, 6, 10),
            'purchase_value': 4990.00,
            'supplier': 'Lenovo Brasil',
            'operating_system': 'Windows 11 Pro',
            'processor': 'Intel Core i5-1235U',
            'ram': '8 GB DDR4',
            'storage': '256 GB SSD',
            'ip_address': '192.168.1.102',
        },
        {
            'name': 'SRV-PRINC-001',
            'asset_type': 'server',
            'brand': 'HP',
            'model_name': 'ProLiant DL380 Gen10',
            'serial_number': 'HP-DL380-C001',
            'asset_tag': 'PAT-00201',
            'status': 'active',
            'condition': 'good',
            'location': 'Datacenter -- Rack A, Slot 3',
            'assigned_to': tech,
            'purchase_date': date(2022, 1, 20),
            'warranty_until': date(2025, 1, 20),
            'purchase_value': 48500.00,
            'supplier': 'HP Enterprise Brasil',
            'operating_system': 'Windows Server 2022',
            'processor': 'Intel Xeon Gold 6226R (2x)',
            'ram': '128 GB DDR4 ECC',
            'storage': '4 TB RAID 10',
            'ip_address': '10.0.0.1',
        },
        {
            'name': 'IMP-RH-001',
            'asset_type': 'printer',
            'brand': 'HP',
            'model_name': 'LaserJet Pro M404dn',
            'serial_number': 'HP-M404-D001',
            'asset_tag': 'PAT-00301',
            'status': 'maintenance',
            'condition': 'fair',
            'location': 'RH -- Sala de Impressao',
            'purchase_date': date(2021, 8, 5),
            'warranty_until': date(2023, 8, 5),
            'purchase_value': 1890.00,
            'supplier': 'HP Store',
            'ip_address': '192.168.1.200',
        },
        {
            'name': 'SW-CORE-001',
            'asset_type': 'network',
            'brand': 'Cisco',
            'model_name': 'Catalyst 9200L',
            'serial_number': 'CIS-9200-E001',
            'asset_tag': 'PAT-00401',
            'status': 'active',
            'condition': 'good',
            'location': 'Datacenter -- Rack B',
            'assigned_to': tech,
            'purchase_date': date(2022, 4, 12),
            'warranty_until': date(2025, 4, 12),
            'purchase_value': 15200.00,
            'supplier': 'Cisco Systems Brasil',
        },
        {
            'name': 'NB-TI-003',
            'asset_type': 'laptop',
            'brand': 'Apple',
            'model_name': 'MacBook Pro 14" M3',
            'serial_number': 'APL-MBP14-F001',
            'asset_tag': 'PAT-00103',
            'status': 'available',
            'condition': 'new',
            'location': 'TI -- Estoque',
            'purchase_date': date(2024, 1, 8),
            'warranty_until': date(2026, 1, 8),
            'purchase_value': 18990.00,
            'supplier': 'Apple Store Brasil',
            'operating_system': 'macOS Sonoma',
            'processor': 'Apple M3 Pro',
            'ram': '18 GB Unified Memory',
            'storage': '512 GB SSD',
        },
        {
            'name': 'MON-COM-005',
            'asset_type': 'monitor',
            'brand': 'LG',
            'model_name': '27UK650-W 4K',
            'serial_number': 'LG-27UK-G001',
            'asset_tag': 'PAT-00501',
            'status': 'active',
            'condition': 'good',
            'location': 'Comercial -- Mesa 15',
            'purchase_date': date(2023, 9, 1),
            'warranty_until': date(2026, 9, 1),
            'purchase_value': 2490.00,
        },
        {
            'name': 'NB-OPS-004',
            'asset_type': 'desktop',
            'brand': 'Dell',
            'model_name': 'OptiPlex 7090',
            'serial_number': 'DELL-7090-H001',
            'asset_tag': 'PAT-00104',
            'status': 'inactive',
            'condition': 'poor',
            'location': 'TI -- Deposito',
            'purchase_date': date(2019, 5, 10),
            'warranty_until': date(2022, 5, 10),
            'purchase_value': 3200.00,
            'operating_system': 'Windows 10 Pro',
            'processor': 'Intel Core i5-10500',
            'ram': '8 GB DDR4',
            'storage': '256 GB SSD',
        },
    ]

    created = []
    for data in assets_data:
        asset, c = Asset.objects.get_or_create(
            serial_number=data['serial_number'],
            defaults=data
        )
        created.append(asset)

    print(f'  OK {len(created)} ativos criados')
    return created


def create_tickets(assets):
    admin = User.objects.get(username='admin')
    tech = User.objects.get(username='tecnico')
    tech2 = User.objects.get(username='tecnico2')
    usuario = User.objects.get(username='usuario')
    joao = User.objects.get(username='joao.financeiro')
    lucia = User.objects.get(username='lucia.comercial')

    notebook_rh = Asset.objects.get(serial_number='DELL-5530-A001')
    impressora = Asset.objects.get(serial_number='HP-M404-D001')
    servidor = Asset.objects.get(serial_number='HP-DL380-C001')

    tickets_data = [
        {
            'title': 'Notebook nao conecta ao Wi-Fi corporativo',
            'description': 'Meu notebook parou de conectar a rede Wi-Fi apos a ultima atualizacao do Windows. Ja reiniciei o equipamento diversas vezes mas o problema persiste. A rede aparece na lista mas ao tentar conectar exibe "Nao foi possivel conectar a esta rede". Afeta apenas o Wi-Fi, cabo funciona normalmente.',
            'priority': 'high',
            'status': 'in_progress',
            'category': 'network',
            'created_by': usuario,
            'assigned_to': tech,
            'asset': notebook_rh,
            'due_date': date.today() + timedelta(days=2),
        },
        {
            'title': 'Impressora da area de RH nao esta imprimindo',
            'description': 'A impressora HP LaserJet da sala de RH apresentou erro E02 e parou de funcionar. Todos os trabalhos de impressao ficam na fila e nao saem. Ja desliiguei e liguei novamente sem sucesso. Temos documentos urgentes para imprimir hoje.',
            'priority': 'critical',
            'status': 'open',
            'category': 'hardware',
            'created_by': usuario,
            'asset': impressora,
        },
        {
            'title': 'Solicitar acesso ao sistema ERP -- modulo Financeiro',
            'description': 'Preciso de acesso ao modulo Financeiro do sistema ERP para consulta de relatorios gerenciais. Meu gestor, Sr. Roberto Alves, ja aprovou via e-mail. Anexo segue o e-mail de aprovacao para referencia. Aguardo liberacao com urgencia pois ha reuniao na quinta-feira.',
            'priority': 'medium',
            'status': 'open',
            'category': 'access',
            'created_by': joao,
        },
        {
            'title': 'Excel travando ao abrir planilhas grandes',
            'description': 'O Microsoft Excel esta travando completamente quando tento abrir planilhas com mais de 50 mil linhas. O programa fica "sem resposta" por varios minutos ou fecha sozinho. Isso esta prejudicando meu trabalho de fechamento mensal. Ja tentei reparar o Office pelo Painel de Controle mas nao resolveu.',
            'priority': 'medium',
            'status': 'in_progress',
            'category': 'software',
            'created_by': joao,
            'assigned_to': tech2,
        },
        {
            'title': 'Lentidao no sistema de vendas -- CRM',
            'description': 'O sistema CRM esta extremamente lento desde segunda-feira. Paginas que antes carregavam em 2 segundos agora levam mais de 30 segundos. Ja afetou toda a equipe comercial (8 pessoas). Temos reuniao com cliente importante amanha e precisamos do sistema funcionando.',
            'priority': 'critical',
            'status': 'in_progress',
            'category': 'software',
            'created_by': lucia,
            'assigned_to': tech,
            'asset': servidor,
        },
        {
            'title': 'Tela azul (BSOD) ao iniciar o computador',
            'description': 'Computador apresenta tela azul com erro "MEMORY_MANAGEMENT" toda vez que e ligado. O erro 0x0000001A aparece poucos segundos apos o Windows comecar a carregar. Preciso do equipamento funcionando para trabalhar.',
            'priority': 'high',
            'status': 'resolved',
            'category': 'hardware',
            'created_by': lucia,
            'assigned_to': tech2,
        },
        {
            'title': 'Solicitar novo notebook para funcionario em onboarding',
            'description': 'Temos novo colaborador iniciando na segunda-feira (Pedro Alves -- Analista de Marketing). Precisamos de um notebook configurado com Windows 11, Office 365, acesso ao e-mail corporativo e VPN. Favor confirmar disponibilidade de equipamento em estoque.',
            'priority': 'low',
            'status': 'closed',
            'category': 'hardware',
            'created_by': admin,
            'assigned_to': tech,
        },
        {
            'title': 'VPN nao conecta trabalhando em home office',
            'description': 'Nao consigo conectar a VPN corporativa de casa. O cliente GlobalProtect exibe o erro "Gateway nao responde". Na empresa a VPN funciona normalmente. Ja testei em duas redes diferentes (casa e 4G do celular). Logs do cliente estao disponiveis para analise.',
            'priority': 'high',
            'status': 'open',
            'category': 'network',
            'created_by': usuario,
        },
    ]

    created = []
    for data in tickets_data:
        ticket = Ticket.objects.create(**data)
        created.append(ticket)

    print(f'  OK {len(created)} chamados criados')
    return created


def create_comments(tickets):
    admin = User.objects.get(username='admin')
    tech = User.objects.get(username='tecnico')
    tech2 = User.objects.get(username='tecnico2')
    usuario = User.objects.get(username='usuario')

    t1 = tickets[0]  # Wi-Fi
    t3 = tickets[2]  # Acesso ERP
    t4 = tickets[3]  # Excel
    t5 = tickets[4]  # CRM lento
    t6 = tickets[5]  # BSOD

    comments = [
        # Wi-Fi
        TicketComment(ticket=t1, author=tech, content='Ola! Recebemos seu chamado. Estou verificando o problema. Pode confirmar qual versao da atualizacao do Windows foi instalada? (Configuracões > Windows Update > Historico de Atualizacões)', is_internal=False),
        TicketComment(ticket=t1, author=usuario, content='Versao instalada: KB5033375 -- instalada sexta-feira as 22h. O problema comecou na segunda-feira ao ligar o notebook.', is_internal=False),
        TicketComment(ticket=t1, author=tech, content='Problema identificado: driver de rede Intel AX201 incompativel com KB5033375. Vou enviar o rollback do driver por e-mail. Por favor, siga as instrucões em anexo.', is_internal=False),
        TicketComment(ticket=t1, author=tech, content='NOTA INTERNA: Bug conhecido da Microsoft. Aguardando patch oficial. Rollback do driver resolve temporariamente. Monitorar outros equipamentos com mesmo hardware.', is_internal=True),

        # Acesso ERP
        TicketComment(ticket=t3, author=admin, content='Solicitacao recebida. Encaminhei para o gestor do sistema ERP para validacao. Aguarde confirmacao em ate 1 dia util.', is_internal=False),

        # Excel
        TicketComment(ticket=t4, author=tech2, content='Bom dia! Verificando o chamado. Voce pode enviar um print do gerenciador de tarefas quando o Excel travar? Preciso ver o uso de memoria RAM.', is_internal=False),
        TicketComment(ticket=t4, author=tech2, content='NOTA INTERNA: Suspeita de memoria insuficiente (8GB). Maquina LNV-E15-B002. Verificar possibilidade de upgrade de RAM para 16GB. Orcamento: ~R$250.', is_internal=True),

        # CRM Lento
        TicketComment(ticket=t5, author=tech, content='Chamado recebido com prioridade critica. Iniciei investigacao no servidor. Identificamos pico de CPU no servidor SQL as 08h de segunda-feira. Investigando causa raiz.', is_internal=False),
        TicketComment(ticket=t5, author=tech, content='INTERNO: Query sem indice causando full table scan em tabela de 2M registros. DBA foi acionado. ETA fix: 2-3 horas.', is_internal=True),
        TicketComment(ticket=t5, author=tech, content='Atualizacao: identificamos uma query problematica no modulo de relatorios. A equipe de desenvolvimento foi notificada. Aplicamos solucao temporaria que deve melhorar a performance. Monitorando o sistema.', is_internal=False),

        # BSOD - Resolvido
        TicketComment(ticket=t6, author=tech2, content='Analisando o dump de memoria. Erro indica falha em modulo de RAM.', is_internal=False),
        TicketComment(ticket=t6, author=tech2, content='Diagnostico concluido: um dos modulos de RAM estava com defeito. Realizamos a substituicao pelo modulo reserva do estoque. Equipamento testado e funcionando normalmente. Chamado resolvido!', is_internal=False),
    ]

    for c in comments:
        c.save()

    print(f'  OK {len(comments)} comentarios criados')


def create_maintenance(assets):
    tech = User.objects.get(username='tecnico')
    tech2 = User.objects.get(username='tecnico2')

    impressora = Asset.objects.get(serial_number='HP-M404-D001')
    servidor = Asset.objects.get(serial_number='HP-DL380-C001')

    records = [
        MaintenanceRecord(
            asset=impressora,
            maintenance_type='corrective',
            status='in_progress',
            description='Erro E02 -- verificacao do fusor e troca de componentes internos',
            technician=tech,
            scheduled_date=date.today(),
            cost=350.00,
        ),
        MaintenanceRecord(
            asset=servidor,
            maintenance_type='preventive',
            status='completed',
            description='Manutencao preventiva semestral: limpeza, verificacao de logs, teste de failover e atualizacao de firmware',
            technician=tech2,
            scheduled_date=date.today() - timedelta(days=30),
            completed_date=date.today() - timedelta(days=29),
            cost=0.00,
            notes='Tudo normal. Proxima manutencao em 6 meses.',
        ),
        MaintenanceRecord(
            asset=servidor,
            maintenance_type='upgrade',
            status='scheduled',
            description='Expansao de memoria RAM de 128GB para 256GB para suportar nova carga de trabalho do CRM',
            technician=tech,
            scheduled_date=date.today() + timedelta(days=15),
            cost=8500.00,
        ),
    ]

    for r in records:
        r.save()

    print(f'  OK {len(records)} registros de manutencao criados')


def main():
    print('\nInfraDesk -- Criando dados de demonstracao...\n')

    print('-> Departamentos...')
    create_departments()

    print('-> Usuarios...')
    create_users()

    print('-> Ativos de TI...')
    assets = create_assets()

    print('-> Chamados...')
    tickets = create_tickets(assets)

    print('-> Comentarios...')
    create_comments(tickets)

    print('-> Manutencões...')
    create_maintenance(assets)

    print('\n[OK] Dados criados com sucesso!\n')
    print('=' * 50)
    print('Credenciais de acesso:')
    print('  Admin:    admin / admin123')
    print('  Tecnico:  tecnico / tecnico123')
    print('  Usuario:  usuario / usuario123')
    print('=' * 50)
    print('Acesse: http://127.0.0.1:8000\n')


if __name__ == '__main__':
    main()
