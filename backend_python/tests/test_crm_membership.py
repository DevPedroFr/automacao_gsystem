import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.api.leads import (
    CrmRecordCreate,
    LeadStatusUpdate,
    add_lead_to_crm,
    create_lead_record,
    list_lead_records,
    list_all_leads,
    update_lead_status,
)
from app.core.auth import AuthenticatedUser
from app.db.database import Base, _apply_migrations
from app.db.models import CrmRecord, Lead


class CrmMembershipTests(unittest.TestCase):
    user = AuthenticatedUser(username="test", access_level="g_system")

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

        self.assertEqual(list_all_leads(self.session, self.user)["total"], 0)

        response = add_lead_to_crm(selected_lead.id, self.session, self.user)

        self.assertTrue(response["data"]["in_crm"])
        crm_leads = list_all_leads(self.session, self.user)
        self.assertEqual(crm_leads["total"], 1)
        self.assertEqual(crm_leads["data"][0]["id"], selected_lead.id)
        self.assertIsNotNone(crm_leads["data"][0]["last_record_at"])
        records = list_lead_records(selected_lead.id, self.session, self.user)["data"]
        self.assertEqual(records[0]["record_type"], "crm_added")
        self.assertEqual(records[0]["created_by"], self.user.username)

    def test_notes_and_status_changes_keep_user_and_history(self):
        lead = Lead(id="history-lead", name="Lead com histórico", in_crm=True)
        self.session.add(lead)
        self.session.commit()

        note = create_lead_record(
            lead.id,
            CrmRecordCreate(content="  Ligação realizada  "),
            self.session,
            self.user,
        )["data"]
        update_lead_status(
            lead.id,
            LeadStatusUpdate(status="contacted"),
            self.session,
            self.user,
        )

        records = list_lead_records(lead.id, self.session, self.user)["data"]
        self.assertEqual(note["content"], "Ligação realizada")
        self.assertEqual(note["created_by"], self.user.username)
        self.assertEqual(records[0]["record_type"], "status_change")
        self.assertEqual(records[0]["previous_status"], "new")
        self.assertEqual(records[0]["new_status"], "contacted")
        self.assertEqual(records[0]["created_by"], self.user.username)

    def test_blank_note_is_rejected(self):
        lead = Lead(id="blank-note-lead", name="Lead sem nota")
        self.session.add(lead)
        self.session.commit()

        with self.assertRaises(HTTPException) as error:
            create_lead_record(
                lead.id,
                CrmRecordCreate(content="   "),
                self.session,
                self.user,
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(self.session.query(CrmRecord).count(), 0)

    def test_migration_adds_crm_flag_to_existing_database(self):
        engine = create_engine("sqlite:///:memory:")
        try:
            with engine.begin() as connection:
                connection.exec_driver_sql(
                    "CREATE TABLE campaigns (id VARCHAR PRIMARY KEY)"
                )
                connection.exec_driver_sql(
                    "CREATE TABLE leads (id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL)"
                )
                connection.exec_driver_sql(
                    "INSERT INTO campaigns (id) VALUES ('old-campaign')"
                )
                connection.exec_driver_sql(
                    "INSERT INTO leads (id, name) VALUES ('old-lead', 'Lead antigo')"
                )

            _apply_migrations(engine)
            lead_columns = {column["name"] for column in inspect(engine).get_columns("leads")}
            campaign_columns = {column["name"] for column in inspect(engine).get_columns("campaigns")}
            self.assertIn("tenant_id", lead_columns)
            self.assertIn("in_crm", lead_columns)
            self.assertIn("company_research_data", lead_columns)
            self.assertIn("company_research_updated_at", lead_columns)
            self.assertIn("tenant_id", campaign_columns)
            with engine.connect() as connection:
                self.assertEqual(
                    connection.exec_driver_sql("SELECT tenant_id FROM leads WHERE id = 'old-lead'").scalar(),
                    "g_system",
                )
                self.assertEqual(
                    connection.exec_driver_sql("SELECT tenant_id FROM campaigns WHERE id = 'old-campaign'").scalar(),
                    "g_system",
                )
        finally:
            engine.dispose()

    def test_lead_can_be_moved_to_paid_status(self):
        lead = Lead(id="paid-lead", name="Lead pago", in_crm=True, commercial_status="won")
        self.session.add(lead)
        self.session.commit()

        response = update_lead_status(
            lead.id,
            LeadStatusUpdate(status="paid"),
            self.session,
            self.user,
        )

        self.assertEqual(response["data"]["commercial_status"], "paid")


if __name__ == "__main__":
    unittest.main()
