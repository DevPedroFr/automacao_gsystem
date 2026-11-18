"""
Router /api/campaigns/:campaignId/leads e /api/leads — Gerenciamento de leads.
Porta fiel das rotas do backend Node.js (routes/leads.js) com exportação CSV.
"""
import io
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.access import get_accessible_campaign, get_accessible_lead
from app.core.auth import AuthenticatedUser, allowed_tenants, get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Campaign, CrmRecord, Lead, Diagnostic
from app.integrations.company_research import CompanyResearchError, CompanyResearchIntegration

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Leads"])
COMPANY_RESEARCH_CACHE_TTL = timedelta(hours=24)

ALLOWED_SORT_FIELDS = {
    "dms", "cos", "google_rating", "name", "priority",
    "google_reviews_count", "pagespeed_score", "created_at"
}


def _lead_to_dict(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "campaign_id": lead.campaign_id,
        "tenant_id": lead.tenant_id,
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
        "instagram_candidates": lead.instagram_candidates,
        "has_facebook": lead.has_facebook,
        "has_linkedin": lead.has_linkedin,
        "social_last_post_days": lead.social_last_post_days,
        "dms": lead.dms,
        "cos": lead.cos,
        "priority": lead.priority,
        "in_crm": lead.in_crm,
        "commercial_status": lead.commercial_status,
        "source_provider": lead.source_provider,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }


def _crm_record_to_dict(record: CrmRecord) -> dict:
    return {
        "id": record.id,
        "lead_id": record.lead_id,
        "record_type": record.record_type,
        "content": record.content,
        "previous_status": record.previous_status,
        "new_status": record.new_status,
        "created_by": record.created_by,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def _campaign_lead_to_dict(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "name": lead.name,
        "address": lead.address,
        "city": lead.city,
        "google_rating": lead.google_rating,
        "in_crm": lead.in_crm,
    }


def _diagnostic_to_dict(d: Diagnostic) -> dict:
    return {
        "id": d.id,
        "lead_id": d.lead_id,
        "observed_facts": d.observed_facts,
        "inferences": d.inferences,
        "recommendations": d.recommendations,
        # Estratégia de vendas
        "sales_approach": getattr(d, "sales_approach", None),
        "pain_points": getattr(d, "pain_points", None),
        "talking_points": getattr(d, "talking_points", None),
        "value_proposition": getattr(d, "value_proposition", None),
        # Rascunhos de mensagens
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
    sort_by: Optional[str] = Query("name", description="Campo de ordenação"),
    sort_order: Optional[str] = Query("ASC", description="ASC ou DESC"),
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """GET /api/campaigns/:campaignId/leads — Lista leads com filtros e ordenação."""
    get_accessible_campaign(db, campaign_id, user)

    query = db.query(Lead).filter(
        Lead.campaign_id == campaign_id,
        Lead.tenant_id.in_(allowed_tenants(user)),
    )

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
    return {"data": [_campaign_lead_to_dict(lead) for lead in leads], "total": len(leads)}


@router.get("/api/leads", summary="Lista leads adicionados ao CRM")
def list_all_leads(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
    tenant_id: Optional[str] = None,
):
    """GET /api/leads — Lista somente os leads adicionados manualmente ao CRM."""
    accessible_tenants = allowed_tenants(user)
    if tenant_id is not None:
        if tenant_id not in {"spy_car", "g_system"}:
            raise HTTPException(status_code=400, detail={"message": "Empresa inválida."})
        if tenant_id not in accessible_tenants:
            raise HTTPException(status_code=403, detail={"message": "Você não pode acessar o CRM desta empresa."})
        accessible_tenants = (tenant_id,)

    leads = (
        db.query(Lead)
        .filter(Lead.in_crm.is_(True), Lead.tenant_id.in_(accessible_tenants))
        .order_by(Lead.created_at.desc())
        .all()
    )
    last_records = {}
    if leads:
        last_records = dict(
            db.query(CrmRecord.lead_id, func.max(CrmRecord.created_at))
            .filter(CrmRecord.lead_id.in_([lead.id for lead in leads]))
            .group_by(CrmRecord.lead_id)
            .all()
        )

    data = []
    for lead in leads:
        lead_data = _lead_to_dict(lead)
        last_record_at = last_records.get(lead.id)
        lead_data["last_record_at"] = last_record_at.isoformat() if last_record_at else None
        data.append(lead_data)
    return {"data": data, "total": len(data)}


@router.get("/api/leads/{lead_id}/records", summary="Lista o histórico de registros de um lead")
def list_lead_records(
    lead_id: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    lead = get_accessible_lead(db, lead_id, user)
    records = (
        db.query(CrmRecord)
        .filter(CrmRecord.lead_id == lead.id)
        .order_by(CrmRecord.created_at.desc(), CrmRecord.id.desc())
        .all()
    )
    return {"data": [_crm_record_to_dict(record) for record in records], "total": len(records)}


class CrmRecordCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


@router.post("/api/leads/{lead_id}/records", summary="Adiciona uma nota ao histórico do lead")
def create_lead_record(
    lead_id: str,
    body: CrmRecordCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    lead = get_accessible_lead(db, lead_id, user)
    content = body.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail={"message": "O registro não pode ficar vazio."})

    record = CrmRecord(
        lead_id=lead.id,
        record_type="note",
        content=content,
        created_by=user.username,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"data": _crm_record_to_dict(record)}


@router.post("/api/leads/{lead_id}/crm", summary="Adiciona um lead ao CRM")
def add_lead_to_crm(
    lead_id: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """POST /api/leads/:id/crm — Inclui um lead coletado no CRM."""
    lead = get_accessible_lead(db, lead_id, user)

    if not lead.in_crm:
        lead.in_crm = True
        db.add(CrmRecord(
            lead_id=lead.id,
            record_type="crm_added",
            content="Lead adicionado ao CRM",
            created_by=user.username,
        ))
        db.commit()
        db.refresh(lead)

    return {"data": _lead_to_dict(lead), "message": "Lead adicionado ao CRM"}


class LeadStatusUpdate(BaseModel):
    status: str

@router.patch("/api/leads/{lead_id}/status", summary="Atualiza o status comercial de um lead")
def update_lead_status(
    lead_id: str,
    body: LeadStatusUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """PATCH /api/leads/:id/status — Atualiza commercial_status."""
    lead = get_accessible_lead(db, lead_id, user)

    valid_statuses = ["new", "contacted", "negotiation", "won", "paid", "lost"]
    if body.status not in valid_statuses:
        raise HTTPException(status_code=400, detail={"error": "invalid_status", "message": f"Status inválido. Permitidos: {valid_statuses}"})

    previous_status = lead.commercial_status or "new"
    lead.commercial_status = body.status
    if previous_status != body.status:
        db.add(CrmRecord(
            lead_id=lead.id,
            record_type="status_change",
            previous_status=previous_status,
            new_status=body.status,
            created_by=user.username,
        ))
    db.commit()
    db.refresh(lead)
    return {"data": _lead_to_dict(lead)}


@router.get("/api/leads/{lead_id}", summary="Detalhes completos de um lead")
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """GET /api/leads/:id — Retorna detalhes do lead com diagnóstico, se existir."""
    lead = get_accessible_lead(db, lead_id, user)

    diagnostic = None
    try:
        diagnostic = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    except Exception as e:
        logger.error(f"Erro ao buscar diagnóstico para o lead {lead_id}: {e}")
        db.rollback()

    data = _lead_to_dict(lead)
    data["diagnostic"] = _diagnostic_to_dict(diagnostic) if diagnostic else None
    return {"data": data}


@router.post("/api/leads/{lead_id}/research", summary="Busca dados públicos de uma empresa com Gemini")
async def research_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Pesquisa informações empresariais públicas e retorna dados com fontes."""
    lead = get_accessible_lead(db, lead_id, user)

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if lead.company_research_data and lead.company_research_updated_at:
        cache_age = now - lead.company_research_updated_at
        if cache_age < COMPANY_RESEARCH_CACHE_TTL:
            try:
                return {"data": json.loads(lead.company_research_data)}
            except json.JSONDecodeError as err:
                logger.error("Cache de pesquisa inválido para o lead %s", lead.id)
                raise HTTPException(
                    status_code=500,
                    detail={"error": "invalid_cache", "message": "Os dados de pesquisa armazenados estão inválidos."},
                ) from err

    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail={"error": "configuration_error", "message": "GEMINI_API_KEY não está configurada."},
        )

    try:
        result = await run_in_threadpool(
            CompanyResearchIntegration(settings.GEMINI_API_KEY).search_company,
            lead.name,
            lead.address or lead.city or "",
        )
    except CompanyResearchError as err:
        logger.error("Pesquisa Gemini falhou para o lead %s: %s", lead.id, err)
        raise HTTPException(
            status_code=err.status_code,
            detail={"error": "research_failed", "message": str(err)},
            headers={"Retry-After": str(err.retry_after_seconds)} if err.retry_after_seconds else None,
        ) from err

    lead.company_research_data = json.dumps(result, ensure_ascii=False)
    lead.company_research_updated_at = now
    db.commit()

    return {"data": result}



@router.get("/api/campaigns/{campaign_id}/leads/export", summary="Exporta leads em CSV")
def export_leads_csv(
    campaign_id: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """GET /api/campaigns/:campaignId/leads/export — Gera arquivo CSV dos leads."""
    get_accessible_campaign(db, campaign_id, user)

    leads = (
        db.query(Lead)
        .filter(
            Lead.campaign_id == campaign_id,
            Lead.tenant_id.in_(allowed_tenants(user)),
        )
        .order_by(Lead.name.asc())
        .all()
    )

    headers = ["Nome", "Endereço", "Avaliação Google"]

    def _q(val):
        return f'"{str(val or "").replace(chr(34), chr(34)+chr(34))}"'

    rows = []
    for lead in leads:
        rows.append([
            _q(lead.name), _q(lead.address), lead.google_rating if lead.google_rating is not None else "",
        ])

    # BOM UTF-8 para compatibilidade com Excel
    csv_lines = [",".join(headers)] + [",".join(str(v) for v in row) for row in rows]
    csv_content = "\ufeff" + "\n".join(csv_lines)

    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=leads_{campaign_id}.csv"},
    )


class InstagramSelection(BaseModel):
    handle: str

@router.post("/api/leads/{lead_id}/select-instagram", summary="Seleciona o Instagram correto para o lead")
def select_instagram(
    lead_id: str,
    body: InstagramSelection,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Seleciona o Instagram correto dentre os candidatos e atualiza o lead."""
    lead = get_accessible_lead(db, lead_id, user)

    # Atualiza o lead com a seleção
    lead.has_instagram = 1
    lead.instagram_url = f"https://instagram.com/{body.handle}"
    # Opcionalmente podemos limpar os candidatos
    lead.instagram_candidates = None
    
    # Recalcula DMS e COS
    from app.services.score_service import calculate_dms, calculate_cos, get_priority
    lead_dict = {
        "google_rating": lead.google_rating,
        "google_reviews_count": lead.google_reviews_count,
        "has_website": lead.has_website,
        "pagespeed_score": lead.pagespeed_score,
        "has_instagram": lead.has_instagram,
        "has_facebook": lead.has_facebook,
        "social_last_post_days": lead.social_last_post_days,
    }
    dms = calculate_dms(lead_dict)
    cos = calculate_cos(lead_dict, dms)
    priority = get_priority(cos)
    
    lead.dms = dms
    lead.cos = cos
    lead.priority = priority
    
    db.commit()
    db.refresh(lead)
    
    # Se já existir um diagnóstico, invalida para que o frontend/usuário regere
    diagnostic = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    if diagnostic:
        db.delete(diagnostic)
        db.commit()
        
    return {"data": _lead_to_dict(lead)}
