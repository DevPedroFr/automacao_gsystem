"""
Script de teste integrado de todas as rotas da API FastAPI para garantir paridade 100% com o backend Node.js antigo.
"""
import sys
import os
import uuid

# Garante UTF-8 no terminal Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Adiciona o diretório do backend_python ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.api.main import app
from app.core.auth import create_access_token
from app.core.config import settings
from app.db.database import init_db, SessionLocal
from app.db.models import Campaign, Lead, Diagnostic, Setting

settings.AUTH_SECRET = "api-endpoint-test-secret"
client = TestClient(
    app,
    headers={"Authorization": f"Bearer {create_access_token('api-test', 'diretoria')}"},
)

def run_tests():
    print("=" * 70)
    print("🧪 INICIANDO TESTES DE INTEGRAÇÃO DA API FASTAPI (PYTHON)")
    print("=" * 70)

    # 0. Inicializa banco
    init_db()
    db = SessionLocal()
    print("✅ 0. Banco de dados inicializado com sucesso.")

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check falhou: {res.text}"
    assert res.json().get("status") == "ok"
    print("✅ 1. GET /api/health -> OK")

    # 2. Dashboard stats
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200, f"Dashboard stats falhou: {res.text}"
    data = res.json()
    assert "data" in data
    assert "crmStats" in data["data"]
    print("✅ 2. GET /api/dashboard/stats -> OK")

    # 3. Settings GET / POST
    res = client.post("/api/settings", json={"webhook_url": "https://meu-webhook.com/api", "tema": "dark"})
    assert res.status_code == 200, f"Settings POST falhou: {res.text}"
    assert res.json()["data"]["webhook_url"] == "https://meu-webhook.com/api"

    res = client.get("/api/settings")
    assert res.status_code == 200
    assert res.json()["data"]["webhook_url"] == "https://meu-webhook.com/api"
    print("✅ 3. GET / POST /api/settings -> OK")

    # 4. Criar dados de teste para Campanha e Leads
    test_camp_id = str(uuid.uuid4())
    camp = Campaign(
        id=test_camp_id,
        niche="Odontologia",
        location="Curitiba, PR",
        status="completed",
        total_leads=2
    )
    db.add(camp)

    lead1_id = str(uuid.uuid4())
    lead1 = Lead(
        id=lead1_id,
        campaign_id=test_camp_id,
        name="Clínica Sorriso Curitiba",
        category="Dentista",
        phone="(41) 99999-1111",
        website="https://clinicasorriso.com.br",
        address="Av. Batel, 1000 - Curitiba, PR",
        city="Curitiba",
        google_rating=4.8,
        google_reviews_count=95,
        has_website=1,
        pagespeed_score=65,
        has_instagram=1,
        instagram_url="https://instagram.com/clinicasorriso",
        dms=75,
        cos=60,
        priority="B",
        commercial_status="new"
    )
    db.add(lead1)

    lead2_id = str(uuid.uuid4())
    lead2 = Lead(
        id=lead2_id,
        campaign_id=test_camp_id,
        name="Dentista Dr. Silva",
        category="Dentista",
        phone="(41) 99999-2222",
        website=None,
        address="Rua XV de Novembro, 500 - Curitiba, PR",
        city="Curitiba",
        google_rating=3.9,
        google_reviews_count=12,
        has_website=0,
        pagespeed_score=None,
        has_instagram=0,
        dms=25,
        cos=85,
        priority="A",
        commercial_status="new"
    )
    db.add(lead2)
    db.commit()
    print("✅ 4. Inserção de dados de teste -> OK")

    # 5. Listar campanhas
    res = client.get("/api/campaigns")
    assert res.status_code == 200
    camps = res.json().get("data", [])
    assert any(c["id"] == test_camp_id for c in camps)
    print(f"✅ 5. GET /api/campaigns -> OK ({len(camps)} campanhas listadas)")

    # 6. Detalhes de campanha
    res = client.get(f"/api/campaigns/{test_camp_id}")
    assert res.status_code == 200
    assert res.json()["data"]["niche"] == "Odontologia"
    print(f"✅ 6. GET /api/campaigns/{test_camp_id} -> OK")

    # 7. Stats da campanha
    res = client.get(f"/api/campaigns/{test_camp_id}/stats")
    assert res.status_code == 200
    cstats = res.json()["data"]
    assert cstats["total_leads"] == 2
    assert cstats["priority_a"] == 1
    assert cstats["priority_b"] == 1
    print(f"✅ 7. GET /api/campaigns/{test_camp_id}/stats -> OK")

    # 8. Listar leads da campanha
    res = client.get(f"/api/campaigns/{test_camp_id}/leads")
    assert res.status_code == 200
    leads_res = res.json()
    assert leads_res["total"] == 2
    print(f"✅ 8. GET /api/campaigns/{test_camp_id}/leads -> OK (2 leads)")

    # 8b. Filtro de prioridade
    res = client.get(f"/api/campaigns/{test_camp_id}/leads?priority=A")
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert res.json()["data"][0]["priority"] == "A"
    print(f"✅ 8b. GET /api/campaigns/{test_camp_id}/leads?priority=A -> OK (Filtro validado)")

    # 9. Detalhes do lead
    res = client.get(f"/api/leads/{lead1_id}")
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Clínica Sorriso Curitiba"
    print(f"✅ 9. GET /api/leads/{lead1_id} -> OK")

    # 10. Exportação CSV de leads
    res = client.get(f"/api/campaigns/{test_camp_id}/leads/export")
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")
    assert "Clínica Sorriso Curitiba" in res.text
    print(f"✅ 10. GET /api/campaigns/{test_camp_id}/leads/export -> OK (CSV gerado com sucesso)")

    # 11. Gerar diagnóstico para lead
    res = client.post(f"/api/leads/{lead2_id}/diagnostic")
    assert res.status_code in (201, 200), f"Diagnóstico falhou: {res.text}"
    diag_data = res.json().get("data", {})
    assert diag_data.get("lead_id") == lead2_id
    assert diag_data.get("diagnostic_status") == "completed"
    print(f"✅ 11. POST /api/leads/{lead2_id}/diagnostic -> OK (Diagnóstico gerado)")

    # 12. Consultar diagnóstico gerado
    res = client.get(f"/api/leads/{lead2_id}/diagnostic")
    assert res.status_code == 200
    assert res.json()["data"]["lead_id"] == lead2_id
    print(f"✅ 12. GET /api/leads/{lead2_id}/diagnostic -> OK")

    # 13. Limpeza dos dados de teste
    db.delete(lead1)
    db.delete(lead2)
    db.delete(camp)
    db.commit()
    db.close()
    print("✅ 13. Limpeza de dados de teste -> OK")

    print("\n" + "=" * 70)
    print("🎉 TODOS OS 13 TESTES DE API FORAM EXECUTADOS COM 100% DE SUCESSO!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_tests()
