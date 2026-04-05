# Deploy no PythonAnywhere (Grátis)

## 1. Criar conta
Acesse https://www.pythonanywhere.com e crie uma conta gratuita.
Anote seu **username** — o site ficará em `seuusername.pythonanywhere.com`.

---

## 2. Abrir console Bash
No dashboard do PythonAnywhere, clique em **"Bash"** (aba Consoles).

---

## 3. Clonar o repositório
```bash
git clone https://github.com/Daniel-1984/infradesk.git
cd infradesk
```

---

## 4. Criar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Criar o arquivo .env
```bash
cp .env.example .env
nano .env
```

Edite o arquivo com seus dados reais:
```
SECRET_KEY=cole-uma-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=seuusername.pythonanywhere.com
```

> Gere uma SECRET_KEY em: https://djecrety.ir/

Salve: `Ctrl+O`, Enter, `Ctrl+X`.

---

## 6. Configurar o banco e arquivos estáticos
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

## 7. Configurar Web App no PythonAnywhere

1. Vá na aba **Web** no dashboard
2. Clique em **"Add a new web app"**
3. Escolha **"Manual configuration"**
4. Escolha **Python 3.10**

### 7.1 — Configurar o WSGI
Clique no link do arquivo WSGI (ex: `/var/www/seuusername_pythonanywhere_com_wsgi.py`).

Apague todo o conteúdo e cole:
```python
import os
import sys

# Caminho do projeto
path = '/home/seuusername/infradesk'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'infradesk.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

> Substitua `seuusername` pelo seu username real.

Salve o arquivo.

### 7.2 — Configurar Virtualenv
Na aba Web, em **Virtualenv**, cole o caminho:
```
/home/seuusername/venv
```

### 7.3 — Configurar arquivos estáticos
Na aba Web, em **Static files**, adicione:

| URL         | Directory                                      |
|-------------|------------------------------------------------|
| `/static/`  | `/home/seuusername/infradesk/staticfiles`      |
| `/media/`   | `/home/seuusername/infradesk/media`            |

---

## 8. Reiniciar o app
Clique no botão verde **"Reload seuusername.pythonanywhere.com"**.

Acesse: `https://seuusername.pythonanywhere.com`

---

## 9. Atualizar o projeto (quando fizer mudanças)
```bash
cd ~/infradesk
source venv/bin/activate
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
```

Depois clique em **Reload** na aba Web.

---

## Problemas comuns

**Erro 500 / Internal Server Error**
- Verifique o arquivo de log em: aba Web > Log files > Error log
- Confirme que `.env` existe e tem `ALLOWED_HOSTS` correto

**Static files não aparecem (CSS quebrado)**
- Rode `python manage.py collectstatic --noinput` novamente
- Confirme os caminhos na seção Static files da aba Web

**ModuleNotFoundError**
- Confirme que o virtualenv está ativado e `pip install -r requirements.txt` foi executado
