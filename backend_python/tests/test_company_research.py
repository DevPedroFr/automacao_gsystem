import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from fastapi import HTTPException
from google.genai._interactions import RateLimitError
from google.genai.errors import APIError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.leads import research_lead
from app.db.database import Base
from app.db.models import Lead
from app.integrations.company_research import CompanyResearchError, CompanyResearchIntegration


class CompanyResearchTests(unittest.TestCase):
    @staticmethod
    def _rate_limit_error(message, headers=None):
        body = {"error": {"message": message, "code": "too_many_requests"}}
        response = httpx.Response(
            429,
            request=httpx.Request("POST", "https://generativelanguage.googleapis.com/v1/interactions"),
            headers=headers,
            json=body,
        )
        return RateLimitError("Error code: 429", response=response, body=body)

    @patch("app.integrations.company_research.settings.GEMINI_MODEL", "configured-model")
    @patch("app.integrations.company_research.genai.Client")
    def test_search_returns_structured_data_and_grounded_sources(self, client_factory):
        annotation = SimpleNamespace(
            type="url_citation",
            title="Site oficial",
            url="https://example.com/sobre",
        )
        interaction = SimpleNamespace(
            output_text=json.dumps({
                "responsible_name": "Ana Silva",
                "responsible_role": "Diretora",
                "public_business_phone": "+55 11 3333-4444",
                "opening_date": "2012",
            }),
            steps=[
                SimpleNamespace(
                    type="model_output",
                    content=[
                        SimpleNamespace(type="text", annotations=[annotation]),
                    ],
                ),
            ],
        )
        client = client_factory.return_value
        client.interactions.create.return_value = interaction

        result = CompanyResearchIntegration("test-api-key").search_company(
            "Empresa Exemplo",
            "Rua Central, São Paulo",
        )

        self.assertEqual(result["responsible_name"], "Ana Silva")
        self.assertEqual(result["responsible_role"], "Diretora")
        self.assertEqual(result["public_business_phone"], "+55 11 3333-4444")
        self.assertEqual(result["opening_date"], "2012")
        self.assertEqual(result["sources"], [{
            "title": "Site oficial",
            "url": "https://example.com/sobre",
        }])
        request = client.interactions.create.call_args.kwargs
        self.assertEqual(request["model"], "configured-model")
        self.assertEqual(request["tools"], [{"type": "google_search"}])
        self.assertFalse(request["store"])
        self.assertIn("Empresa Exemplo", request["input"])
        self.assertIn("Rua Central, São Paulo", request["input"])
        self.assertIn("telefone pessoal", request["system_instruction"])
        retry_options = client_factory.call_args.kwargs["http_options"].retry_options
        self.assertEqual(retry_options.attempts, 1)

    @patch("app.integrations.company_research.genai.Client")
    def test_search_rejects_response_without_structured_output(self, client_factory):
        client_factory.return_value.interactions.create.return_value = SimpleNamespace(
            output_text="",
            steps=[],
        )

        with self.assertRaisesRegex(CompanyResearchError, "não retornou dados"):
            CompanyResearchIntegration("test-api-key").search_company("Empresa", "Endereço")

    @patch("app.integrations.company_research.time.sleep")
    @patch("app.integrations.company_research.genai.Client")
    def test_search_retries_transient_rate_limit(self, client_factory, sleep):
        interaction = SimpleNamespace(
            output_text=json.dumps({"responsible_name": "Ana Silva"}),
            steps=[],
        )
        client = client_factory.return_value
        client.interactions.create.side_effect = [
            APIError(429, {"error": {"status": "RESOURCE_EXHAUSTED"}}),
            interaction,
        ]

        result = CompanyResearchIntegration("test-api-key").search_company("Empresa", "Endereço")

        self.assertEqual(result["responsible_name"], "Ana Silva")
        self.assertEqual(client.interactions.create.call_count, 2)
        sleep.assert_called_once_with(1)

    @patch("app.integrations.company_research.time.sleep")
    @patch("app.integrations.company_research.genai.Client")
    def test_search_respects_retry_after_for_transient_rate_limit(self, client_factory, sleep):
        interaction = SimpleNamespace(
            output_text=json.dumps({"responsible_name": "Ana Silva"}),
            steps=[],
        )
        client = client_factory.return_value
        client.interactions.create.side_effect = [
            self._rate_limit_error(
                "Temporary rate limit",
                headers={"retry-after-ms": "30000"},
            ),
            interaction,
        ]

        result = CompanyResearchIntegration("test-api-key").search_company("Empresa", "Endereço")

        self.assertEqual(result["responsible_name"], "Ana Silva")
        self.assertEqual(client.interactions.create.call_count, 2)
        sleep.assert_called_once_with(30)

    @patch("app.integrations.company_research.time.sleep")
    @patch("app.integrations.company_research.genai.Client")
    def test_search_does_not_retry_exhausted_quota(self, client_factory, sleep):
        client_factory.return_value.interactions.create.side_effect = self._rate_limit_error(
            "You exceeded your current quota, please check your plan and billing details."
        )

        with self.assertRaises(CompanyResearchError) as context:
            CompanyResearchIntegration("test-api-key").search_company("Empresa", "Endereço")

        self.assertEqual(context.exception.status_code, 429)
        self.assertIn("cotas do modelo", str(context.exception))
        self.assertEqual(client_factory.return_value.interactions.create.call_count, 1)
        sleep.assert_not_called()

    @patch("app.integrations.company_research.time.sleep")
    @patch("app.integrations.company_research.genai.Client")
    def test_search_retries_quota_message_when_retry_after_is_provided(self, client_factory, sleep):
        interaction = SimpleNamespace(
            output_text=json.dumps({"responsible_name": "Ana Silva"}),
            steps=[],
        )
        client = client_factory.return_value
        client.interactions.create.side_effect = [
            self._rate_limit_error(
                "You exceeded your current quota, please check your plan and billing details.",
                headers={"retry-after-ms": "30000"},
            ),
            interaction,
        ]

        result = CompanyResearchIntegration("test-api-key").search_company("Empresa", "Endereço")

        self.assertEqual(result["responsible_name"], "Ana Silva")
        self.assertEqual(client.interactions.create.call_count, 2)
        sleep.assert_called_once_with(30)

    @patch("app.api.leads.settings.GEMINI_API_KEY", "test-api-key")
    @patch(
        "app.api.leads.CompanyResearchIntegration.search_company",
        return_value={"responsible_name": "Ana Silva", "sources": []},
    )
    def test_lead_research_endpoint_uses_saved_name_and_address(self, search_company):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        try:
            session.add(Lead(id="lead-id", name="Empresa Exemplo", address="Rua Central, São Paulo"))
            session.commit()

            result = asyncio.run(research_lead("lead-id", session))
            cached_result = asyncio.run(research_lead("lead-id", session))

            self.assertEqual(result["data"]["responsible_name"], "Ana Silva")
            self.assertEqual(cached_result, result)
            search_company.assert_called_once_with("Empresa Exemplo", "Rua Central, São Paulo")
        finally:
            session.close()
            engine.dispose()

    @patch("app.api.leads.settings.GEMINI_API_KEY", "test-api-key")
    @patch(
        "app.api.leads.run_in_threadpool",
        side_effect=CompanyResearchError(
            "Limite do Gemini",
            status_code=429,
            retry_after_seconds=30,
        ),
    )
    def test_lead_research_endpoint_preserves_rate_limit_status(self, run_search):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        try:
            session.add(Lead(id="lead-id", name="Empresa Exemplo"))
            session.commit()

            with self.assertRaises(HTTPException) as context:
                asyncio.run(research_lead("lead-id", session))

            self.assertEqual(context.exception.status_code, 429)
            self.assertEqual(context.exception.headers["Retry-After"], "30")
            run_search.assert_called_once()
        finally:
            session.close()
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
