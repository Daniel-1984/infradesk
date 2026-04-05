"""
Management command: python manage.py load_playbook
Popula a base de conhecimento com entradas iniciais do playbook técnico.
Seguro de executar múltiplas vezes (usa get_or_create pelo título+domínio).
"""

from django.core.management.base import BaseCommand
from diagnostics.models import PlaybookEntry


PLAYBOOK_DATA = [
    # ── ERP PROTHEUS ──────────────────────────────────────────────────────────
    {
        'domain': 'ERP_PROTHEUS',
        'title': 'Lentidão geral no Protheus',
        'keywords': 'lento,lentidao,travando,demora,trava,devagar,demorado,carregando,aguardando',
        'probable_cause': (
            'Lentidão no Protheus pode ser causada por sobrecarga no AppServer, '
            'número excessivo de conexões simultâneas no DBAccess, '
            'consultas SQL sem índice adequado ou rede congestionada entre client e servidor.'
        ),
        'checklist': (
            'Verificar CPU e memória do servidor AppServer\n'
            'Verificar quantidade de conexões ativas no DBAccess\n'
            'Analisar log do AppServer (console.log) em busca de erros ou filas\n'
            'Verificar latência de rede entre estação e servidor (ping, tracert)\n'
            'Identificar se a lentidão é global ou apenas para um usuário/módulo\n'
            'Verificar se há jobs ou processos pesados rodando em paralelo\n'
            'Analisar queries lentas no banco de dados (slow query log)'
        ),
        'recommended_action': (
            'Se global: reiniciar AppServer fora do horário de pico. '
            'Se pontual: investigar rotina específica com profiler do Protheus. '
            'Considerar tunning de índices e parâmetros MV_TOPMAX.'
        ),
        'priority_hint': 'high',
    },
    {
        'domain': 'ERP_PROTHEUS',
        'title': 'Erro de conexão com o Protheus (SmartClient)',
        'keywords': 'conexao,conectar,smartclient,nao abre,nao conecta,offline,servidor indisponivel,topconnect',
        'probable_cause': (
            'Falha de conexão pode indicar AppServer fora do ar, '
            'porta bloqueada por firewall, '
            'configuração incorreta no SmartClient.ini ou DBAccess parado.'
        ),
        'checklist': (
            'Verificar se o serviço AppServer está ativo no servidor\n'
            'Verificar se o serviço DBAccess está ativo\n'
            'Testar conexão telnet na porta configurada do Protheus (ex: 7890)\n'
            'Conferir configurações do SmartClient.ini (IP, porta, environment)\n'
            'Verificar regras de firewall na porta do Protheus\n'
            'Analisar console.log do AppServer para mensagens de erro\n'
            'Verificar se licenças de acesso estão disponíveis'
        ),
        'recommended_action': (
            'Reiniciar AppServer e DBAccess. '
            'Conferir configurações de rede e firewall. '
            'Verificar licenças no Protheus License Server.'
        ),
        'priority_hint': 'critical',
    },
    {
        'domain': 'ERP_PROTHEUS',
        'title': 'Erro ao gerar NF-e / Nota Fiscal Eletrônica',
        'keywords': 'nfe,nota fiscal,nf-e,sefaz,rejeicao,transmissao,xml,danfe,emissao nota',
        'probable_cause': (
            'Rejeição pela SEFAZ por inconsistência nos dados cadastrais, '
            'certificado digital vencido, '
            'parâmetros fiscais incorretos ou timeout de comunicação com a SEFAZ.'
        ),
        'checklist': (
            'Verificar código de rejeição retornado pela SEFAZ\n'
            'Conferir validade do certificado digital A1/A3\n'
            'Verificar parametrizações fiscais (MV_CFOP, MV_ESTADO, etc.)\n'
            'Conferir dados cadastrais do emitente (CNPJ, IE, endereço)\n'
            'Verificar conectividade com endpoint da SEFAZ\n'
            'Analisar XML gerado em busca de campos faltantes ou inválidos\n'
            'Consultar tabela de rejeições da SEFAZ pelo código retornado'
        ),
        'recommended_action': (
            'Corrigir os dados conforme código de rejeição da SEFAZ. '
            'Renovar certificado digital se vencido. '
            'Consultar documentação técnica NF-e e acionar equipe fiscal se necessário.'
        ),
        'priority_hint': 'high',
    },

    # ── DATABASE ───────────────────────────────────────────────────────────────
    {
        'domain': 'DATABASE',
        'title': 'Lentidão no banco de dados',
        'keywords': 'banco lento,sql lento,query demorada,timeout,lentidao banco,consulta lenta,travando banco',
        'probable_cause': (
            'Queries sem índice adequado, fragmentação de índices, '
            'crescimento excessivo de log de transações, '
            'bloqueios (locks/deadlocks) entre sessões concorrentes '
            'ou falta de recursos de hardware no servidor de banco.'
        ),
        'checklist': (
            'Identificar queries mais lentas via DMVs (SQL Server) ou slow query log (MySQL)\n'
            'Verificar fragmentação de índices e executar reorganize/rebuild se necessário\n'
            'Verificar espaço em disco e crescimento do arquivo de log\n'
            'Analisar locks e deadlocks ativos (sp_who2, sys.dm_exec_requests)\n'
            'Verificar consumo de CPU e memória do servidor de banco\n'
            'Analisar plano de execução das queries problemáticas\n'
            'Verificar estatísticas desatualizadas (UPDATE STATISTICS)'
        ),
        'recommended_action': (
            'Executar UPDATE STATISTICS e reorganização de índices. '
            'Matar sessões bloqueadas se necessário. '
            'Agendar manutenção de índices em janela de baixo uso.'
        ),
        'priority_hint': 'high',
    },
    {
        'domain': 'DATABASE',
        'title': 'Falha de conexão com o banco de dados',
        'keywords': 'sem conexao banco,nao conecta banco,banco fora,instancia parada,connection refused,login failed',
        'probable_cause': (
            'Serviço do banco de dados parado, '
            'limite de conexões atingido, '
            'credenciais incorretas ou expiradas, '
            'firewall bloqueando a porta do banco.'
        ),
        'checklist': (
            'Verificar se o serviço do banco está rodando (SQL Server Agent, mysqld, etc.)\n'
            'Verificar número de conexões ativas vs. limite configurado\n'
            'Testar conexão com credenciais via ferramenta de admin (SSMS, DBeaver)\n'
            'Verificar regras de firewall na porta do banco (1433, 3306, 5432)\n'
            'Verificar logs de erro do banco de dados\n'
            'Confirmar se string de conexão da aplicação está correta'
        ),
        'recommended_action': (
            'Reiniciar o serviço do banco se parado. '
            'Aumentar limite de conexões se necessário. '
            'Atualizar credenciais na aplicação se expiradas.'
        ),
        'priority_hint': 'critical',
    },

    # ── NETWORK ────────────────────────────────────────────────────────────────
    {
        'domain': 'NETWORK',
        'title': 'Sem acesso à internet ou rede instável',
        'keywords': 'sem internet,rede caiu,sem rede,wifi caiu,instabilidade,ping alto,conexao caindo,sem conectividade',
        'probable_cause': (
            'Falha no roteador ou switch, '
            'cabo de rede danificado, '
            'configuração DHCP incorreta, '
            'sobrecarga no link de internet ou problema no provedor.'
        ),
        'checklist': (
            'Verificar se outros dispositivos na mesma rede têm o mesmo problema\n'
            'Testar ping para o gateway padrão (ex: 192.168.1.1)\n'
            'Testar ping para DNS externo (8.8.8.8)\n'
            'Verificar luzes de status do switch/roteador\n'
            'Reiniciar adaptador de rede da estação\n'
            'Verificar cabo ou sinal WiFi\n'
            'Verificar se IP foi atribuído corretamente (ipconfig)\n'
            'Verificar status do link com o provedor de internet'
        ),
        'recommended_action': (
            'Se problema pontual na estação: renovar IP (ipconfig /release + /renew), trocar cabo. '
            'Se problema generalizado: reiniciar switch/roteador. '
            'Se problema no link: contatar provedor.'
        ),
        'priority_hint': 'high',
    },
    {
        'domain': 'NETWORK',
        'title': 'VPN sem conexão ou queda frequente',
        'keywords': 'vpn,acesso remoto,vpn caindo,nao conecta vpn,tunnel,remote access',
        'probable_cause': (
            'Credenciais VPN expiradas, '
            'certificado VPN vencido, '
            'firewall bloqueando porta VPN (UDP 1194, TCP 443, etc.) '
            'ou instabilidade no link de internet do usuário.'
        ),
        'checklist': (
            'Verificar se as credenciais VPN estão válidas e não expiradas\n'
            'Verificar se o cliente VPN está atualizado\n'
            'Testar com outro provedor de internet (hotspot 4G)\n'
            'Verificar logs do cliente VPN para código de erro\n'
            'Confirmar se o servidor VPN está operacional\n'
            'Verificar se firewall local ou antivírus está bloqueando'
        ),
        'recommended_action': (
            'Renovar credenciais VPN se expiradas. '
            'Reinstalar cliente VPN se corrompido. '
            'Liberar portas VPN no firewall corporativo.'
        ),
        'priority_hint': 'high',
    },

    # ── ACCESS ─────────────────────────────────────────────────────────────────
    {
        'domain': 'ACCESS',
        'title': 'Usuário bloqueado ou senha expirada',
        'keywords': 'bloqueado,senha expirada,nao consigo logar,conta bloqueada,acesso negado,resetar senha,redefinir senha',
        'probable_cause': (
            'Tentativas de login incorretas excederam o limite de lockout do AD, '
            'política de expiração de senha atingiu o prazo '
            'ou usuário trocou de equipe e teve permissões revogadas.'
        ),
        'checklist': (
            'Verificar no Active Directory se a conta está bloqueada (Account Lockout)\n'
            'Identificar a origem do bloqueio (Lockout Status Tool ou Event Viewer)\n'
            'Desbloquear conta e redefinir senha se necessário\n'
            'Verificar se há sessões antigas com senha desatualizada causando lockout\n'
            'Orientar usuário sobre política de senhas vigente\n'
            'Verificar se dispositivos móveis têm senha antiga salva'
        ),
        'recommended_action': (
            'Desbloquear conta no AD. '
            'Redefinir senha e solicitar troca no próximo login. '
            'Investigar origem do lockout para prevenir reincidência.'
        ),
        'priority_hint': 'medium',
    },

    # ── OFFICE EXCEL ───────────────────────────────────────────────────────────
    {
        'domain': 'OFFICE_EXCEL',
        'title': 'Excel travando ou lento ao abrir arquivo',
        'keywords': 'excel lento,planilha travando,excel nao abre,xlsx demorado,arquivo pesado,excel congelando',
        'probable_cause': (
            'Arquivo com excesso de formatações, fórmulas voláteis (AGORA, HOJE, INDIRETO), '
            'conexões de dados externas desatualizadas, '
            'macros VBA pesadas ou arquivo corrompido.'
        ),
        'checklist': (
            'Abrir Excel em modo seguro (excel /safe) para descartar suplementos\n'
            'Verificar tamanho do arquivo — se maior que 20MB investigar causas\n'
            'Desabilitar cálculo automático temporariamente (Fórmulas > Cálculo Manual)\n'
            'Remover formatações em excesso (células em branco formatadas)\n'
            'Verificar e remover conexões de dados externas desnecessárias\n'
            'Salvar como novo arquivo xlsx para limpar metadados corrompidos\n'
            'Verificar se suplementos do Excel estão causando o problema'
        ),
        'recommended_action': (
            'Salvar uma cópia limpa do arquivo. '
            'Substituir fórmulas voláteis por valores onde possível. '
            'Dividir planilha muito grande em arquivos menores.'
        ),
        'priority_hint': 'low',
    },

    # ── EMAIL ──────────────────────────────────────────────────────────────────
    {
        'domain': 'EMAIL',
        'title': 'Outlook não sincroniza ou e-mails não chegam',
        'keywords': 'outlook,email nao chega,caixa entrada,sincronizar,e-mail parado,nao envia,nao recebe,offline mode',
        'probable_cause': (
            'Outlook em modo offline, '
            'perfil do Outlook corrompido, '
            'cota de caixa postal atingida, '
            'problema de autenticação com Exchange/Office 365 '
            'ou antivírus interferindo na comunicação.'
        ),
        'checklist': (
            'Verificar se Outlook está em modo offline (barra inferior ou Enviar/Receber)\n'
            'Verificar quota da caixa de entrada (Arquivo > Configurações de Conta)\n'
            'Testar acesso ao webmail (OWA/Outlook Web) para isolar problema\n'
            'Verificar credenciais da conta de e-mail (senha não expirou?)\n'
            'Reparar perfil do Outlook (Painel de Controle > Email > Perfis)\n'
            'Verificar se antivírus está em scan de e-mail causando lentidão\n'
            'Verificar logs do Exchange/M365 para rejeição de mensagens'
        ),
        'recommended_action': (
            'Retirar modo offline. '
            'Se corrompido: recriar perfil do Outlook. '
            'Limpar itens da lixeira e itens enviados se quota atingida.'
        ),
        'priority_hint': 'medium',
    },

    # ── HARDWARE ───────────────────────────────────────────────────────────────
    {
        'domain': 'HARDWARE',
        'title': 'Computador não liga ou desliga sozinho',
        'keywords': 'nao liga,desliga,reinicia,computador apagando,sem energia,tela preta,nao inicializa,boot',
        'probable_cause': (
            'Fonte de alimentação com defeito, '
            'superaquecimento causando desligamento de proteção, '
            'memória RAM com falha, '
            'HD/SSD com setores defeituosos impedindo boot '
            'ou problema na placa-mãe.'
        ),
        'checklist': (
            'Verificar temperatura do processador (BIOS ou ferramentas como HWMonitor)\n'
            'Verificar limpeza interna — poeira em excesso causa superaquecimento\n'
            'Testar RAM removendo módulos um a um\n'
            'Verificar integridade do HD/SSD (CrystalDiskInfo ou chkdsk)\n'
            'Verificar LEDs de diagnóstico na placa-mãe\n'
            'Testar com outra fonte de alimentação se disponível\n'
            'Verificar log de eventos do Windows (Visualizador de Eventos > Sistema)'
        ),
        'recommended_action': (
            'Se superaquecimento: limpeza e troca de pasta térmica. '
            'Se HD com falha: backup imediato e substituição. '
            'Se fonte: encaminhar para manutenção com peça de reposição.'
        ),
        'priority_hint': 'high',
    },

    # ── PRINTER ────────────────────────────────────────────────────────────────
    {
        'domain': 'PRINTER',
        'title': 'Impressora offline ou não imprime',
        'keywords': 'impressora,nao imprime,offline impressora,fila impressao,driver,imprimir,toner,cartucho',
        'probable_cause': (
            'Serviço de spooler parado no Windows, '
            'driver corrompido, '
            'fila de impressão travada com trabalho com erro, '
            'impressora fora do ar ou sem papel/toner.'
        ),
        'checklist': (
            'Verificar fisicamente: papel, toner/cartucho, cabos e energia\n'
            'Reiniciar o serviço Print Spooler (services.msc)\n'
            'Limpar fila de impressão: parar spooler, apagar C:\\Windows\\System32\\spool\\PRINTERS\\*, reiniciar\n'
            'Definir a impressora como padrão e testar página de teste\n'
            'Verificar se a impressora está Online (não em modo offline)\n'
            'Reinstalar driver se corrompido (Device Manager > Uninstall > Reinstall)\n'
            'Testar impressão a partir de outra estação para isolar problema'
        ),
        'recommended_action': (
            'Limpar fila e reiniciar spooler. '
            'Se persistir: reinstalar driver. '
            'Se hardware: acionar manutenção ou substituir consumíveis.'
        ),
        'priority_hint': 'medium',
    },

    # ── BACKUP ─────────────────────────────────────────────────────────────────
    {
        'domain': 'BACKUP',
        'title': 'Backup falhou ou não executou',
        'keywords': 'backup falhou,erro backup,backup nao rodou,restore,recuperar arquivo,dados perdidos,backup incompleto',
        'probable_cause': (
            'Espaço em disco insuficiente no destino do backup, '
            'falha de comunicação com storage ou nuvem, '
            'arquivo em uso durante o backup impedindo cópia, '
            'credenciais de acesso ao destino expiradas ou serviço de backup parado.'
        ),
        'checklist': (
            'Verificar log do software de backup (Veeam, Backup Exec, Windows Server Backup, etc.)\n'
            'Verificar espaço disponível no destino do backup\n'
            'Verificar conectividade com o destino (NAS, storage, nuvem)\n'
            'Verificar se credenciais de acesso ao destino ainda são válidas\n'
            'Verificar se o serviço de backup está em execução\n'
            'Identificar quais arquivos falharam (abertos/bloqueados?)\n'
            'Verificar integridade do último backup bem-sucedido'
        ),
        'recommended_action': (
            'Liberar espaço no destino ou expandir storage. '
            'Reconfigurar credenciais se expiradas. '
            'Executar backup manual imediato após corrigir a causa. '
            'Validar restauração periódica dos backups.'
        ),
        'priority_hint': 'high',
    },
]


class Command(BaseCommand):
    help = 'Carrega o playbook inicial de diagnóstico técnico'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for entry_data in PLAYBOOK_DATA:
            obj, created = PlaybookEntry.objects.update_or_create(
                domain=entry_data['domain'],
                title=entry_data['title'],
                defaults={
                    'keywords': entry_data['keywords'],
                    'probable_cause': entry_data['probable_cause'],
                    'checklist': entry_data['checklist'],
                    'recommended_action': entry_data['recommended_action'],
                    'priority_hint': entry_data['priority_hint'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Playbook carregado: {created_count} criados, {updated_count} atualizados.'
        ))
