import asyncio
import time
import sys
import os
import json

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.models.lead import LeadSearchParams, LeadResult
from app.integrations.google_places import GooglePlacesIntegration
from app.integrations.pagespeed import PageSpeedIntegration
from app.integrations.domain_checker import DomainSecurityIntegration
from app.integrations.instagram import InstagramIntegration
from app.integrations.claude_ai import ClaudeAIIntegration
from app.integrations.stitch import GoogleStitchIntegration

from app.services.triage_service import TriageService
from app.services.diagnosis_service import DiagnosisService
from app.services.site_service import SiteService


async def run_end_to_end_demo():
    print("=" * 80)
    print("🚀 DEMONSTRAÇÃO PONTA A PONTA (END-TO-END) — AUTOMAÇÃO GP")
    print("=" * 80)

    target_keyword = sys.argv[1] if len(sys.argv) > 1 else "Clínica Odontológica"
    target_location = sys.argv[2] if len(sys.argv) > 2 else "São Paulo, SP"
    override_website = sys.argv[3] if len(sys.argv) > 3 else None

    start_total_time = time.time()
    api_status_log = {}
    stage_times = {}
    estimated_cost_usd = 0.0

    # -------------------------------------------------------------------------
    # ETAPA 1: BUSCA DE LEADS NO GOOGLE PLACES
    # -------------------------------------------------------------------------
    print(f"\n📍 [ETAPA 1/5] Busca de Leads no Google Places API (New)")
    print(f"   • Palavra-chave: '{target_keyword}' | Localização: '{target_location}'")

    t0 = time.time()
    places_client = GooglePlacesIntegration()

    if places_client.api_key:
        api_status_log["Google Places API"] = "LIVE (Ao Vivo)"
        estimated_cost_usd += 0.00  # Covered by Google Cloud $200 free monthly credit
    else:
        api_status_log["Google Places API"] = "MOCK (Demonstração Sem Chave)"

    search_params = LeadSearchParams(keyword=target_keyword, location=target_location, max_results=1)
    leads = await places_client.search_leads(search_params)

    if not leads:
        print("   ⚠️ Nenhum lead real encontrado pela busca. Encerrando a demonstração sem inventar dados.")
        return

    lead = leads[0]

    # If user passed a specific real website for live testing, attach it to the lead
    if override_website and override_website != "auto":
        lead.website_uri = override_website

    t1 = time.time()
    stage_times["Etapa 1: Busca de Lead"] = round(t1 - t0, 3)

    print(f"   ✅ Lead retornado:")
    print(f"      - Nome: {lead.name}")
    print(f"      - ID do Place: {lead.place_id}")
    print(f"      - Endereço: {lead.formatted_address}")
    print(f"      - Telefone: {lead.national_phone_number}")
    print(f"      - Website: {lead.website_uri}")
    print(f"      - Avaliação: ⭐ {lead.rating} ({lead.user_rating_count} avaliações)")
    print(f"   ⏱️ Tempo da etapa: {stage_times['Etapa 1: Busca de Lead']}s")

    # -------------------------------------------------------------------------
    # ETAPA 2: TRIAGEM DIGITAL (PAGESPEED, SSL/DOMÍNIO, INSTAGRAM)
    # -------------------------------------------------------------------------
    print(f"\n🔍 [ETAPA 2/5] Triagem Digital Concorrente")
    print(f"   • Testando site real: {lead.website_uri}")

    t0 = time.time()

    # 2.1 PageSpeed (Live HTTP Call to Google PageSpeed Insights API)
    print("   [2.1] Executando Google PageSpeed Insights API...")
    ps_client = PageSpeedIntegration()
    if ps_client.api_key:
        api_status_log["Google PageSpeed API"] = "LIVE (Com Chave)"
    else:
        api_status_log["Google PageSpeed API"] = "LIVE (Sem Chave - Cota Gratuita Pública)"

    pagespeed_result = await ps_client.check_performance(lead.website_uri)
    print(f"         - Performance Score: {pagespeed_result.performance_score}/100")
    print(f"         - SEO Score: {pagespeed_result.seo_score}/100")
    print(f"         - Mobile Friendly: {'Sim ✅' if pagespeed_result.mobile_friendly else 'Não ❌'}")
    if pagespeed_result.error:
        print(f"         - Obs: {pagespeed_result.error}")

    # 2.2 SSL / Socket / DNS (100% Native Python - 100% Free Live Check)
    print("   [2.2] Verificando SSL, Socket Latency e DNS (Python Nativo)...")
    domain_client = DomainSecurityIntegration()
    api_status_log["SSL / Socket / DNS Check"] = "LIVE (Nativo 100% Gratuito)"

    security_result = await domain_client.verify_domain(lead.website_uri)
    print(f"         - Domínio Resolvido: {'Sim ✅' if security_result.dns_resolved else 'Não ❌'}")
    print(f"         - Possui SSL Válido: {'Sim ✅' if security_result.ssl_valid else 'Não ❌'}")
    print(f"         - Emissor do Certificado: {security_result.ssl_issuer or 'N/A'}")
    print(f"         - Dias para Expiração do SSL: {security_result.days_to_expiration or 'N/A'} dias")
    if security_result.error:
        print(f"         - Erro/Aviso: {security_result.error}")

    # 2.3 Instagram Triage
    print("   [2.3] Analisando perfil do Instagram...")
    insta_client = InstagramIntegration()
    if settings.META_GRAPH_ACCESS_TOKEN:
        api_status_log["Instagram Meta Graph API"] = "LIVE (Oficial)"
    elif settings.RAPIDAPI_KEY:
        api_status_log["Instagram Meta Graph API"] = "LIVE (Fallback RapidAPI)"
        estimated_cost_usd += 0.005
    else:
        api_status_log["Instagram Meta Graph API"] = "MOCK (Sem Credenciais)"

    insta_result = await insta_client.get_instagram_profile(lead.name)
    print(f"         - Handle: @{insta_result.handle}")
    print(f"         - Conta Comercial: {'Sim ✅' if insta_result.is_business_account else 'Não'}")
    print(f"         - Seguidores: {insta_result.followers_count or 'N/A'}")
    print(f"         - Provedor Utilizado: {insta_result.provider_used}")

    t1 = time.time()
    stage_times["Etapa 2: Triagem Digital"] = round(t1 - t0, 3)
    print(f"   ⏱️ Tempo da etapa: {stage_times['Etapa 2: Triagem Digital']}s")

    # Assemble full triage report
    from app.models.triage import FullTriageReport
    needs_site = (
        not lead.website_uri
        or (pagespeed_result.performance_score and pagespeed_result.performance_score < 50)
        or not security_result.ssl_valid
    )
    triage_report = FullTriageReport(
        lead=lead,
        pagespeed=pagespeed_result,
        security=security_result,
        instagram=insta_result,
        needs_new_website=needs_site,
    )

    # -------------------------------------------------------------------------
    # ETAPA 3 & 4: DIAGNÓSTICO E PROMPT STITCH VIA CLAUDE AI
    # -------------------------------------------------------------------------
    print(f"\n🧠 [ETAPAS 3 e 4] Diagnóstico & Geração de Prompt via Anthropic Claude AI (Haiku 4.5)")
    t0 = time.time()

    claude_client = ClaudeAIIntegration()
    if claude_client.client:
        api_status_log["Claude AI (Haiku 4.5)"] = "LIVE (Ao Vivo)"
        estimated_cost_usd += 0.0015  # ~1.5 cents per MTok output
    else:
        api_status_log["Claude AI (Haiku 4.5)"] = "MOCK (Motor Heurístico Local Gratuito)"

    diagnosis_service = DiagnosisService(llm=claude_client)
    diagnosis_res, stitch_prompt_res = await diagnosis_service.run_diagnosis_and_prompt(triage_report)

    t1 = time.time()
    stage_times["Etapas 3 & 4: Diagnóstico + Prompt AI"] = round(t1 - t0, 3)

    print(f"   ✅ Diagnóstico Gerado:")
    print(f"      - Resumo: {diagnosis_res.overall_summary}")
    print(f"      - Precisa de novo site: {'SIM ⚠️' if diagnosis_res.needs_new_website else 'NÃO ✅'}")
    print(f"      - Recomendações ({len(diagnosis_res.recommendations)} itens):")
    for r in diagnosis_res.recommendations:
        print(f"        • [{r.severity}] {r.category}: {r.finding} -> Ação: {r.action_item}")

    if stitch_prompt_res:
        print(f"\n   📝 Prompt Estruturado Gerado para o Google Stitch:")
        print(f"      --------------------------------------------------")
        print(f"      \"{stitch_prompt_res.stitch_prompt}\"")
        print(f"      --------------------------------------------------")
        print(f"      - Componentes Sugeridos: {', '.join(stitch_prompt_res.suggested_components)}")
        print(f"      - Identidade Visual: {stitch_prompt_res.brand_identity}")

    print(f"   ⏱️ Tempo da etapa: {stage_times['Etapas 3 & 4: Diagnóstico + Prompt AI']}s")

    # -------------------------------------------------------------------------
    # ETAPA 5: GERAÇÃO DO SITE VIA GOOGLE STITCH API
    # -------------------------------------------------------------------------
    print(f"\n🎨 [ETAPA 5/5] Geração do Site via Google Stitch API / SDK")
    t0 = time.time()

    stitch_client = GoogleStitchIntegration()
    if stitch_client.api_key:
        api_status_log["Google Stitch API"] = "LIVE (Beta Gratuito Google Labs)"
    else:
        api_status_log["Google Stitch API"] = "MOCK (Gerador de Demonstração HTML)"

    site_service = SiteService(generator=stitch_client)
    prompt_text = stitch_prompt_res.stitch_prompt if stitch_prompt_res else "Create a modern landing page"
    site_result = await site_service.generate_site_for_lead(lead.name, prompt_text)

    t1 = time.time()
    stage_times["Etapa 5: Geração de Site (Stitch)"] = round(t1 - t0, 3)

    print(f"   ✅ Resultado da Geração:")
    print(f"      - ID do Projeto Stitch: {site_result.project_id}")
    print(f"      - Status: {site_result.status}")
    print(f"      - URL de Preview: {site_result.preview_url}")
    print(f"      - Tamanho do HTML Gerado: {len(site_result.html_content or '')} bytes")
    print(f"   ⏱️ Tempo da etapa: {stage_times['Etapa 5: Geração de Site (Stitch)']}s")

    # -------------------------------------------------------------------------
    # PAINEL RESUMO FINAL (EXIGIDO PELO CEO)
    # -------------------------------------------------------------------------
    total_time = round(time.time() - start_total_time, 3)
    estimated_cost_brl = round(estimated_cost_usd * 5.60, 4)

    print("\n" + "=" * 80)
    print("📊 PAINEL DE AVALIAÇÃO DE DESEMPENHO E CUSTOS DA DEMONSTRAÇÃO")
    print("=" * 80)

    print("\n1. STATUS DAS INTEGRAÇÕES E MOCKS:")
    for service, status in api_status_log.items():
        print(f"   • {service:<30}: {status}")

    print("\n2. TEMPO DE PROCESSAMENTO POR ETAPA:")
    for stage_name, duration in stage_times.items():
        print(f"   • {stage_name:<40}: {duration}s")
    print(f"   ⏱️ TEMPO TOTAL DE PROCESSAMENTO COMPLETO: {total_time}s")

    print("\n3. ESTIMATIVA DE CUSTO RECORRENTE POR LEAD:")
    print(f"   • Google Places (New): R$ 0,00 (Gratuito até 10.000 buscas/mês no limite de $200)")
    print(f"   • PageSpeed Insights: R$ 0,00 (100% Gratuito até 25.000 req/dia)")
    print(f"   • Verificação SSL/DNS/Socket: R$ 0,00 (100% Gratuito - Python nativo)")
    print(f"   • Claude AI (Haiku 4.5): ~R$ 0,008 por lead processado")
    print(f"   • Google Stitch API: R$ 0,00 (Fase Beta Gratuita)")
    print(f"   💰 CUSTO TOTAL APROXIMADO POR LEAD: R$ {estimated_cost_brl:.4f} (Aproximadamente R$ 0,01 / lead)")

    print("\n" + "=" * 80)
    print("✅ DEMONSTRAÇÃO PONTA A PONTA CONCLUÍDA COM SUCESSO!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_end_to_end_demo())
