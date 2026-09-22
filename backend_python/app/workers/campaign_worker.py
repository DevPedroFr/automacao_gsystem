"""
Campaign Worker — Processa uma campanha de prospecção de forma assíncrona.
Busca leads reais via Google Places API, executa triagem digital completa,
calcula scores DMS/COS e persiste tudo no banco de dados local.
"""
import asyncio
import uuid
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Campaign, Lead, ApiCallLog
from app.models.lead import LeadSearchParams
from app.services.lead_service import LeadService
from app.integrations.pagespeed import PageSpeedIntegration
from app.integrations.domain_checker import DomainSecurityIntegration
from app.integrations.instagram import InstagramIntegration
from app.services.score_service import calculate_dms, calculate_cos, get_priority

logger = logging.getLogger(__name__)


async def process_campaign(campaign_id: str, niche: str, location: str, db: Session):
    """
    Processa uma campanha completa:
    1. Busca leads reais via Google Places API
    2. Para cada lead: executa PageSpeed, SSL/DNS e Instagram
    3. Calcula DMS, COS e Priority
    4. Persiste cada lead no banco
    5. Atualiza o status da campanha para 'completed' ou 'failed'
    """
    logger.info(f"🔄 Iniciando processamento da campanha {campaign_id} — {niche} em {location}")

    try:
        # 1. Busca leads usando o LeadService configurado
        lead_service = LeadService()
        leads_found = await lead_service.find_leads(keyword=niche, location=location)
        
        provider_name = "apify" if settings.LEAD_PROVIDER == "apify" else "google_places"

        # Registra chamada ao log de API
        _log_api_call(db, provider_name, "search", "/places:searchText" if provider_name == "google_places" else "/acts/compass~crawler-google-places/runs", 200, True)

        logger.info(f"   📍 {len(leads_found)} leads encontrados no Google Places")

        # 2. Processa cada lead com delay escalonado para respeitar rate limits
        processed_count = 0
        for index, place_lead in enumerate(leads_found):
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign or campaign.status == "cancelled":
                logger.info(f"Campanha {campaign_id} interrompida pelo usuário.")
                return

            if index > 0:
                await asyncio.sleep(1.0)  # 1s de delay entre leads

            try:
                lead_data = await _process_single_lead(place_lead, campaign_id, db)
                db.add(lead_data)
                db.commit()
                processed_count += 1
                logger.info(
                    f"   ✅ [{index + 1}/{len(leads_found)}] {place_lead.name} "
                    f"— DMS: {lead_data.dms} | COS: {lead_data.cos} | {lead_data.priority}"
                )
            except Exception as lead_err:
                logger.error(f"   ⚠️ Erro ao processar lead '{place_lead.name}': {lead_err}")
                db.rollback()
                # Continua processando os outros leads mesmo se um falhar

        # 3. Marca campanha como concluída
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign and campaign.status == "processing":
            campaign.status = "completed"
            campaign.total_leads = processed_count
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


async def _process_single_lead(place_lead, campaign_id: str, db: Session) -> Lead:
    """Executa toda a triagem digital em um único lead e retorna o objeto Lead pronto para salvar."""

    # 2a. PageSpeed Insights
    pagespeed_score = None
    seo_score = None
    lcp_ms = None
    inp_ms = None
    cls_val = None

    if place_lead.website_uri:
        try:
            ps_client = PageSpeedIntegration()
            ps_result = await ps_client.check_performance(place_lead.website_uri)
            pagespeed_score = int(ps_result.performance_score) if ps_result.performance_score else None
            seo_score = int(ps_result.seo_score) if ps_result.seo_score else None
            lcp_ms = int(ps_result.lcp_ms) if hasattr(ps_result, "lcp_ms") and ps_result.lcp_ms else None
            inp_ms = int(ps_result.inp_ms) if hasattr(ps_result, "inp_ms") and ps_result.inp_ms else None
            cls_val = float(ps_result.cls) if hasattr(ps_result, "cls") and ps_result.cls else None
            _log_api_call(db, "pagespeed", "pagespeed", "/runPagespeed", 200, True)
        except Exception as ps_err:
            logger.warning(f"PageSpeed falhou para {place_lead.name}: {ps_err}")

    # 2b. Instagram
    has_instagram = 0
    instagram_url = None
    instagram_candidates_json = None
    try:
        from app.integrations.search import DuckDuckGoSearch
        import json
        
        city = location_from_address(place_lead.formatted_address or "")
        candidates = await DuckDuckGoSearch.search_instagram_profiles(place_lead.name, city)
        
        if candidates:
            clean_name = "".join(c for c in place_lead.name.lower() if c.isalnum())
            first_candidate_clean = "".join(c for c in candidates[0].lower() if c.isalnum())
            
            is_confident = (clean_name in first_candidate_clean or first_candidate_clean in clean_name)
            
            if is_confident:
                insta_client = InstagramIntegration()
                insta_result = await insta_client.get_instagram_profile(candidates[0])
                if insta_result.found:
                    has_instagram = 1
                    instagram_url = f"https://instagram.com/{insta_result.handle}"
                else:
                    instagram_candidates_json = json.dumps(candidates)
            else:
                instagram_candidates_json = json.dumps(candidates)
                
        _log_api_call(db, "duckduckgo", "search", "/html", 200, True)
    except Exception as insta_err:
        logger.warning(f"Instagram search failed for {place_lead.name}: {insta_err}")

    # 2c. Montar dicionário para calcular scores
    lead_dict = {
        "google_rating": place_lead.rating,
        "google_reviews_count": place_lead.user_rating_count or 0,
        "has_website": 1 if place_lead.website_uri else 0,
        "pagespeed_score": pagespeed_score,
        "has_instagram": has_instagram,
        "has_facebook": 0,
        "social_last_post_days": None,
    }

    dms = calculate_dms(lead_dict)
    cos = calculate_cos(lead_dict, dms)
    priority = get_priority(cos)

    # 2d. Extrai cidade do endereço
    address = place_lead.formatted_address or ""
    city = location_from_address(address)

    return Lead(
        id=str(uuid.uuid4()),
        campaign_id=campaign_id,
        name=place_lead.name,
        category=niche_from_types(getattr(place_lead, "primary_type", None)),
        phone=place_lead.national_phone_number,
        website=place_lead.website_uri,
        address=address,
        city=city,
        image_url=getattr(place_lead, "image_url", None),
        gallery_urls=json.dumps(getattr(place_lead, "image_urls", [])) if getattr(place_lead, "image_urls", None) else None,
        google_rating=place_lead.rating,
        google_reviews_count=place_lead.user_rating_count or 0,
        has_website=1 if place_lead.website_uri else 0,
        pagespeed_score=pagespeed_score,
        lcp_ms=lcp_ms,
        inp_ms=inp_ms,
        cls=cls_val,
        seo_score=seo_score,
        has_instagram=has_instagram,
        instagram_url=instagram_url,
        has_facebook=0,
        has_linkedin=0,
        social_last_post_days=None,
        instagram_candidates=instagram_candidates_json,
        dms=dms,
        cos=cos,
        priority=priority,
        commercial_status="new",
        source_provider="google_places",
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


def niche_from_types(primary_type: str | None) -> str:
    """Formata o tipo do Google Places em texto legível."""
    if not primary_type:
        return ""
    return primary_type.replace("_", " ").title()
