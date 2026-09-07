# Automação GP

Projeto de prospecção e diagnóstico digital com frontend em Next.js e backend principal migrado para Python/FastAPI.

## Visão geral

- Frontend: Next.js + React + Tailwind
- Backend principal: FastAPI + SQLAlchemy + SQLite em desenvolvimento
- Backend legado: Node.js/Express mantido apenas como referência histórica
- APIs externas: Google Places, PageSpeed, Meta Graph/Instagram, Claude/Gemini, Google Stitch
- Banco local em desenvolvimento: SQLite
- Produção/integração futura: Redis/Celery e PostgreSQL

Estrutura principal:

```text
automacao-de-diagnostico/
├── backend/                     # legado Node.js (referência histórica)
├── backend_python/              # backend principal em Python/FastAPI
│   ├── app/
│   ├── scripts/
│   ├── tests/
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   └── Dockerfile
├── docs/                        # documentação da arquitetura e integrações
├── frontend/                    # painel administrativo em Next.js
├── renata-flora-landing/
├── mota-tobias-landing/
├── package-lock.json
├── refactor.js
├── README.md
└── .gitignore
```

---

## Como rodar o projeto localmente

### 1) Backend Python (principal)

```bash
cd backend_python
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
pip install pytest pytest-asyncio
```

Crie o arquivo de ambiente a partir do exemplo:

```bash
copy .env.example .env
```

O mínimo recomendado é:

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

Inicie o backend:

```bash
cd backend_python
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/api/health

### 2) Frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Acesse:

- Painel: http://localhost:3000

### 3) Landing pages (opcional)

```bash
cd mota-tobias-landing
npm install
npm run dev
```

ou

```bash
cd renata-flora-landing
npm install
npm run dev
```

---

## Requisitos

- Node.js 18+
- npm 9+
- Python 3.11+
- pip
- Git
- Redis opcional para workers/filas

---

## Variáveis do frontend

O frontend usa a API Python na porta 8000.

`NEXT_PUBLIC_API_URL` é lida durante o build do Next.js e fica embutida no bundle do navegador. Em produção, configure a variável antes de executar `npm run build`; alterar somente o ambiente do container depois do build não altera a URL já compilada.

Arquivo esperado em [frontend/.env.local](frontend/.env.local):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## Validação do projeto

### Testes do backend

```bash
cd backend_python
python -m pytest -q
```

Resultado verificado:

```text
4 passed in 0.42s
```

### Build do frontend

```bash
cd frontend
npm run build
```

Resultado verificado: compilação bem-sucedida no Next.js.

---

## Endpoints principais

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

Também existem rotas legadas mantidas para compatibilidade com a automação antiga.

---

## Solução de problemas comuns

### Erro de importação do SQLAlchemy

```bash
cd backend_python
pip install -r requirements.txt
```

### Porta 8000 ocupada

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Se a porta estiver ocupada, libere o processo anterior ou use outra porta:

```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend não encontra o backend

Em desenvolvimento, verifique [frontend/.env.local](frontend/.env.local) e confirme:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Em uma imagem Docker, passe a variável para a etapa de build:

```bash
docker build --build-arg NEXT_PUBLIC_API_URL=https://api.seudominio.com.br/api -t automacao-frontend frontend
```

### Teste assíncrono coletado pelo pytest

Se aparecer erro de `async def functions are not natively supported`, execute o utilitário manualmente:

```bash
cd backend_python
python scripts/test_google_places.py
```

---

## Observações importantes

- A stack ativa do projeto é Python + FastAPI + Next.js.
- A pasta [backend](backend) continua como referência histórica do Node.js e pode ser arquivada ou removida após a validação da stack principal.
- Sem chaves externas preenchidas, o sistema continua funcionando em modo local e fallback.

---

## Próximo passo recomendado

1. Configurar Redis/Celery para filas reais
2. Conectar banco PostgreSQL em produção
3. Preencher chaves do Google Places, PageSpeed e Claude
4. Publicar frontend + backend em VPS ou plataforma cloud

---

## Licença

Projeto interno / corporativo. Ajustar conforme a política da empresa e do cliente.
