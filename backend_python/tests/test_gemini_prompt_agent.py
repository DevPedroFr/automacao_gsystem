import asyncio
import unittest
from unittest.mock import patch

from app.integrations.gemini_ai import GeminiAIIntegration
from app.models.lead import LeadResult
from app.models.triage import FullTriageReport, PageSpeedResult, DomainSecurityResult, InstagramProfileResult


class GeminiPromptAgentTests(unittest.TestCase):
    def test_generate_diagnosis_uses_gemini_response(self):
        integration = GeminiAIIntegration(api_key="fake-key")
        report = FullTriageReport(
            lead=LeadResult(place_id="1", name="Clínica Teste", formatted_address="São Paulo"),
            pagespeed=PageSpeedResult(url="https://example.com", performance_score=40, seo_score=60, mobile_friendly=True),
            security=DomainSecurityResult(domain="example.com", ssl_valid=True),
            instagram=InstagramProfileResult(handle="@clinicateste", is_business_account=True, followers_count=100),
            needs_new_website=True,
        )

        with patch.object(integration, "_call_gemini", return_value='{"overall_summary":"Resumo","needs_new_website":true,"recommendations":[{"category":"Performance","severity":"HIGH","finding":"Baixa performance","action_item":"Otimize"}]}'):
            result = asyncio.run(integration.generate_diagnosis(report))

        self.assertEqual(result.overall_summary, "Resumo")
        self.assertTrue(result.needs_new_website)
        self.assertEqual(result.recommendations[0].category, "Performance")


if __name__ == "__main__":
    unittest.main()
