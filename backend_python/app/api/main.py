from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from typing import List, Optional

from app.core.config import settings
from app.models.lead import LeadResult, LeadSearchParams
from app.models.triage import FullTriageReport
from app.models.diagnosis import DiagnosisResult, StitchPromptResult
from app.models.site import GeneratedSiteResult, SiteGenerationRequest

from app.services.lead_service import LeadService
from app.services.triage_service import TriageService
from app.services.diagnosis_service import DiagnosisService
from app.services.site_service import SiteService

app = FastAPI(
    title=settings.APP_NAME,
    description="API de Automação de Triagem e Geração de Sites com Google Places, PageSpeed, SSL, Meta Graph, Claude AI e Google Stitch.",
    version="1.0.0",
)

# Instantiate domain services
lead_service = LeadService()
triage_service = TriageService()
diagnosis_service = DiagnosisService()
site_service = SiteService()


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "stages_configured": [
            "1. Lead Search (Google Places API New)",
            "2. Digital Triage (Google PageSpeed + SSL/WHOIS + Meta Graph Instagram)",
            "3. Diagnosis & Recommendations (Anthropic Claude Haiku 4.5)",
            "4. Stitch Prompt Generation (Anthropic Claude)",
            "5. Site Generation (Google Stitch API)",
        ],
    }


@app.get("/leads/search", response_model=List[LeadResult], tags=["Etapa 1 - Busca de Leads"])
async def search_leads(
    keyword: str = Query(..., description="Palavra-chave ex: 'Clínica Odontológica'"),
    location: str = Query(..., description="Cidade/Localização ex: 'São Paulo, SP'"),
    max_results: int = Query(20, ge=1, le=60),
):
    """Etapa 1: Busca de leads no Google Places API (New) com filtro de SKUs essenciais."""
    try:
        return await lead_service.find_leads(keyword=keyword, location=location, max_results=max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/triage/run", response_model=FullTriageReport, tags=["Etapa 2 - Triagem Digital"])
async def run_triage(lead: LeadResult):
    """Etapa 2: Triagem completa de presença digital (PageSpeed, SSL/WHOIS e Instagram)."""
    try:
        return await triage_service.execute_triage(lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/diagnosis/generate", tags=["Etapa 3 & 4 - Diagnóstico e Prompt Stitch"])
async def generate_diagnosis(report: FullTriageReport):
    """Etapa 3 & 4: Geração de diagnóstico e prompt para o Stitch via Anthropic Claude (Haiku 4.5)."""
    try:
        diagnosis, stitch_prompt = await diagnosis_service.run_diagnosis_and_prompt(report)
        return {
            "diagnosis": diagnosis,
            "stitch_prompt": stitch_prompt,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/site/generate", response_model=GeneratedSiteResult, tags=["Etapa 5 - Geração do Site"])
async def generate_site(req: SiteGenerationRequest):
    """Etapa 5: Geração de site/UI HTML a partir do prompt via Google Stitch API."""
    try:
        return await site_service.generate_site_for_lead(req.lead_name, req.stitch_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
