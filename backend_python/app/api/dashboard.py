"""
Router /api/dashboard — Estatísticas globais para o painel.
Porta fiel das rotas do backend Node.js (routes/dashboard.js).
"""
import logging
from datetime import datetime, date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Campaign, Lead, Diagnostic, ApiCallLog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", summary="Estatísticas globais do painel")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    GET /api/dashboard/stats
    Retorna métricas consolidadas: leads, campanhas, diagnósticos, distribuição de prioridades
    e consumo das APIs gratuitas (Google Places, PageSpeed, Claude).
    """
    # 1. Total de leads
    total_leads = db.query(func.count(Lead.id)).scalar() or 0

    # 2. Média DMS
    avg_dms_result = db.query(func.avg(Lead.dms)).filter(Lead.dms.isnot(None)).scalar()
    avg_dms = round(avg_dms_result) if avg_dms_result else 0

    # 3. Campanhas em processamento
    active_campaigns = (
        db.query(func.count(Campaign.id))
        .filter(Campaign.status == "processing")
        .scalar() or 0
    )

    # 4. Diagnósticos concluídos
    total_diagnostics = (
        db.query(func.count(Diagnostic.id))
        .filter(Diagnostic.diagnostic_status == "completed")
        .scalar() or 0
    )

    # 5. Distribuição de prioridades
    priority_counts = (
        db.query(Lead.priority, func.count(Lead.id))
        .group_by(Lead.priority)
        .all()
    )
    priority_map = {"A": 0, "B": 0, "C": 0}
    for priority, count in priority_counts:
        if priority in priority_map:
            priority_map[priority] = count

    # 6. Consumo de APIs (mês atual para Places, dia atual para PageSpeed/Claude)
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    places_usage = (
        db.query(func.count(ApiCallLog.id))
        .filter(
            ApiCallLog.provider == "google_places",
            ApiCallLog.success == 1,
            ApiCallLog.created_at >= month_start,
        )
        .scalar() or 0
    )

    pagespeed_usage = (
        db.query(func.count(ApiCallLog.id))
        .filter(
            ApiCallLog.provider == "pagespeed",
            ApiCallLog.success == 1,
            ApiCallLog.created_at >= today_start,
        )
        .scalar() or 0
    )

    claude_usage = (
        db.query(func.count(ApiCallLog.id))
        .filter(
            ApiCallLog.provider == "claude",
            ApiCallLog.success == 1,
            ApiCallLog.created_at >= today_start,
        )
        .scalar() or 0
    )

    return {
        "success": True,
        "data": {
            "totalLeads": total_leads,
            "avgDms": avg_dms,
            "activeCampaigns": active_campaigns,
            "totalDiagnostics": total_diagnostics,
            "priorityDistribution": [
                {"name": "Prioridade A", "value": priority_map["A"], "color": "#22C55E"},
                {"name": "Prioridade B", "value": priority_map["B"], "color": "#F59E0B"},
                {"name": "Prioridade C", "value": priority_map["C"], "color": "#EF4444"},
            ],
            "apiUsage": {
                "apify": {
                    "used": places_usage,
                    "limit": 10000,
                    "unit": "pesquisas",
                },
                "gemini": {
                    "used": claude_usage,
                    "limit": 1500,
                    "unit": "requisições",
                },
                "pagespeed": {
                    "used": pagespeed_usage,
                    "limit": 25000,
                    "unit": "auditorias",
                },
            },
        },
    }
