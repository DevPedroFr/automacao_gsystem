import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.dashboard import get_dashboard_stats
from app.core.auth import AuthenticatedUser
from app.db.database import Base
from app.db.models import Lead


class DashboardCrmStatsTests(unittest.TestCase):
    user = AuthenticatedUser(username="test", access_level="g_system")

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_counts_only_crm_leads_and_calculates_closed_over_contacted(self):
        crm_leads = [
            Lead(id="contacted-1", name="Contatado 1", in_crm=True, commercial_status="contacted"),
            Lead(id="contacted-2", name="Contatado 2", in_crm=True, commercial_status="contacted"),
            Lead(id="interested", name="Interessado", in_crm=True, commercial_status="negotiation"),
            Lead(id="closed", name="Fechado", in_crm=True, commercial_status="won"),
            Lead(id="paid", name="Pago", in_crm=True, commercial_status="paid"),
        ]
        outside_crm = Lead(id="external", name="Fora do CRM", commercial_status="won")
        other_tenant = Lead(
            id="spy-contacted",
            name="Contatado da Spy car",
            in_crm=True,
            commercial_status="contacted",
            tenant_id="spy_car",
        )
        self.session.add_all([*crm_leads, outside_crm, other_tenant])
        self.session.commit()

        stats = get_dashboard_stats(self.session, self.user)["data"]["crmStats"]

        self.assertEqual(stats, {
            "contactedCustomers": 2,
            "interestedCustomers": 1,
            "closedCustomers": 1,
            "paidCustomers": 1,
            "conversionRate": 50.0,
        })

    def test_conversion_is_zero_when_there_are_no_contacted_leads(self):
        self.session.add(Lead(id="closed", name="Fechado", in_crm=True, commercial_status="won"))
        self.session.commit()

        stats = get_dashboard_stats(self.session, self.user)["data"]["crmStats"]

        self.assertEqual(stats["conversionRate"], 0)


if __name__ == "__main__":
    unittest.main()
