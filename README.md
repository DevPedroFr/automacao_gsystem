# Automação GP

Projeto de prospecção e diagnóstico digital com frontend em Next.js e backend migrado para Python/FastAPI.

## Visão geral

- Frontend: Next.js + React + Tailwind
- Backend: FastAPI + SQLAlchemy + SQLite (dev)
- APIs externas: Google Places, PageSpeed, Meta Graph/Instagram, Claude/Gemini, Google Stitch
- Banco local em desenvolvimento: SQLite
- Produção/integração futura: Redis/Celery e PostgreSQL

Estrutura principal:

```text
automacao-de-diagnostico/
├── backend/                     # legado Node.js (mantido como referência)
├── backend_python/              # backend principal em Python/FastAPI
│   ├── app/
│   ├── scripts/
│   ├── tests/
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   └── Dockerfile
├── docs/                        # documentação da arquitetura e integrações
├── frontend/                    # aplicação web em Next.js
├── renata-flora-landing/
├── mota-tobias-landing/
├── package-lock.json
├── refactor.js
└── README.md
```

---

## Requisitos

- Node.js 18+
- npm 9+
- Python 3.11+
- pip
- Git
- (opcional) Redis para workers/filas

---

## 1) Clonar e preparar ambiente

```bash
git clone <repo-url>
cd automacao-de-diagnostico
```

### Backend Python

```bash
cd backend_python
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.\.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
pip install pytest pytest-asyncio
```

### Frontend Node

```bash
cd ../frontend
npm install
```

---

## 2) Configurar variáveis de ambiente

### Backend Python

Copie e ajuste o arquivo de ambiente:

```bash
cd backend_python
copy .env.example .env
```

Arquivo mínimo recomendado:

```env
APP_NAME="Automação GP API"
DEBUG=True
PORT=8000
DATABASE_URL=sqlite:///database.sqlite
REDIS_URL=redis://localhost:6379/0

GOOGLE_PLACES_API_KEY=
GOOGLE_PAGESPEED_API_KEY=
META_GRAPH_ACCESS_TOKEN=
META_INSTAGRAM_ACCOUNT_ID=
RAPIDAPI_KEY=
RAPIDAPI_HOST=instagram-data-api.p.rapidapi.com
ANTHROPIC_API_KEY=
CLAUDE_MODEL=claude-3-5-haiku-20241022
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
GOOGLE_STITCH_API_KEY=
GOOGLE_STITCH_BASE_URL=https://stitch.googleapis.com/v1
```

> Em desenvolvimento, o backend funciona com SQLite e sem chaves externas, usando fallback e dados locais quando necessário.

### Frontend

O frontend já vem com um arquivo de ambiente pronto em:

```text
frontend/.env.local
```

Conteúdo esperado:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Se o arquivo não existir, crie:

```bash
cd frontend
copy .env.local.example .env.local
```

Ou crie diretamente:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 3) Rodar o backend Python

Na raiz do projeto:

```bash
cd backend_python
.\.venv\Scripts\activate
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8001 --reload
```

Se estiver usando bash/zsh:

```bash
cd backend_python
source .venv/bin/activate
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### URLs do backend

- API principal: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/api/health

---

## 4) Rodar o frontend

Em outro terminal:

```bash
cd frontend
npm run dev
```

Acesse:

- http://localhost:3000

---

## 5) Validar a stack completa

### Testes do backend

```bash
cd backend_python
python -m pytest -q
```

Resultado esperado (validado):

```text
4 passed in 0.42s
```

### Build do frontend

```bash
cd frontend
npm run build
```

Resultado esperado (validado): build compilado com sucesso pelo Next.js.

---

## 6) Endpoints principais

### API Python

- GET /api/health
- GET /api/dashboard/stats
- GET /api/campaigns
- POST /api/campaigns
- GET /api/campaigns/{campaign_id}/leads
- GET /api/campaigns/{campaign_id}/leads/export
- GET /api/leads/{lead_id}
- POST /api/leads/{lead_id}/diagnostic
- GET /api/leads/{lead_id}/diagnostic
- GET /api/settings
- POST /api/settings
- POST /api/settings/test-webhook

### Compatibilidade legacy

Também existem rotas mantidas para compatibilidade com o motor antigo:

- /leads/search
- /triage/run
- /diagnosis/generate
- /site/generate

---

## 7) Solução de problemas comuns

### Erro: ModuleNotFoundError: No module named 'sqlalchemy'

```bash
cd backend_python
pip install -r requirements.txt
```

### Erro: async def functions are not natively supported

Isso acontece quando o pytest coleta um script assíncrono como teste. O projeto já foi ajustado para não coletar o utilitário de testes de Google Places como caso de teste. Se precisar validar manualmente:

```bash
cd backend_python
python scripts/test_google_places.py
```

### Frontend não encontra backend

Verifique se o arquivo [frontend/.env.local](frontend/.env.local) contém:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Backend não sobe

Confirme se a porta 8000 está livre e se a venv foi ativada. Rodando:

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### SQLAlchemy / SQLite

O backend usa SQLite em desenvolvimento. O arquivo do banco fica em:

```text
backend_python/database.sqlite
```

---

## 8) Observações importantes

- O backend Python já está no lugar principal e interage com o frontend em Next.js na porta 3000.
- O frontend já está configurado para consumir a API em http://localhost:8000/api.
- Sem chaves externas preenchidas, o sistema continua funcionando em modo local/de demonstração.
- Para rodar diagnósticos e geração de site com IA real, configure os serviços de API e chaves de ambiente.

---

## 9) Comandos rápidos de inicialização

### Windows PowerShell

```powershell
cd backend_python
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

### Linux/macOS

```bash
cd backend_python
source .venv/bin/activate
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Outro terminal:

```bash
cd frontend
npm install
npm run dev
```

---

## 10) Validação executada no ambiente

Os seguintes pontos foram confirmados no projeto:

- Backend Python importa corretamente e sobe em http://localhost:8000
- Teste do backend: 4 passed in 0.42s
- Frontend compilou com sucesso via Next.js build
- Frontend em desenvolvimento responde em http://localhost:3000

---

## 11) Próximo passo recomendado

Se quiser, a próxima etapa é:

1. subir um Redis/Celery real;
2. conectar banco PostgreSQL em produção;
3. configurar chaves do Google Places, PageSpeed e Claude;
4. publicar o frontend e o backend em uma VPS ou plataforma de hospedagem.

---

## Licença

Projeto interno / corporativo. Ajustar conforme a política da empresa e do cliente.
