import asyncio
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv('backend_python/.env')
sys.path.append(os.path.abspath('backend_python'))

from app.integrations.gemini_ai import GeminiAIIntegration
from app.models.triage import FullTriageReport, PageSpeedResult, DomainSecurityResult, InstagramProfileResult
from app.models.lead import LeadResult

async def test():
    client = GeminiAIIntegration()
    
    lead_result = LeadResult(
        place_id="123",
        name="Clínica Sorriso Feliz",
        formatted_address="Rua das Flores, 123 - Centro, São Paulo - SP",
        national_phone_number="(11) 98765-4321",
        website_uri="https://sorrisofeliz.com.br",
        rating=4.5,
        user_rating_count=120,
    )
    
    report = FullTriageReport(
        lead=lead_result,
        pagespeed=None,
        security=None,
        instagram=None,
        needs_new_website=True,
    )

    try:
        diagnosis = await client.generate_diagnosis(report)
        with open('ai_out.txt', 'w', encoding='utf-8') as f:
            f.write('WHATSAPP: ' + str(diagnosis.whatsapp_draft) + '\n')
            f.write('EMAIL: ' + str(diagnosis.email_draft) + '\n')
    except Exception as e:
        with open('ai_out.txt', 'w', encoding='utf-8') as f:
            f.write(repr(e))

if __name__ == '__main__':
    asyncio.run(test())
