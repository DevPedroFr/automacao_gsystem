"""
Router /api/leads/:leadId/diagnostic — Geração e consulta de diagnósticos via Claude AI.
Porta fiel das rotas do backend Node.js (routes/diagnostics.js).
"""
import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Lead, Diagnostic
from app.integrations.claude_ai import ClaudeAIIntegration
from app.integrations.gemini_ai import GeminiAIIntegration
from app.models.triage import FullTriageReport
from app.models.lead import LeadResult

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Diagnósticos"])


def _diag_to_dict(d: Diagnostic) -> dict:
    return {
        "id": d.id,
        "lead_id": d.lead_id,
        "observed_facts": d.observed_facts,
        "inferences": d.inferences,
        "recommendations": d.recommendations,
        "email_draft": d.email_draft,
        "whatsapp_draft": d.whatsapp_draft,
        "instagram_draft": d.instagram_draft,
        "stitch_prompt": d.stitch_prompt,
        "diagnostic_status": d.diagnostic_status,
        "error_message": d.error_message,
        "generated_at": d.generated_at.isoformat() if d.generated_at else None,
    }


@router.post("/api/leads/{lead_id}/diagnostic", status_code=201, summary="Gera diagnóstico de um lead via Claude AI")
async def generate_diagnostic(lead_id: str, db: Session = Depends(get_db)):
    """
    POST /api/leads/:leadId/diagnostic
    Gera o diagnóstico inteligente do lead usando Claude AI (ou heurística local se sem chave).
    Se já existir diagnóstico concluído, retorna 409.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Lead não encontrado"})

    existing = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    if existing:
        if existing.diagnostic_status == "ai_validation_failed" or not existing.stitch_prompt:
            db.delete(existing)
            db.commit()
        else:
            raise HTTPException(
                status_code=409,
                detail={"error": "already_exists", "message": "Diagnóstico já gerado. Use GET para consultá-lo."},
            )

    lead_result = LeadResult(
        place_id=lead.id,
        name=lead.name,
        formatted_address=lead.address or lead.city or "",
        national_phone_number=lead.phone,
        website_uri=lead.website,
        rating=lead.google_rating,
        user_rating_count=lead.google_reviews_count,
    )

    try:
        from app.services.diagnosis_service import DiagnosisService
        from app.models.triage import FullTriageReport, PageSpeedResult, DomainSecurityResult, InstagramProfileResult

        pagespeed = PageSpeedResult(
            url=lead.website or "",
            performance_score=lead.pagespeed_score,
            seo_score=lead.seo_score,
            mobile_friendly=True,
        )
        security = DomainSecurityResult(
            domain=lead.website or "",
            dns_resolved=bool(lead.website),
            ssl_valid=bool(lead.website),
        )
        
        # Extract handle from URL if possible
        ig_handle = lead.name
        if lead.instagram_url:
            parts = lead.instagram_url.split("instagram.com/")
            if len(parts) > 1:
                ig_handle = parts[1].split("/")[0].strip()
        
        instagram = InstagramProfileResult(
            handle=ig_handle,
            is_business_account=bool(lead.has_instagram),
            followers_count=None,
            provider_used="db",
        )

        report = FullTriageReport(
            lead=lead_result,
            pagespeed=pagespeed,
            security=security,
            instagram=instagram,
            needs_new_website=not bool(lead.website) or (lead.pagespeed_score or 100) < 50,
        )

        if settings.AI_PROVIDER == "gemini":
            ai_client = GeminiAIIntegration()
        else:
            ai_client = ClaudeAIIntegration()
            
        diag_service = DiagnosisService(llm=ai_client)
        diagnosis_res, stitch_prompt_res = await diag_service.run_diagnosis_and_prompt(report)

        diag_id = str(uuid.uuid4())
        diagnostic = Diagnostic(
            id=diag_id,
            lead_id=lead_id,
            observed_facts=diagnosis_res.overall_summary,
            recommendations="\n".join(
                f"[{r.severity}] {r.category}: {r.finding}" for r in diagnosis_res.recommendations
            ) if diagnosis_res.recommendations else None,
            email_draft=diagnosis_res.email_draft,
            whatsapp_draft=diagnosis_res.whatsapp_draft,
            instagram_draft=diagnosis_res.instagram_draft,
            stitch_prompt=stitch_prompt_res.stitch_prompt if stitch_prompt_res else None,
            diagnostic_status="completed",
            generated_at=datetime.utcnow(),
        )
        db.add(diagnostic)
        db.commit()
        db.refresh(diagnostic)

        return {"data": _diag_to_dict(diagnostic)}

    except Exception as err:
        logger.error(f"Erro ao gerar diagnóstico para lead {lead_id}: {err}")
        diag_id = str(uuid.uuid4())
        diagnostic = Diagnostic(
            id=diag_id,
            lead_id=lead_id,
            diagnostic_status="ai_validation_failed",
            error_message=str(err),
            generated_at=datetime.utcnow(),
        )
        db.add(diagnostic)
        db.commit()
        raise HTTPException(status_code=500, detail={"error": "diagnosis_error", "message": str(err)})


@router.get("/api/leads/{lead_id}/diagnostic", summary="Consulta diagnóstico de um lead")
def get_diagnostic(lead_id: str, db: Session = Depends(get_db)):
    """GET /api/leads/:leadId/diagnostic — Retorna o diagnóstico existente."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Lead não encontrado"})

    diagnostic = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    if not diagnostic:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "Diagnóstico não gerado ainda. Use POST para gerar."},
        )
    return {"data": _diag_to_dict(diagnostic)}
