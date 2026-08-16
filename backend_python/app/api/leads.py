"""
Router /api/campaigns/:campaignId/leads e /api/leads — Gerenciamento de leads.
Porta fiel das rotas do backend Node.js (routes/leads.js) com exportação CSV.
"""
import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Campaign, Lead, Diagnostic

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Leads"])

ALLOWED_SORT_FIELDS = {
    "dms", "cos", "google_rating", "name", "priority",
    "google_reviews_count", "pagespeed_score", "created_at"
}


def _lead_to_dict(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "campaign_id": lead.campaign_id,
        "name": lead.name,
        "category": lead.category,
        "phone": lead.phone,
        "website": lead.website,
        "address": lead.address,
        "city": lead.city,
        "image_url": lead.image_url,
        "google_rating": lead.google_rating,
        "google_reviews_count": lead.google_reviews_count,
        "has_website": lead.has_website,
        "pagespeed_score": lead.pagespeed_score,
        "lcp_ms": lead.lcp_ms,
        "inp_ms": lead.inp_ms,
        "cls": lead.cls,
        "seo_score": lead.seo_score,
        "has_instagram": lead.has_instagram,
        "instagram_url": lead.instagram_url,
        "has_facebook": lead.has_facebook,
        "has_linkedin": lead.has_linkedin,
        "social_last_post_days": lead.social_last_post_days,
        "dms": lead.dms,
        "cos": lead.cos,
        "priority": lead.priority,
        "commercial_status": lead.commercial_status,
        "source_provider": lead.source_provider,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }


def _diagnostic_to_dict(d: Diagnostic) -> dict:
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


# ── Rotas ─────────────────────────────────────────────────────────────────────

@router.get("/api/campaigns/{campaign_id}/leads", summary="Lista leads de uma campanha")
def list_leads(
    campaign_id: str,
    priority: Optional[str] = Query(None, description="Filtrar por prioridade A, B ou C"),
    search: Optional[str] = Query(None, description="Busca parcial pelo nome"),
    sort_by: Optional[str] = Query("cos", description="Campo de ordenação"),
    sort_order: Optional[str] = Query("DESC", description="ASC ou DESC"),
    db: Session = Depends(get_db),
):
    """GET /api/campaigns/:campaignId/leads — Lista leads com filtros e ordenação."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Campanha não encontrada"})

    query = db.query(Lead).filter(Lead.campaign_id == campaign_id)

    if priority:
        query = query.filter(Lead.priority == priority.upper())

    if search:
        query = query.filter(Lead.name.ilike(f"%{search}%"))

    sort_field = sort_by if sort_by in ALLOWED_SORT_FIELDS else "cos"
    sort_col = getattr(Lead, sort_field, Lead.cos)
    if sort_order and sort_order.upper() == "ASC":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    leads = query.all()
    return {"data": [_lead_to_dict(l) for l in leads], "total": len(leads)}


@router.get("/api/leads/{lead_id}", summary="Detalhes completos de um lead")
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    """GET /api/leads/:id — Retorna detalhes do lead com diagnóstico, se existir."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Lead não encontrado"})

    diagnostic = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    data = _lead_to_dict(lead)
    data["diagnostic"] = _diagnostic_to_dict(diagnostic) if diagnostic else None
    return {"data": data}


@router.get("/api/campaigns/{campaign_id}/leads/export", summary="Exporta leads em CSV")
def export_leads_csv(campaign_id: str, db: Session = Depends(get_db)):
    """GET /api/campaigns/:campaignId/leads/export — Gera arquivo CSV dos leads."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Campanha não encontrada"})

    leads = db.query(Lead).filter(Lead.campaign_id == campaign_id).order_by(Lead.cos.desc()).all()

    headers = [
        "Nome", "Categoria", "Telefone", "Website", "Endereço", "Cidade",
        "Rating Google", "Avaliações Google", "Tem Site",
        "PageSpeed", "LCP (ms)", "INP (ms)", "CLS",
        "Instagram", "Facebook", "Último Post (dias)",
        "DMS", "COS", "Prioridade",
    ]

    def _q(val):
        return f'"{str(val or "").replace(chr(34), chr(34)+chr(34))}"'

    rows = []
    for lead in leads:
        rows.append([
            _q(lead.name), _q(lead.category), _q(lead.phone), _q(lead.website),
            _q(lead.address), _q(lead.city),
            lead.google_rating or "", lead.google_reviews_count or 0,
            "Sim" if lead.has_website else "Não",
            lead.pagespeed_score or "", lead.lcp_ms or "", lead.inp_ms or "", lead.cls or "",
            "Sim" if lead.has_instagram else "Não",
            "Sim" if lead.has_facebook else "Não",
            lead.social_last_post_days if lead.social_last_post_days is not None else "",
            lead.dms, lead.cos, lead.priority,
        ])

    # BOM UTF-8 para compatibilidade com Excel
    csv_lines = [",".join(headers)] + [",".join(str(v) for v in row) for row in rows]
    csv_content = "\ufeff" + "\n".join(csv_lines)

    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=leads_{campaign_id}.csv"},
    )
