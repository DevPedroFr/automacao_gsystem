import asyncio
import unittest

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.campaigns import CampaignCreate, create_campaign, get_campaign, list_campaigns
from app.api.leads import list_all_leads
from app.core.auth import AuthenticatedUser
from app.db.database import Base
from app.db.models import Campaign, Lead


class TenantAccessTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.spy_car = AuthenticatedUser("spy-user", "spy_car")
        self.g_system = AuthenticatedUser("g-user", "g_system")
        self.directoria = AuthenticatedUser("director", "diretoria")

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_campaign_and_crm_lists_are_scoped_by_access_level(self):
        spy_campaign = Campaign(id="spy-campaign", niche="Nicho Spy", location="São Paulo", tenant_id="spy_car")
        g_campaign = Campaign(id="g-campaign", niche="Nicho G", location="Curitiba", tenant_id="g_system")
        spy_lead = Lead(id="spy-lead", name="Lead Spy", in_crm=True, tenant_id="spy_car")
        g_lead = Lead(id="g-lead", name="Lead G", in_crm=True, tenant_id="g_system")
        self.session.add_all([spy_campaign, g_campaign, spy_lead, g_lead])
        self.session.commit()

        self.assertEqual(
            [campaign["id"] for campaign in list_campaigns(self.session, self.spy_car)["data"]],
            ["spy-campaign"],
        )
        self.assertEqual(
            {campaign["id"] for campaign in list_campaigns(self.session, self.directoria)["data"]},
            {"spy-campaign", "g-campaign"},
        )
        self.assertEqual(list_all_leads(self.session, self.g_system)["total"], 1)
        self.assertEqual(list_all_leads(self.session, self.directoria)["total"], 2)
        self.assertEqual(
            list_all_leads(self.session, self.directoria, "spy_car")["data"][0]["tenant_id"],
            "spy_car",
        )
        with self.assertRaises(HTTPException) as error:
            list_all_leads(self.session, self.g_system, "spy_car")
        self.assertEqual(error.exception.status_code, 403)

    def test_campaign_from_another_tenant_is_not_accessible(self):
        self.session.add(Campaign(id="spy-campaign", niche="Nicho", location="São Paulo", tenant_id="spy_car"))
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            get_campaign("spy-campaign", self.session, self.g_system)

        self.assertEqual(error.exception.status_code, 404)

    def test_directoria_must_choose_campaign_company(self):
        with self.assertRaises(HTTPException) as error:
            asyncio.run(create_campaign(
                CampaignCreate(niche="Nicho", location="São Paulo"),
                BackgroundTasks(),
                self.session,
                self.directoria,
            ))

        self.assertEqual(error.exception.status_code, 400)

    def test_directoria_can_create_for_either_company_and_users_for_their_own(self):
        spy_campaign = asyncio.run(create_campaign(
            CampaignCreate(niche="Nicho Spy", location="São Paulo", tenant_id="spy_car"),
            BackgroundTasks(),
            self.session,
            self.directoria,
        ))["data"]
        g_campaign = asyncio.run(create_campaign(
            CampaignCreate(niche="Nicho G", location="Curitiba"),
            BackgroundTasks(),
            self.session,
            self.g_system,
        ))["data"]

        self.assertEqual(spy_campaign["tenant_id"], "spy_car")
        self.assertEqual(g_campaign["tenant_id"], "g_system")

        with self.assertRaises(HTTPException) as error:
            asyncio.run(create_campaign(
                CampaignCreate(niche="Nicho indevido", location="São Paulo", tenant_id="g_system"),
                BackgroundTasks(),
                self.session,
                self.spy_car,
            ))
        self.assertEqual(error.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
