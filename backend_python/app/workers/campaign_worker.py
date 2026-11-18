"""
Campaign Worker — Processa uma campanha de prospecção de forma assíncrona.
Busca leads no provider configurado e persiste apenas os dados básicos de cada empresa.
"""
import uuid
import logging
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Campaign, Lead, ApiCallLog
from app.services.lead_service import LeadService

logger = logging.getLogger(__name__)


async def process_campaign(campaign_id: str, niche: str, location: str, db: Session):
    """
    Busca leads no provider configurado, persiste seus dados básicos e atualiza o status.
    """
    logger.info(f"🔄 Iniciando processamento da campanha {campaign_id} — {niche} em {location}")

    try:
        # 1. Busca leads usando o LeadService configurado
        lead_service = LeadService()
        leads_found = await lead_service.find_leads(keyword=niche, location=location)
        
        provider_name = "apify" if settings.LEAD_PROVIDER == "apify" else "google_places"

        # Registra chamada ao log de API
        _log_api_call(db, provider_name, "search", "/places:searchText" if provider_name == "google_places" else "/acts/compass~crawler-google-places/runs", 200, True)

        logger.info(f"   📍 {len(leads_found)} leads encontrados via {provider_name}")

        # 2. Persiste os dados básicos de cada lead
        processed_count = 0
        for index, place_lead in enumerate(leads_found):
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign or campaign.status == "cancelled":
                logger.info(f"Campanha {campaign_id} interrompida pelo usuário.")
                return

            # Evita duplicar lead já existente nesta campanha ao reativar
            existing_lead = db.query(Lead).filter(
                Lead.campaign_id == campaign_id,
                Lead.name == place_lead.name
            ).first()
            if existing_lead:
                logger.info(f"   ⏩ Lead '{place_lead.name}' já cadastrado nesta campanha. Pulando...")
                processed_count += 1
                continue

            try:
                lead_data = _process_single_lead(
                    place_lead,
                    campaign_id,
                    provider_name,
                    campaign.tenant_id,
                )
                db.add(lead_data)
                db.commit()
                processed_count += 1
                logger.info(
                    f"   ✅ [{index + 1}/{len(leads_found)}] {place_lead.name}"
                )
            except Exception as lead_err:
                logger.error(f"   ⚠️ Erro ao processar lead '{place_lead.name}': {lead_err}")
                db.rollback()
                # Continua processando os outros leads mesmo se um falhar

        # 3. Marca campanha como concluída e consolida total real de leads no banco
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign and campaign.status == "processing":
            total_in_db = db.query(func.count(Lead.id)).filter(Lead.campaign_id == campaign_id).scalar() or 0
            campaign.status = "completed"
            campaign.total_leads = total_in_db
            campaign.updated_at = datetime.utcnow()
            db.commit()

        logger.info(f"🎉 Campanha {campaign_id} concluída! {processed_count} leads processados.")

    except Exception as error:
        logger.error(f"❌ Erro fatal ao processar campanha {campaign_id}: {error}")
        db.rollback()

        # Marca campanha como falha
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                campaign.status = "failed"
                campaign.error_message = str(error)
                campaign.updated_at = datetime.utcnow()
                db.commit()
        except Exception as update_err:
            logger.error(f"Falha ao atualizar status da campanha: {update_err}")


def _process_single_lead(
    place_lead,
    campaign_id: str,
    provider_name: str,
    tenant_id: str = "g_system",
) -> Lead:
    """Cria um lead com nome, endereço e avaliação do provider de busca."""
    address = place_lead.formatted_address or ""
    city = location_from_address(address)

    return Lead(
        id=str(uuid.uuid4()),
        campaign_id=campaign_id,
        tenant_id=tenant_id,
        name=place_lead.name,
        address=address,
        city=city,
        google_rating=place_lead.rating,
        google_reviews_count=place_lead.user_rating_count or 0,
        commercial_status="new",
        source_provider=provider_name,
        created_at=datetime.utcnow(),
    )


def _log_api_call(db: Session, provider: str, service_type: str, endpoint: str, status_code: int, success: bool):
    """Registra uma chamada de API no log para controle de cotas."""
    try:
        log = ApiCallLog(
            id=str(uuid.uuid4()),
            provider=provider,
            service_type=service_type,
            endpoint=endpoint,
            status_code=status_code,
            success=1 if success else 0,
            created_at=datetime.utcnow(),
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()  # Não deixa erro de log travar o processamento principal


def location_from_address(address: str) -> str:
    """Extrai a cidade a partir do endereço completo do Google Places."""
    parts = address.split(",")
    if len(parts) >= 2:
        return parts[-2].strip().split(" - ")[-1].strip()
    return address


