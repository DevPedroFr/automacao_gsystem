import asyncio
import unittest
from types import SimpleNamespace

from app.api.leads import _campaign_lead_to_dict, export_leads_csv
from app.core.auth import AuthenticatedUser
from app.db.models import Campaign, Lead
from app.workers.campaign_worker import _process_single_lead


class FakeQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *_):
        return self

    def order_by(self, *_):
        return self

    def first(self):
        return self.result

    def all(self):
        return self.result


class FakeSession:
    def query(self, model):
        if model is Campaign:
            return FakeQuery(SimpleNamespace(id="campaign-id"))
        if model is Lead:
            return FakeQuery([
                SimpleNamespace(
                    name="Clínica Exemplo",
                    address="Rua Central, 100, Campinas, SP",
                    google_rating=4.7,
                    phone="(19) 99999-0000",
                )
            ])
        raise AssertionError(f"Consulta inesperada: {model}")


class CampaignWorkerTests(unittest.TestCase):
    user = AuthenticatedUser(username="test", access_level="g_system")

    def test_campaign_lead_keeps_only_basic_google_data(self):
        place_lead = SimpleNamespace(
            name="Clínica Exemplo",
            formatted_address="Rua Central, 100, Campinas, SP",
            rating=4.7,
            user_rating_count=83,
        )

        lead = _process_single_lead(place_lead, "campaign-id", "google_places")

        self.assertEqual(lead.name, "Clínica Exemplo")
        self.assertEqual(lead.address, place_lead.formatted_address)
        self.assertEqual(lead.city, "Campinas")
        self.assertEqual(lead.google_rating, 4.7)
        self.assertEqual(lead.google_reviews_count, 83)
        self.assertIsNone(lead.phone)
        self.assertIsNone(lead.website)
        self.assertEqual(lead.source_provider, "google_places")

    def test_campaign_lead_response_exposes_only_list_fields(self):
        lead = SimpleNamespace(
            id="lead-id",
            name="Clínica Exemplo",
            address="Rua Central, 100, Campinas, SP",
            city="Campinas",
            google_rating=4.7,
            in_crm=False,
            phone="(19) 99999-0000",
        )

        result = _campaign_lead_to_dict(lead)

        self.assertEqual(
            set(result),
            {"id", "name", "address", "city", "google_rating", "in_crm"},
        )
        self.assertNotIn("phone", result)

    def test_campaign_csv_contains_only_requested_columns(self):
        response = export_leads_csv("campaign-id", FakeSession(), self.user)

        async def read_response():
            chunks = [chunk async for chunk in response.body_iterator]
            return "".join(chunk.decode() if isinstance(chunk, bytes) else chunk for chunk in chunks).lstrip("\ufeff")

        csv_content = asyncio.run(read_response())

        self.assertEqual(csv_content.splitlines()[0], "Nome,Endereço,Avaliação Google")
        self.assertIn("Clínica Exemplo", csv_content)
        self.assertNotIn("Telefone", csv_content)
        self.assertNotIn("(19) 99999-0000", csv_content)


if __name__ == "__main__":
    unittest.main()
