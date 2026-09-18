import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env variables from backend_python/.env
load_dotenv('backend_python/.env')

sys.path.append(os.path.abspath('backend_python'))

from app.integrations.apify import ApifyIntegration
from app.models.lead import LeadSearchParams

async def test_search():
    client = ApifyIntegration()
    params = LeadSearchParams(keyword="Escritorio de Advocacia", location="Mogi das Cruzes", max_results=15)
    print("Iniciando busca no Apify...")
    try:
        leads = await client.search_leads(params)
        print(f"Encontrados: {len(leads)} leads")
        for idx, lead in enumerate(leads):
            print(f"{idx+1}. {lead.name} - {lead.formatted_address}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == '__main__':
    asyncio.run(test_search())
