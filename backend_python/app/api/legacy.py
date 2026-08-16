"""
Rotas legadas do motor de automação (busca de leads, triagem, diagnóstico e geração de site).
Mantidas para compatibilidade com o script run_demo_pipeline.py.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.core.config import settings
from app.models.lead import LeadResult, LeadSearchParams
from app.models.triage import FullTriageReport
from app.models.diagnosis import DiagnosisResult, StitchPromptResult
from app.models.site import GeneratedSiteResult, SiteGenerationRequest

from app.services.lead_service import LeadService
from app.services.triage_service import TriageService
from app.services.diagnosis_service import DiagnosisService
from app.services.site_service import SiteService

_lead_service = LeadService()
_triage_service = TriageService()
_diagnosis_service = DiagnosisService()
_site_service = SiteService()

_legacy = APIRouter(tags=["Motor de Automação (Legacy)"])


@_legacy.get("/leads/search", response_model=List[LeadResult])
async def search_leads_route(
    keyword: str = Query(...),
    location: str = Query(...),
    max_results: int = Query(20, ge=1, le=60),
):
    try:
        return await _lead_service.find_leads(keyword=keyword, location=location, max_results=max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@_legacy.post("/triage/run", response_model=FullTriageReport)
async def run_triage_route(lead: LeadResult):
    try:
        return await _triage_service.execute_triage(lead)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@_legacy.post("/diagnosis/generate")
async def generate_diagnosis_route(report: FullTriageReport):
    try:
        diagnosis, stitch_prompt = await _diagnosis_service.run_diagnosis_and_prompt(report)
        return {"diagnosis": diagnosis, "stitch_prompt": stitch_prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@_legacy.post("/site/generate", response_model=GeneratedSiteResult)
async def generate_site_route(req: SiteGenerationRequest):
    try:
        return await _site_service.generate_site_for_lead(req.lead_name, req.stitch_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
