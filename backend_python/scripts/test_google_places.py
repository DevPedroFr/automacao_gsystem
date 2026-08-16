import asyncio
import sys
import os

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add parent dir to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.integrations.google_places import GooglePlacesIntegration
from app.models.lead import LeadSearchParams


async def _run_test_places():
    keyword = sys.argv[1] if len(sys.argv) > 1 else "Clínica Odontológica"
    location = sys.argv[2] if len(sys.argv) > 2 else "São Paulo, SP"

    print("=" * 60)
    print("Testando integração Google Places API (New)")
    print(f"Palavra-chave: {keyword}")
    print(f"Localização: {location}")
    print("=" * 60)

    client = GooglePlacesIntegration()

    if not client.api_key:
        print("\n[AVISO] GOOGLE_PLACES_API_KEY nao configurada no arquivo .env!")
        print("[INFO] Rodando em modo de demonstracao/simulacao (Mock).\n")
    else:
        print("\n[OK] Chave GOOGLE_PLACES_API_KEY encontrada no .env! Fazendo requisicao real para o Google Cloud...\n")

    params = LeadSearchParams(keyword=keyword, location=location, max_results=5)

    try:
        leads = await client.search_leads(params)
        print(f"Encontrados {len(leads)} leads:\n")

        for idx, lead in enumerate(leads, 1):
            print(f"[{idx}] {lead.name}")
            print(f"    - ID do Local: {lead.place_id}")
            print(f"    - Endereco: {lead.formatted_address or 'N/A'}")
            print(f"    - Telefone: {lead.national_phone_number or 'N/A'}")
            print(f"    - Site: {lead.website_uri or 'Sem site cadastrado'}")
            print(f"    - Avaliacao: {lead.rating or 'N/A'} ({lead.user_rating_count or 0} avaliações)")
            print(f"    - Status: {lead.business_status or 'N/A'}\n")

    except Exception as e:
        print(f"[ERRO] Falha ao buscar leads: {e}")


# Prevent pytest from collecting this utility script as a test case.
_run_test_places.__test__ = False


if __name__ == "__main__":
    asyncio.run(_run_test_places())
