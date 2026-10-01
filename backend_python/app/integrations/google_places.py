from typing import List, Optional
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:  # pragma: no cover - optional dependency
    webdriver = None
    By = None
    Options = None
    WebDriverWait = None
    EC = None

from app.core.config import settings
from app.core.interfaces.lead_search import LeadSearchProvider
from app.models.lead import LeadSearchParams, LeadResult
from app.integrations.base import BaseHTTPClient


class GooglePlacesIntegration(BaseHTTPClient, LeadSearchProvider):
    """[Etapa 1] Google Places API (New) implementation with a scraping fallback.

    The public API is preferred, but when it becomes unavailable or returns an error,
    the integration falls back to a lightweight Google search scraping strategy.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.GOOGLE_PLACES_API_KEY
        super().__init__(
            provider_name="Google Places API (New)",
            base_url="https://places.googleapis.com/v1",
            timeout=10.0,
        )
        self.api_key = key

    async def search_leads(self, params: LeadSearchParams) -> List[LeadResult]:
        if self.api_key:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": (
                    "places.id,"
                    "places.displayName,"
                    "places.formattedAddress,"
                    "places.nationalPhoneNumber,"
                    "places.internationalPhoneNumber,"
                    "places.websiteUri,"
                    "places.googleMapsUri,"
                    "places.rating,"
                    "places.userRatingCount,"
                    "places.businessStatus"
                ),
            }

            payload = {
                "textQuery": f"{params.keyword} em {params.location}",
                "pageSize": min(params.max_results, 20),
            }

            try:
                data = await self._request("POST", "/places:searchText", json_data=payload, headers=headers)
                places_data = data.get("places", [])

                results = []
                for item in places_data:
                    display_name = item.get("displayName", {}).get("text", "Sem Nome")
                    results.append(
                        LeadResult(
                            place_id=item.get("id", ""),
                            name=display_name,
                            formatted_address=item.get("formattedAddress"),
                            national_phone_number=item.get("nationalPhoneNumber"),
                            international_phone_number=item.get("internationalPhoneNumber"),
                            website_uri=item.get("websiteUri"),
                            google_maps_uri=item.get("googleMapsUri"),
                            rating=item.get("rating"),
                            user_rating_count=item.get("userRatingCount"),
                            business_status=item.get("businessStatus"),
                        )
                    )
                if results:
                    return results
            except Exception:
                pass

        scraped_results = await self._search_with_google_scraper(params)
        if scraped_results:
            return scraped_results

        if not self.api_key:
            return [
                LeadResult(
                    place_id="mock-1",
                    name=f"{params.keyword} Teste 1",
                    formatted_address=f"Rua Centro, 123, {params.location}",
                    website_uri="https://exemplo1.com.br",
                    rating=4.5,
                    user_rating_count=12,
                    business_status="OPERATIONAL"
                ),
                LeadResult(
                    place_id="mock-2",
                    name=f"{params.keyword} Premium",
                    formatted_address=f"Avenida Principal, 456, {params.location}",
                    website_uri="https://exemplo2.com.br",
                    rating=4.8,
                    user_rating_count=35,
                    business_status="OPERATIONAL"
                )
            ]

        return []

    async def _search_with_google_scraper(self, params: LeadSearchParams) -> List[LeadResult]:
        query = f"{params.keyword} {params.location}".strip()
        search_url = "https://www.google.com/search"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(search_url, params={"q": query, "hl": "pt-BR", "num": 1}, headers=headers)
                response.raise_for_status()
        except Exception:
            response = None

        if response is not None:
            parsed_results = self._parse_google_html(response.text, params)
            if parsed_results:
                return parsed_results

        if webdriver is None or Options is None or By is None or WebDriverWait is None or EC is None:
            return []

        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(f"{search_url}?q={query.replace(' ', '+')}+{params.location.replace(' ', '+')}&hl=pt-BR")
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a")))
            html = driver.page_source
            driver.quit()
            parsed_results = self._parse_google_html(html, params)
            if parsed_results:
                return parsed_results
        except Exception:
            return []

        return []

    def _parse_google_html(self, html: str, params: LeadSearchParams) -> List[LeadResult]:
        soup = BeautifulSoup(html, "html.parser")
        results: List[LeadResult] = []
        seen_ids = set()

        for item in soup.select("a"):
            href = item.get("href", "")
            if not href or "/url?q=" not in href:
                continue

            parsed_query = parse_qs(urlparse(href).query).get("q", [])
            if not parsed_query:
                continue

            target_url = parsed_query[0]
            if target_url.startswith("http") is False:
                continue

            title = " ".join(item.get_text(" ", strip=True).split())
            if not title or title.lower() in {"mais", "imagens", "vídeos", "notícias", "maps"}:
                continue

            if target_url in seen_ids:
                continue
            seen_ids.add(target_url)

            results.append(
                LeadResult(
                    place_id=f"scraped-{len(results) + 1}",
                    name=title,
                    formatted_address=f"Resultado encontrado para '{params.keyword}' em {params.location}",
                    website_uri=target_url,
                )
            )

            if len(results) >= 1:
                break

        return results

    async def get_lead_details(self, place_id: str) -> LeadResult:
        if not self.api_key:
            return LeadResult(
                place_id=place_id,
                name="Mock Place Details",
                formatted_address="Endereço Exemplo",
                national_phone_number="(11) 99999-0000",
                website_uri="https://exemplo.com.br",
            )

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "id,displayName,formattedAddress,nationalPhoneNumber,websiteUri,rating,businessStatus"
            ),
        }

        data = await self._request("GET", f"/places/{place_id}", headers=headers)
        return LeadResult(
            place_id=data.get("id", place_id),
            name=data.get("displayName", {}).get("text", ""),
            formatted_address=data.get("formattedAddress"),
            national_phone_number=data.get("nationalPhoneNumber"),
            website_uri=data.get("websiteUri"),
            rating=data.get("rating"),
            business_status=data.get("businessStatus"),
        )

    async def fetch_place_photos_by_place_id(self, place_id: str, max_photos: int = 4) -> List[str]:
        """
        Coleta fotos públicas do Google Places a partir de um place_id já conhecido.
        """
        if not self.api_key or not place_id:
            return []

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "id,photos",
        }

        try:
            data = await self._request("GET", f"/places/{place_id}", headers=headers)
            raw_photos = data.get("photos", [])[:max_photos]
            return await self._resolve_photo_media_uris(raw_photos)
        except Exception as e:
            self.logger.warning(f"Erro ao buscar fotos por place_id '{place_id}': {e}")
            return []

    async def fetch_place_photos_by_query(self, query: str, max_photos: int = 4) -> List[str]:
        """
        Coleta sob demanda fotos públicas do Google Places usando o nome e cidade/endereço da empresa.
        Retorna URLs diretas de alta resolução da CDN do Google (lh3.googleusercontent.com).
        """
        if not self.api_key or not query.strip():
            return []

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.photos",
        }
        payload = {
            "textQuery": query.strip(),
            "pageSize": 1,
        }

        try:
            data = await self._request("POST", "/places:searchText", json_data=payload, headers=headers)
            places = data.get("places", [])
            if not places:
                return []

            raw_photos = places[0].get("photos", [])[:max_photos]
            return await self._resolve_photo_media_uris(raw_photos)
        except Exception as e:
            self.logger.warning(f"Erro ao buscar fotos por query '{query}': {e}")
            return []

    async def _resolve_photo_media_uris(self, raw_photos: List[dict]) -> List[str]:
        """
        Resolve os nomes das fotos do Google Places para URLs públicas diretas da CDN.
        """
        if not raw_photos:
            return []

        photo_urls = []
        async with httpx.AsyncClient(timeout=8.0) as client:
            for photo in raw_photos:
                photo_name = photo.get("name")
                if not photo_name:
                    continue
                media_url = f"{self.base_url}/{photo_name}/media"
                params = {
                    "maxHeightPx": 800,
                    "maxWidthPx": 1200,
                    "skipHttpRedirect": "true",
                    "key": self.api_key,
                }
                try:
                    resp = await client.get(media_url, params=params)
                    if resp.status_code == 200:
                        cdn_url = resp.json().get("photoUri")
                        if cdn_url:
                            photo_urls.append(cdn_url)
                except Exception as err:
                    self.logger.debug(f"Falha ao resolver CDN para foto {photo_name}: {err}")

        return photo_urls

