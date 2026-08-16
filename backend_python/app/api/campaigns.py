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
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Campaign, Lead

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

def _campaign_to_dict(c: Campaign) -> dict:
    return {
        "id": c.id,
        "niche": c.niche,
        "location": c.location,
        "status": c.status,
        "total_leads": c.total_leads,
        "error_message": c.error_message,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


# ── Rotas ─────────────────────────────────────────────────────────────────────

@router.get("/", summary="Lista todas as campanhas")
def list_campaigns(db: Session = Depends(get_db)):
    """GET /api/campaigns — Lista todas as campanhas, mais recente primeiro."""
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return {"data": [_campaign_to_dict(c) for c in campaigns]}


@router.get("/{campaign_id}", summary="Detalhes de uma campanha")
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """GET /api/campaigns/:id — Retorna detalhes de uma campanha."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Campanha não encontrada"})
    return {"data": _campaign_to_dict(campaign)}


@router.post("/", status_code=201, summary="Cria nova campanha e inicia processamento")
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
