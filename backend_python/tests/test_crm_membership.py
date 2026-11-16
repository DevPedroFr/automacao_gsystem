import unittest

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.api.leads import add_lead_to_crm, list_all_leads
from app.db.database import Base, _apply_migrations
from app.db.models import Lead


class CrmMembershipTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_only_manually_added_leads_appear_in_crm(self):
        selected_lead = Lead(id="selected", name="Lead selecionado")
        unselected_lead = Lead(id="unselected", name="Lead não selecionado")
        self.session.add_all([selected_lead, unselected_lead])
        self.session.commit()

        self.assertEqual(list_all_leads(self.session)["total"], 0)

        response = add_lead_to_crm(selected_lead.id, self.session)

        self.assertTrue(response["data"]["in_crm"])
        crm_leads = list_all_leads(self.session)
        self.assertEqual(crm_leads["total"], 1)
        self.assertEqual(crm_leads["data"][0]["id"], selected_lead.id)

    def test_migration_adds_crm_flag_to_existing_database(self):
        engine = create_engine("sqlite:///:memory:")
        try:
            with engine.begin() as connection:
                connection.exec_driver_sql(
                    "CREATE TABLE leads (id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL)"
                )

            _apply_migrations(engine)
            columns = {column["name"] for column in inspect(engine).get_columns("leads")}
            self.assertIn("in_crm", columns)
            self.assertIn("company_research_data", columns)
            self.assertIn("company_research_updated_at", columns)
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
