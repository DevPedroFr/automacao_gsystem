# Automação GP - Backend Python (Integrações com APIs Externas & SOLID)

Estrutura de backend Python desenvolvida seguindo os princípios **SOLID** para conectar todas as APIs externas descritas na arquitetura da automação 24/7 (Google Places, PageSpeed, SSL/WHOIS, Meta Graph, Anthropic Claude AI e Google Stitch).

---

## 📐 Organização de Pastas (SOLID Architecture)

```
backend_python/
├── app/
│   ├── core/                           # Configurações globais e Abstrações Interfaces (DIP & ISP)
│   │   ├── config.py                   # Pydantic Settings para Variáveis de Ambiente e API Keys
│   │   ├── exceptions.py               # Exceções customizadas de integração e rate limit
│   │   └── interfaces/                 # Interfaces Abstratas (ABC) para cada etapa da automação
│   │       ├── lead_search.py          # LeadSearchProvider (Etapa 1)
│   │       ├── website_triage.py       # WebsitePerformanceChecker & DomainSecurityChecker (Etapa 2)
│   │       ├── social_triage.py        # SocialMediaChecker (Etapa 2)
│   │       ├── llm_service.py          # LLMService (Etapa 3 & Etapa 4)
│   │       └── site_generator.py       # SiteGenerator (Etapa 5)
│   │
│   ├── models/                         # DTOs e Schemas Pydantic
│   │   ├── lead.py                     # Modelo de buscas e resultados de Leads
│   │   ├── triage.py                   # Modelo de resultados da Triagem Digital
│   │   ├── diagnosis.py                # Modelo de diagnósticos e recomendações
│   │   └── site.py                     # Modelo de geração do site Stitch
│   │
│   ├── integrations/                   # Implementações Concretas das APIs (Single Responsibility)
│   │   ├── base.py                     # Cliente HTTP Base com httpx (retries, timeouts, exceptions)
│   │   ├── google_places.py            # [Etapa 1] Google Places API (New) (Text Search & Details)
│   │   ├── pagespeed.py                # [Etapa 2] Google PageSpeed Insights API
│   │   ├── domain_checker.py           # [Etapa 2] Verificação nativa Python (SSL, Socket, WHOIS, DNS)
│   │   ├── instagram.py                # [Etapa 2] Meta Graph API (Instagram Business) + RapidAPI Fallback
│   │   ├── claude_ai.py                # [Etapa 3 & 4] Anthropic Claude API (Modelo Haiku 4.5)
│   │   └── stitch.py                   # [Etapa 5] Google Stitch API / SDK Client
│   │
│   ├── services/                       # Camada de Serviços Orquestradores (Injeção de Dependências)
│   │   ├── lead_service.py             # Orquestra busca de leads
│   │   ├── triage_service.py           # Orquestra triagem concorrente
│   │   ├── diagnosis_service.py        # Orquestra diagnóstico e prompt do Stitch
│   │   └── site_service.py             # Orquestra chamada ao Stitch
│   │
│   ├── api/                            # FastAPI Application
│   │   └── main.py                     # Entrypoint e endpoints HTTP REST
│   │
│   └── workers/                        # Workers Celery e Tarefas Agendadas (Beat)
│       ├── celery_app.py               # Configuração do Celery + Broker Redis
│       └── tasks.py                    # Tarefas assíncronas e agendamento 24/7
│
├── .env.example                        # Template das chaves de API
├── Dockerfile                          # Container Docker para deploy no EasyPanel / VPS
└── requirements.txt                    # Dependências do projeto Python
```

---

## 🚀 Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
Copie `.env.example` para `.env` e adicione suas chaves de API:
```bash
cp .env.example .env
```

### 3. Rodar a API FastAPI localmente
```bash
uvicorn app.api.main:app --reload --port 8000
```
Acesse a documentação interativa OpenAPI em: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Rodar o Worker Celery e Agendador Beat
```bash
# Executar worker de filas assíncronas:
celery -A app.workers.celery_app worker --loglevel=info

# Executar agendador de buscas periódicas (Celery Beat):
celery -A app.workers.celery_app beat --loglevel=info
```
