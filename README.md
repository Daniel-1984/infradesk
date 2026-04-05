<img width="577" height="701" alt="image" src="https://github.com/user-attachments/assets/fa2c5916-e527-40ae-b19f-c4b3034e4af5" />
<img width="1901" height="930" alt="image" src="https://github.com/user-attachments/assets/5310523f-056a-46cf-b34b-06932cf518ec" />
<img width="1873" height="881" alt="image" src="https://github.com/user-attachments/assets/479fc18e-d497-476c-938d-3a12de2f3e04" />
<img width="1914" height="778" alt="image" src="https://github.com/user-attachments/assets/a3f5ad95-f954-471f-8b91-bfa7a9982945" />
<img width="1917" height="896" alt="image" src="https://github.com/user-attachments/assets/f14038e9-1bc5-48ad-86a8-23432a58bc65" />
<img width="1072" height="877" alt="image" src="https://github.com/user-attachments/assets/c2692c98-8917-4e3c-b9ab-252c74ac2883" />
<img width="1888" height="858" alt="image" src="https://github.com/user-attachments/assets/d8537477-b6fb-41cd-92f6-1f7ec30d38d0" />






# InfraDesk

> Sistema web corporativo de suporte técnico e gestão de ativos de TI, desenvolvido com Django 5, Bootstrap 5 e SQLite.

---

## Visão Geral

O **InfraDesk** é um sistema interno de help desk e inventário de TI projetado para atender às necessidades operacionais de equipes de suporte técnico em ambientes corporativos. Ele centraliza o ciclo de vida de chamados, o controle de ativos, o histórico de manutenções e a gestão de usuários em uma interface moderna e responsiva.

O projeto foi desenvolvido com foco em **organização de código**, **boas práticas Django** e **experiência do usuário**, refletindo padrões de desenvolvimento encontrados em sistemas corporativos reais.

---

## Funcionalidades

### Gestão de Chamados
- Abertura de chamados com título, descrição, categoria e prioridade
- Fluxo de status: Aberto → Em Andamento → Aguardando → Resolvido → Fechado
- Classificação por prioridade: Baixa, Média, Alta e Crítica
- Atribuição de técnicos responsáveis
- Prazo (SLA) com indicador visual de atraso
- Thread de comentários com suporte a **notas internas** (visíveis apenas para técnicos)
- Vinculação de chamados a equipamentos do inventário
- Filtros por status, prioridade, categoria e busca textual

### Inventário de Ativos de TI
- Cadastro completo de equipamentos: notebooks, desktops, servidores, impressoras, switches, monitores e mais
- Rastreamento por número de série e patrimônio
- Controle de status: Em Uso, Disponível, Em Manutenção, Inativo, Descartado
- Especificações técnicas (OS, processador, RAM, armazenamento, IP, MAC)
- Informações de aquisição: data de compra, garantia, valor, fornecedor
- Alertas automáticos de garantia próxima do vencimento
- Atribuição de responsável por equipamento

### Manutenção de Equipamentos
- Registro de manutenções preventivas, corretivas, upgrades e limpezas
- Controle de status, datas e custo por manutenção
- Histórico completo por equipamento

### Dashboard Analítico
- Métricas em tempo real de chamados abertos, em andamento, resolvidos e críticos
- Gráficos de chamados por status e prioridade (Chart.js)
- Ranking de técnicos por chamados resolvidos
- Alertas de garantias próximas do vencimento
- Últimas atividades de manutenção

### Controle de Acesso
- Três níveis de acesso: **Administrador**, **Técnico** e **Usuário**
- Usuários comuns veem apenas seus próprios chamados
- Técnicos têm acesso completo ao sistema e ao painel de gestão
- Administrador com acesso ao Django Admin customizado

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 + Django 5.0 |
| Banco de dados | SQLite (dev) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Gráficos | Chart.js 4.4 |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Assets estáticos | WhiteNoise |
| Autenticação | Django Auth (built-in) |

---

## Estrutura do Projeto

```
infradesk/
├── infradesk/          # Configurações do projeto (settings, urls, wsgi)
├── accounts/           # App de autenticação e perfis de usuário
├── tickets/            # App de chamados e comentários
├── assets/             # App de inventário e manutenção
├── dashboard/          # App do painel analítico
├── templates/          # Templates HTML organizados por app
├── static/
│   ├── css/style.css   # Estilos customizados
│   └── js/main.js      # JavaScript da interface
├── fixtures/           # Dados iniciais (departamentos)
├── setup_demo.py       # Script para popular dados de demonstração
├── manage.py
└── requirements.txt
```

---

## Instalação e Execução

### Pré-requisitos
- Python 3.10 ou superior
- pip

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/infradesk.git
cd infradesk
```

**2. Crie e ative o ambiente virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Execute as migrações**
```bash
python manage.py migrate
```

**5. Popule o banco com dados de demonstração**
```bash
python setup_demo.py
```

**6. Inicie o servidor**
```bash
python manage.py runserver
```


## Dados de Demonstração

O script `setup_demo.py` cria automaticamente:

- 6 departamentos (TI, RH, Financeiro, Comercial, Operações, Jurídico)
- 6 usuários com diferentes perfis e departamentos
- 8 ativos de TI (notebooks, servidor, impressora, switch, monitor)
- 8 chamados em diferentes status e prioridades
- Comentários e notas internas
- 3 registros de manutenção

---

## Screenshots

> Sugestão de capturas para o portfólio:

| Tela | Descrição |
|---|---|
| `/accounts/login/` | Tela de login com tema escuro e cards de credenciais demo |
| `/dashboard/` | Dashboard com gráficos, métricas e lista de chamados recentes |
| `/tickets/` | Lista de chamados com filtros e badges de prioridade |
| `/tickets/1/` | Detalhe do chamado com thread de comentários e painel de gestão |
| `/assets/` | Grid de inventário com cards por tipo de equipamento |
| `/assets/1/` | Detalhe do ativo com especificações e histórico de manutenção |

---

## Roadmap

- [ ] Notificações por e-mail (abertura, atribuição, resolução)
- [ ] Exportação de relatórios em PDF e Excel
- [ ] API REST para integração com outros sistemas
- [ ] Autenticação SSO / LDAP corporativo
- [ ] Dashboard de SLA com métricas por período
- [ ] Upload de anexos em chamados
- [ ] Histórico de alterações (audit trail) por chamado
- [ ] Aplicativo mobile (PWA)
- [ ] Integração com Active Directory para sync de usuários

---



Desenvolvido por **[Daniel Luiz]** — [LinkedIn](https://linkedin.com) | [GitHub](https://github.com)

