import asyncio
from app.workers.celery_app import celery_app
from app.services.lead_service import LeadService
from app.services.triage_service import TriageService
from app.services.diagnosis_service import DiagnosisService
from app.services.site_service import SiteService

lead_service = LeadService()
triage_service = TriageService()
diagnosis_service = DiagnosisService()
site_service = SiteService()


@celery_app.task(name="app.workers.tasks.scheduled_lead_search")
def scheduled_lead_search(keyword: str, location: str):
    """Async background task for searching and auto-processing leads."""
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    async def run_pipeline():
        leads = await lead_service.find_leads(keyword, location, max_results=10)
        reports = []
        for lead in leads:
            triage = await triage_service.execute_triage(lead)
            diagnosis, stitch_prompt = await diagnosis_service.run_diagnosis_and_prompt(triage)
            if stitch_prompt:
                site = await site_service.generate_site_for_lead(lead.name, stitch_prompt.stitch_prompt)
            reports.append({"lead": lead.name, "needs_site": triage.needs_new_website})
        return reports

    return loop.run_until_complete(run_pipeline())
