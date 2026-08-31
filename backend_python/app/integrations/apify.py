import asyncio
import logging
from typing import List, Optional
from app.core.config import settings
from app.core.interfaces.lead_search import LeadSearchProvider
from app.models.lead import LeadSearchParams, LeadResult
from app.integrations.base import BaseHTTPClient
from app.core.exceptions import IntegrationBaseException

logger = logging.getLogger(__name__)


class ApifyIntegration(BaseHTTPClient, LeadSearchProvider):
    """[Etapa 1] Apify Google Places Scraper Actor implementation."""

    def __init__(self, api_key: Optional[str] = None):
        # We read APIFY_API_KEY from settings.
        # Note: we will add APIFY_API_KEY to settings class.
        self.api_key = api_key or getattr(settings, "APIFY_API_KEY", None)
        super().__init__(
            provider_name="Apify Google Places Scraper",
            base_url="https://api.apify.com/v2",
            timeout=30.0,
        )

    async def search_leads(self, params: LeadSearchParams) -> List[LeadResult]:
        if not self.api_key:
            logger.error("Chave de API do Apify (APIFY_API_KEY) não configurada.")
            return []

        actor_id = "compass~crawler-google-places"
        run_endpoint = f"/acts/{actor_id}/runs"
        
        # Start Apify Actor
        payload = {
            "searchStringsArray": [params.keyword],
            "locationQuery": params.location,
            "maxCrawledPlacesPerSearch": min(params.max_results, 15),
            "language": "en",
        }
        
        try:
            logger.info(f"🚀 Iniciando Apify Google Places Scraper para '{params.keyword}' em '{params.location}'")
            run_data = await self._request(
                "POST", 
                run_endpoint, 
                params={"token": self.api_key}, 
                json_data=payload
            )
            
            run_id = run_data.get("data", {}).get("id")
            dataset_id = run_data.get("data", {}).get("defaultDatasetId")
            
            if not run_id or not dataset_id:
                raise IntegrationBaseException(
                    "Retorno inválido da API do Apify (runId ou datasetId ausentes)",
                    provider=self.provider_name
                )
                
            logger.info(f"⏳ Actor iniciado. Run ID: {run_id}. Iniciando polling...")
            
            # Polling status of run
            finished = False
            attempts = 0
            max_attempts = 40
            
            while not finished and attempts < max_attempts:
                attempts += 1
                await asyncio.sleep(5.0)
                
                status_endpoint = f"/actor-runs/{run_id}"
                try:
                    status_data = await self._request("GET", status_endpoint, params={"token": self.api_key})
                    status = status_data.get("data", {}).get("status")
                    logger.info(f"   -> Polling Apify (tentativa {attempts}/{max_attempts}): status = {status}")
                    
                    if status in ["SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"]:
                        finished = True
                        if status != "SUCCEEDED":
                            raise IntegrationBaseException(
                                f"O Actor no Apify terminou com status de falha: {status}",
                                provider=self.provider_name
                            )
                except Exception as poll_err:
                    logger.warning(f"⚠️ Erro ao verificar status do run {run_id}: {poll_err}")
                    continue
                    
            if not finished:
                raise IntegrationBaseException(
                    "Limite de tempo atingido esperando pela conclusão do Actor no Apify",
                    provider=self.provider_name
                )
                
            # Get Dataset Items
            items_endpoint = f"/datasets/{dataset_id}/items"
            logger.info(f"📦 Buscando itens do dataset {dataset_id}")
            
            items = await self._request("GET", items_endpoint, params={"token": self.api_key})
            
            if not isinstance(items, list):
                logger.error(f"Formato de resposta do dataset inesperado: {type(items)}")
                return []
                
            logger.info(f"✅ Apify Scraper concluído. {len(items)} leads extraídos.")
            
            # Map Items
            results = []
            for item in items:
                name = item.get("title") or item.get("name") or "Empresa sem Nome"
                # Map stars/rating/totalScore
                try:
                    rating = float(item.get("totalScore") or item.get("rating") or item.get("stars") or 0.0)
                except (ValueError, TypeError):
                    rating = 0.0
                    
                try:
                    reviews_count = int(item.get("reviewsCount") or item.get("reviews") or 0)
                except (ValueError, TypeError):
                    reviews_count = 0
                    
                image_url = item.get("imageUrl")
                if not image_url and item.get("imageUrls") and len(item.get("imageUrls")) > 0:
                    image_url = item.get("imageUrls")[0]
                    
                results.append(
                    LeadResult(
                        place_id=item.get("placeId") or item.get("cid") or item.get("id") or f"apify-{len(results)}",
                        name=name,
                        formatted_address=item.get("address"),
                        national_phone_number=item.get("phone") or item.get("phoneUnformatted"),
                        international_phone_number=item.get("phone"),
                        website_uri=item.get("website"),
                        google_maps_uri=item.get("url"),
                        rating=rating,
                        user_rating_count=reviews_count,
                        business_status="CLOSED" if item.get("permanentlyClosed") else "OPERATIONAL",
                    )
                )
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro no provedor Apify: {e}")
            raise e

    async def get_lead_details(self, place_id: str) -> LeadResult:
        return LeadResult(
            place_id=place_id,
            name="Apify Details Mock",
            formatted_address="Endereço Apify Details",
            website_uri="https://exemplo.com.br",
        )
