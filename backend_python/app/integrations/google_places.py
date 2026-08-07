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
        if not self.api_key:
            return []

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
