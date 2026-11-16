"""
Router /api/campaigns — Gerenciamento de campanhas de prospecção.
Porta fiel das rotas do backend Node.js (routes/campaigns.js).
"""
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import func, case, or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Campaign, Lead, Diagnostic

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/campaigns", tags=["Campanhas"])


# ── Schemas Pydantic ──────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    niche: str
    location: str
    minRating: Optional[float] = None
    status: Optional[str] = None
    negativeKeywords: Optional[list[str]] = None


# ── Helper ────────────────────────────────────────────────────────────────────

def _campaign_to_dict(c: Campaign, stats: dict = None) -> dict:
    s = stats or {}
    total_leads = s.get("total_leads", c.total_leads or 0)
    return {
        "id": c.id,
        "niche": c.niche,
        "location": c.location,
        "status": c.status,
        "total_leads": total_leads,
        "error_message": c.error_message,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        # Estatísticas enriquecidas úteis:
        "priority_a": s.get("priority_a", 0),
        "priority_b": s.get("priority_b", 0),
        "priority_c": s.get("priority_c", 0),
        "without_website": s.get("without_website", 0),
        "avg_dms": s.get("avg_dms", 0),
        "avg_cos": s.get("avg_cos", 0),
        "diagnostics_count": s.get("diagnostics_count", 0),
    }


# ── Rotas ─────────────────────────────────────────────────────────────────────

@router.get("", summary="Lista todas as campanhas com estatísticas enriquecidas")
def list_campaigns(db: Session = Depends(get_db)):
    """GET /api/campaigns — Lista todas as campanhas com métricas consolidadas, mais recente primeiro."""
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    if not campaigns:
        return {"data": []}

    # Agregação rápida para todas as campanhas
    leads_stats = (
        db.query(
            Lead.campaign_id,
            func.count(Lead.id).label("total_leads"),
            func.sum(case((Lead.priority == "A", 1), else_=0)).label("priority_a"),
            func.sum(case((Lead.priority == "B", 1), else_=0)).label("priority_b"),
            func.sum(case((Lead.priority == "C", 1), else_=0)).label("priority_c"),
            func.sum(case((or_(Lead.has_website == 0, Lead.website.is_(None)), 1), else_=0)).label("without_website"),
            func.round(func.avg(Lead.dms), 1).label("avg_dms"),
            func.round(func.avg(Lead.cos), 1).label("avg_cos"),
        )
        .group_by(Lead.campaign_id)
        .all()
    )

    stats_map = {}
    for row in leads_stats:
        cid, total_leads, p_a, p_b, p_c, without_web, dms, cos = row
        stats_map[cid] = {
            "total_leads": total_leads or 0,
            "priority_a": int(p_a or 0),
            "priority_b": int(p_b or 0),
            "priority_c": int(p_c or 0),
            "without_website": int(without_web or 0),
            "avg_dms": float(dms or 0),
            "avg_cos": float(cos or 0),
            "diagnostics_count": 0,
        }

    # Contagem de diagnósticos gerados por campanha
    diag_rows = (
        db.query(Lead.campaign_id, func.count(Diagnostic.id))
        .join(Diagnostic, Diagnostic.lead_id == Lead.id)
        .group_by(Lead.campaign_id)
        .all()
    )
    for cid, diag_count in diag_rows:
        if cid in stats_map:
            stats_map[cid]["diagnostics_count"] = int(diag_count or 0)

    result = []
    for c in campaigns:
        st = stats_map.get(c.id, {})
        result.append(_campaign_to_dict(c, st))

    return {"data": result}


@router.get("/{campaign_id}", summary="Detalhes de uma campanha com estatísticas")
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """GET /api/campaigns/:id — Retorna detalhes de uma campanha com métricas consolidadas."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Campanha não encontrada"})

    stats_row = (
        db.query(
            func.count(Lead.id).label("total_leads"),
            func.sum(case((Lead.priority == "A", 1), else_=0)).label("priority_a"),
            func.sum(case((Lead.priority == "B", 1), else_=0)).label("priority_b"),
            func.sum(case((Lead.priority == "C", 1), else_=0)).label("priority_c"),
            func.sum(case((or_(Lead.has_website == 0, Lead.website.is_(None)), 1), else_=0)).label("without_website"),
            func.round(func.avg(Lead.dms), 1).label("avg_dms"),
            func.round(func.avg(Lead.cos), 1).label("avg_cos"),
        )
        .filter(Lead.campaign_id == campaign_id)
        .first()
    )

    diag_count = (
        db.query(func.count(Diagnostic.id))
        .join(Lead, Diagnostic.lead_id == Lead.id)
        .filter(Lead.campaign_id == campaign_id)
        .scalar() or 0
    )

    st = {}
    if stats_row:
        total_leads, p_a, p_b, p_c, without_web, dms, cos = stats_row
        st = {
            "total_leads": total_leads or 0,
            "priority_a": int(p_a or 0),
            "priority_b": int(p_b or 0),
            "priority_c": int(p_c or 0),
            "without_website": int(without_web or 0),
            "avg_dms": float(dms or 0),
            "avg_cos": float(cos or 0),
            "diagnostics_count": int(diag_count or 0),
        }

    return {"data": _campaign_to_dict(campaign, st)}


@router.post("", status_code=201, summary="Cria nova campanha e inicia processamento")
async def create_campaign(
    body: CampaignCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    POST /api/campaigns — Cria uma nova campanha e dispara o worker em background.
    O worker buscará leads reais via Google Places API e executará a triagem completa.
    """
    if not body.niche or not body.location:
        raise HTTPException(
            status_code=400,
            detail={"error": "validation_error", "message": 'Os campos "niche" e "location" são obrigatórios'},
        )

    campaign_id = str(uuid.uuid4())
    campaign = Campaign(
        id=campaign_id,
        niche=body.niche,
        location=body.location,
        status="processing",
        total_leads=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    # Dispara processamento assíncrono sem bloquear a resposta HTTP
    background_tasks.add_task(
        _run_campaign_worker,
        campaign_id=campaign_id,
        niche=body.niche,
        location=body.location,
    )

    logger.info(f"🚀 Campanha {campaign_id} criada. Worker iniciado em background.")
    return {"data": _campaign_to_dict(campaign)}


@router.post("/{campaign_id}/cancel", summary="Cancela o processamento de uma campanha")
def cancel_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Campanha não encontrada"})
    if campaign.status != "processing":
        raise HTTPException(
            status_code=409,
            detail={"error": "invalid_status", "message": "Somente campanhas em processamento podem ser paradas"},
        )

    campaign.status = "cancelled"
    campaign.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign)
    return {"data": _campaign_to_dict(campaign), "message": "Campanha interrompida"}


@router.post("/{campaign_id}/activate", summary="Ativa ou reinicia o processamento de uma campanha")
@router.post("/{campaign_id}/restart", include_in_schema=False)
def activate_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    POST /api/campaigns/:id/activate — Ativa ou reinicia a execução de busca e triagem de leads.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Campanha não encontrada"})

    # Se já está processando, retorna sem duplicar
    if campaign.status == "processing":
        return {"data": _campaign_to_dict(campaign), "message": "Campanha já está em processamento"}

    campaign.status = "processing"
    campaign.error_message = None
    campaign.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign)

    background_tasks.add_task(
        _run_campaign_worker,
        campaign_id=campaign.id,
        niche=campaign.niche,
        location=campaign.location,
    )

    logger.info(f"⚡ Campanha {campaign.id} ativada com sucesso. Worker iniciado em background.")
    return {"data": _campaign_to_dict(campaign), "message": "Campanha ativada com sucesso!"}


@router.delete("/{campaign_id}", summary="Exclui uma campanha e seus leads")
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """DELETE /api/campaigns/:id — Remove a campanha e limpa todos os leads e diagnósticos vinculados."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Campanha não encontrada"})

    db.delete(campaign)
    db.commit()
    logger.info(f"🗑️ Campanha {campaign_id} excluída com sucesso.")
    return {"data": {"id": campaign_id}, "message": "Campanha excluída com sucesso"}


@router.get("/{campaign_id}/stats", summary="Estatísticas detalhadas de uma campanha")
def get_campaign_stats(campaign_id: str, db: Session = Depends(get_db)):
    """GET /api/campaigns/:id/stats — Retorna métricas e distribuição de prioridades."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Campanha não encontrada"})

    total_leads = db.query(func.count(Lead.id)).filter(Lead.campaign_id == campaign_id).scalar() or 0

    priority_counts = (
        db.query(Lead.priority, func.count(Lead.id))
        .filter(Lead.campaign_id == campaign_id)
        .group_by(Lead.priority)
        .all()
    )
    priority_map = {"A": 0, "B": 0, "C": 0}
    for priority, count in priority_counts:
        if priority in priority_map:
            priority_map[priority] = count

    averages = (
        db.query(func.round(func.avg(Lead.dms), 1), func.round(func.avg(Lead.cos), 1))
        .filter(Lead.campaign_id == campaign_id)
        .first()
    )

    return {
        "data": {
            "campaign_id": campaign_id,
            "status": campaign.status,
            "total_leads": total_leads,
            "priority_a": priority_map["A"],
            "priority_b": priority_map["B"],
            "priority_c": priority_map["C"],
            "avg_dms": averages[0] or 0,
            "avg_cos": averages[1] or 0,
        }
    }


async def _run_campaign_worker(campaign_id: str, niche: str, location: str):
    """Wrapper que cria uma sessão de banco própria para o background task."""
    from app.db.database import SessionLocal
    from app.workers.campaign_worker import process_campaign

    db = SessionLocal()
    try:
        await process_campaign(campaign_id, niche, location, db)
    except Exception as e:
        logger.error(f"Erro no campaign worker: {e}")
    finally:
        db.close()
