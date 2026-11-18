"""
Router /api/dashboard — Indicadores do CRM dentro do escopo do usuário autenticado.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, allowed_tenants, get_current_user
from app.db.database import get_db
from app.db.models import Lead

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", summary="Indicadores do CRM")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    status_counts = (
        db.query(Lead.commercial_status, func.count(Lead.id))
        .filter(
            Lead.in_crm.is_(True),
            Lead.tenant_id.in_(allowed_tenants(user)),
        )
        .group_by(Lead.commercial_status)
        .all()
    )
    counts = {status: count for status, count in status_counts}
    contacted = counts.get("contacted", 0)
    closed = counts.get("won", 0)

    return {
        "success": True,
        "data": {
            "crmStats": {
                "contactedCustomers": contacted,
                "interestedCustomers": counts.get("negotiation", 0),
                "closedCustomers": closed,
                "paidCustomers": counts.get("paid", 0),
                "conversionRate": round(closed / contacted * 100, 1) if contacted else 0,
            },
        },
    }
