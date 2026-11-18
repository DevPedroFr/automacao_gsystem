from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, allowed_tenants, get_current_user
from app.db.models import Campaign, Lead


def get_accessible_campaign(db: Session, campaign_id: str, user: AuthenticatedUser) -> Campaign:
    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.tenant_id.in_(allowed_tenants(user)),
        )
        .first()
    )
    if campaign is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "Campanha não encontrada"},
        )
    return campaign


def get_accessible_lead(db: Session, lead_id: str, user: AuthenticatedUser) -> Lead:
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.tenant_id.in_(allowed_tenants(user)),
        )
        .first()
    )
    if lead is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "Lead não encontrado"},
        )
    return lead


def require_directoria(user: AuthenticatedUser = Depends(get_current_user)):
    if user.access_level != "diretoria":
        raise HTTPException(
            status_code=403,
            detail={"error": "forbidden", "message": "Apenas a Diretoria pode acessar esta configuração."},
        )
