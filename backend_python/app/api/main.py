"""
FastAPI Application — Backend Unificado (Python)
Substitui completamente o backend Node.js anterior.
Porta: 8000 (configurável via .env)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db

# ── Routers ───────────────────────────────────────────────────────────────────
# Legado: rotas do motor de automação (busca, triagem, diagnóstico, stitch)
from app.api.legacy import _legacy as legacy_router
# Novos: rotas compatíveis com o frontend (campanhas, leads, dashboard, settings)
from app.api.campaigns import router as campaigns_router
from app.api.leads import router as leads_router
from app.api.dashboard import router as dashboard_router
from app.api.settings import router as settings_router
from app.api.diagnostics import router as diagnostics_router

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend unificado de Automação GP. "
        "Integra Google Places API, PageSpeed, SSL/DNS, Meta Graph (Instagram), "
        "Claude AI (Haiku) e Google Stitch para triagem e geração de sites."
    ),
    version="2.0.0",
    redirect_slashes=False,  # Evita redirect 307 que bloqueia CORS no browser
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup: inicializa banco de dados ────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(legacy_router)
app.include_router(campaigns_router)
app.include_router(leads_router)
app.include_router(dashboard_router)
app.include_router(settings_router)
app.include_router(diagnostics_router)

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": "2.0.0",
        "stages_configured": [
            "1. Lead Search (Google Places API New)",
            "2. Digital Triage (PageSpeed + SSL/DNS + Meta Instagram)",
            "3. Diagnosis (Claude AI Haiku)",
            "4. Stitch Prompt Generation (Claude AI)",
            "5. Site Generation (Google Stitch API)",
        ],
    }

@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
