import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from app.integrations.google_places import GooglePlacesIntegration
from app.models.lead import LeadResult, LeadSearchParams


class GooglePlacesFallbackTests(unittest.TestCase):
    def test_search_leads_falls_back_to_scraper_when_api_fails(self):
        integration = GooglePlacesIntegration(api_key="fake-key")
        params = LeadSearchParams(keyword="dentista", location="São Paulo", max_results=3)
        fallback_result = [
            LeadResult(
                place_id="scraped-1",
                name="Dentista Exemplo",
                formatted_address="Rua Exemplo, 123, São Paulo",
                website_uri="https://dentistaexemplo.com.br",
            )
        ]

        with patch.object(
            integration,
            "_request",
            new=AsyncMock(side_effect=Exception("api unavailable")),
        ), patch.object(
            integration,
            "_search_with_google_scraper",
            new=AsyncMock(return_value=fallback_result),
        ):
            result = asyncio.run(integration.search_leads(params))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Dentista Exemplo")
        self.assertEqual(result[0].website_uri, "https://dentistaexemplo.com.br")

    def test_search_leads_returns_empty_when_no_results_found(self):
        integration = GooglePlacesIntegration(api_key="fake-key")
        params = LeadSearchParams(keyword="clinica odontológica", location="Mogi das Cruzes", max_results=1)

        with patch.object(
            integration,
            "_request",
            new=AsyncMock(side_effect=Exception("api unavailable")),
        ), patch.object(
            integration,
            "_search_with_google_scraper",
            new=AsyncMock(return_value=[]),
        ):
            result = asyncio.run(integration.search_leads(params))

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
