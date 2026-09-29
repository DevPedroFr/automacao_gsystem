"""
Router /api/leads/:leadId/diagnostic — Geração e consulta de diagnósticos via Claude AI.
Porta fiel das rotas do backend Node.js (routes/diagnostics.js).
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Lead, Diagnostic
from app.integrations.claude_ai import ClaudeAIIntegration
from app.integrations.gemini_ai import GeminiAIIntegration
from app.models.triage import FullTriageReport
from app.models.lead import LeadResult

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Diagnósticos"])


import json
from fastapi.responses import HTMLResponse

def _diag_to_dict(d: Diagnostic) -> dict:
    brand_colors_parsed = None
    if getattr(d, "brand_colors", None):
        try:
            brand_colors_parsed = json.loads(d.brand_colors)
        except Exception:
            pass

    owners_info_parsed = None
    if getattr(d, "owners_info", None):
        try:
            owners_info_parsed = json.loads(d.owners_info)
        except Exception:
            pass

    # Diagnóstico Consultivo 360°
    blunders_parsed = None
    if getattr(d, "critical_blunders", None):
        try:
            blunders_parsed = json.loads(d.critical_blunders)
        except Exception:
            pass

    matrix_parsed = None
    if getattr(d, "transformation_matrix", None):
        try:
            matrix_parsed = json.loads(d.transformation_matrix)
        except Exception:
            pass

    revenue_parsed = None
    if getattr(d, "revenue_leak", None):
        try:
            revenue_parsed = json.loads(d.revenue_leak)
        except Exception:
            pass

    has_site = bool(getattr(d, "generated_site_html", None))

    return {
        "id": d.id,
        "lead_id": d.lead_id,
        "observed_facts": d.observed_facts,
        "inferences": d.inferences,
        "recommendations": d.recommendations,
        # Estratégia de vendas
        "sales_approach": getattr(d, "sales_approach", None),
        "pain_points": getattr(d, "pain_points", None),
        "talking_points": getattr(d, "talking_points", None),
        "value_proposition": getattr(d, "value_proposition", None),
        # Rascunhos de mensagens
        "email_draft": d.email_draft,
        "whatsapp_draft": d.whatsapp_draft,
        "instagram_draft": d.instagram_draft,
        "stitch_prompt": d.stitch_prompt,
        # Diagnóstico Consultivo 360°
        "critical_blunders": blunders_parsed,
        "transformation_matrix": matrix_parsed,
        "revenue_leak": revenue_parsed,
        "niche_insights": getattr(d, "niche_insights", None),
        # Landing Page & Ativos
        "brand_colors": brand_colors_parsed,
        "owners_info": owners_info_parsed,
        "logo_url": getattr(d, "logo_url", None),
        "has_generated_site": has_site,
        "preview_url": f"/api/leads/{d.lead_id}/lp-preview" if has_site else None,
        "diagnostic_status": d.diagnostic_status,
        "error_message": d.error_message,
        "generated_at": d.generated_at.isoformat() if d.generated_at else None,
    }



@router.post("/api/leads/{lead_id}/diagnostic", status_code=201, summary="Gera diagnóstico de um lead via IA")
async def generate_diagnostic(lead_id: str, db: Session = Depends(get_db)):
    """
    POST /api/leads/:leadId/diagnostic
    Gera (ou regenera) o diagnóstico inteligente do lead usando Gemini AI.
    Sempre substitui diagnóstico anterior para garantir dados frescos e completos.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Lead não encontrado"})

    # Sempre remove diagnóstico anterior para permitir regenerar com o formato rico
    existing = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    if existing:
        db.delete(existing)
        db.commit()

    lead_result = LeadResult(
        place_id=lead.id,
        name=lead.name,
        formatted_address=lead.address or lead.city or "",
        national_phone_number=lead.phone,
        website_uri=lead.website,
        rating=lead.google_rating,
        user_rating_count=lead.google_reviews_count,
        category=lead.category,
        city=lead.city,
    )


    try:
        from app.services.diagnosis_service import DiagnosisService
        from app.models.triage import FullTriageReport, PageSpeedResult, DomainSecurityResult, InstagramProfileResult

        pagespeed = PageSpeedResult(
            url=lead.website or "",
            performance_score=lead.pagespeed_score,
            seo_score=lead.seo_score,
            mobile_friendly=bool(lead.has_website),
        )
        security = DomainSecurityResult(
            domain=lead.website or "",
            dns_resolved=bool(lead.website),
            ssl_valid=False,
            is_domain_active=bool(lead.website),
        )
        
        # Extract handle from URL if possible
        ig_handle = lead.name
        if lead.instagram_url:
            parts = lead.instagram_url.split("instagram.com/")
            if len(parts) > 1:
                ig_handle = parts[1].split("/")[0].strip()
        
        instagram = InstagramProfileResult(
            handle=ig_handle,
            found=bool(lead.has_instagram),
            is_business_account=bool(lead.has_instagram),
            followers_count=None,
            provider_used="db",
        )

        report = FullTriageReport(
            lead=lead_result,
            pagespeed=pagespeed,
            security=security,
            instagram=instagram,
            needs_new_website=not bool(lead.website) or (lead.pagespeed_score or 100) < 50,
        )

        if settings.GEMINI_API_KEY or settings.AI_PROVIDER == "gemini":
            ai_client = GeminiAIIntegration()
        else:
            ai_client = ClaudeAIIntegration()
            
        diag_service = DiagnosisService(llm=ai_client)
        diagnosis_res, stitch_prompt_res = await diag_service.run_diagnosis_and_prompt(report)

        diag_id = str(uuid.uuid4())

        # Formata fatos observados por pilar com tags [GOOGLE], [WEBSITE], [SOCIAL]
        facts_lines = []
        if diagnosis_res.facts:
            for fact in diagnosis_res.facts:
                facts_lines.append(f"[{fact.pilar.upper()}] {fact.text}")
        observed_facts_text = "\n".join(facts_lines) if facts_lines else diagnosis_res.overall_summary

        # Formata inferências por pilar
        inferences_lines = []
        if diagnosis_res.inferences:
            for inf in diagnosis_res.inferences:
                inferences_lines.append(f"[{inf.pilar.upper()}] {inf.text}")
        inferences_text = "\n".join(inferences_lines) if inferences_lines else None

        # Formata recomendações técnicas
        rec_text = "\n".join(
            f"[{r.severity}] {r.category}: {r.finding} → {r.action_item}"
            for r in diagnosis_res.recommendations
        ) if diagnosis_res.recommendations else None

        # Estratégia de venda consultiva
        sales = diagnosis_res.sales_recommendation
        sales_approach = sales.approach_angle if sales else None
        pain_points_text = "\n".join(f"- {p}" for p in sales.pain_points) if sales else None
        talking_points_text = "\n".join(f"- {t}" for t in sales.talking_points) if sales else None
        value_prop = sales.value_proposition if sales else None

        # Serializar novos campos do Diagnóstico Consultivo 360°
        blunders_json = None
        if diagnosis_res.critical_blunders:
            blunders_json = json.dumps([b.model_dump() for b in diagnosis_res.critical_blunders], ensure_ascii=False)

        matrix_json = None
        if diagnosis_res.transformation_matrix:
            matrix_json = json.dumps([t.model_dump() for t in diagnosis_res.transformation_matrix], ensure_ascii=False)

        revenue_json = None
        if diagnosis_res.revenue_leak:
            revenue_json = json.dumps(diagnosis_res.revenue_leak.model_dump(), ensure_ascii=False)

        diagnostic = Diagnostic(
            id=diag_id,
            lead_id=lead_id,
            observed_facts=observed_facts_text,
            inferences=inferences_text,
            recommendations=rec_text,
            sales_approach=sales_approach,
            pain_points=pain_points_text,
            talking_points=talking_points_text,
            value_proposition=value_prop,
            email_draft=diagnosis_res.email_draft,
            whatsapp_draft=diagnosis_res.whatsapp_draft,
            instagram_draft=diagnosis_res.instagram_draft,
            stitch_prompt=stitch_prompt_res.stitch_prompt if stitch_prompt_res else None,
            critical_blunders=blunders_json,
            transformation_matrix=matrix_json,
            revenue_leak=revenue_json,
            niche_insights=diagnosis_res.niche_insights,
            diagnostic_status="completed",
            generated_at=datetime.utcnow(),
        )
        db.add(diagnostic)
        db.commit()
        db.refresh(diagnostic)

        return {"data": _diag_to_dict(diagnostic)}

    except Exception as err:
        logger.error(f"Erro ao gerar diagnóstico para lead {lead_id}: {err}")
        diag_id = str(uuid.uuid4())
        diagnostic = Diagnostic(
            id=diag_id,
            lead_id=lead_id,
            diagnostic_status="ai_validation_failed",
            error_message=str(err),
            generated_at=datetime.utcnow(),
        )
        db.add(diagnostic)
        db.commit()
        raise HTTPException(status_code=500, detail={"error": "diagnosis_error", "message": str(err)})


@router.get("/api/leads/{lead_id}/diagnostic", summary="Consulta diagnóstico de um lead")
def get_diagnostic(lead_id: str, db: Session = Depends(get_db)):
    """GET /api/leads/:leadId/diagnostic — Retorna o diagnóstico existente."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Lead não encontrado"})

    diagnostic = None
    try:
        diagnostic = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    except Exception as e:
        logger.error(f"Erro ao buscar diagnóstico para o lead {lead_id}: {e}")
        db.rollback()

    if not diagnostic:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "Diagnóstico não gerado ainda. Use POST para gerar."},
        )
    return {"data": _diag_to_dict(diagnostic)}


class GenerateLPPayload(BaseModel):
    archetype_id: Optional[str] = None


@router.get("/api/design-archetypes", summary="Lista modelos e arquétipos de design de inspiração")
@router.get("/design-archetypes", include_in_schema=False)
def get_design_archetypes():
    """GET /api/design-archetypes — Retorna os modelos de inspiração arquitetural."""
    from app.services.design_archetypes import DesignArchetypes
    return {"data": DesignArchetypes.list_archetypes()}


@router.post("/api/leads/{lead_id}/generate-lp", summary="Gera a Landing Page sob medida a partir do diagnóstico")
@router.post("/leads/{lead_id}/generate-lp", include_in_schema=False)
async def generate_landing_page(
    lead_id: str,
    payload: Optional[GenerateLPPayload] = None,
    archetype: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    POST /api/leads/:leadId/generate-lp
    1. Busca o diagnóstico e dados do lead.
    2. Executa o enriquecimento de ativos (cores da marca, fotos, busca de sócios).
    3. Constrói o Meta-Prompt de Elite baseado nas regras de nicho e nas dores identificadas.
    4. Gera o código HTML completo e responsivo (Tailwind CSS) e salva no banco.
    """
    from app.services.enrichment_service import EnrichmentService
    from app.services.lp_prompt_engine import LPPromptEngine
    from app.services.site_generator_service import SiteGeneratorService

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Lead não encontrado"})

    diagnostic = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    if not diagnostic:
        raise HTTPException(
            status_code=400,
            detail={"error": "diagnostic_required", "message": "Gere primeiro o diagnóstico antes de criar a Landing Page."},
        )

    try:
        # 1. Enriquecimento de Dados (Cores, Sócios, Logo)
        enrichment = await EnrichmentService.enrich_lead_data(
            lead_name=lead.name,
            city=lead.city or "",
            website_url=lead.website,
            instagram_bio=lead.name,
            logo_url_or_path=lead.logo_url or lead.image_url,
            reviews_text=diagnostic.observed_facts,
        )

        brand_colors = enrichment["brand_colors"]
        owners = enrichment["owners"]
        cnpj = enrichment["cnpj"]

        # Atualiza Lead se achou CNPJ ou Sócios
        if cnpj and not lead.cnpj:
            lead.cnpj = cnpj
        if owners and not lead.owners_info:
            lead.owners_info = json.dumps(owners)

        # 2. Constrói o Prompt de Elite customizado por Nicho
        lead_dict = {
            "name": lead.name,
            "category": lead.category,
            "phone": lead.phone,
            "address": lead.address,
            "city": lead.city,
            "google_rating": lead.google_rating,
            "google_reviews_count": lead.google_reviews_count,
        }
        diagnostic_dict = {
            "pain_points": diagnostic.pain_points,
            "value_proposition": diagnostic.value_proposition,
            "sales_approach": diagnostic.sales_approach,
            "talking_points": diagnostic.talking_points,
            "niche_insights": getattr(diagnostic, "niche_insights", None),
        }

        # Injetar gafes detectadas no contexto do gerador de LP
        blunders_parsed = None
        if getattr(diagnostic, "critical_blunders", None):
            try:
                blunders_parsed = json.loads(diagnostic.critical_blunders)
            except Exception:
                pass
        if blunders_parsed:
            diagnostic_dict["critical_blunders"] = blunders_parsed

        # Determina o arquétipo visual (modelo de inspiração)
        chosen_archetype = (payload.archetype_id if payload else None) or archetype
        if not chosen_archetype or chosen_archetype == "auto":
            niche_key = LPPromptEngine.detect_niche(lead.name, lead.category)
            if niche_key == "construcao":
                chosen_archetype = "showcase_catalog"
            elif niche_key == "advocacia":
                chosen_archetype = "clean_editorial"
            elif niche_key in ["odontologia", "medicina"]:
                chosen_archetype = "authority_proof"
            elif niche_key == "automotivo":
                chosen_archetype = "split_dynamic"
            else:
                chosen_archetype = "cro_high_impact"

        custom_prompt = LPPromptEngine.build_custom_prompt(
            lead_data=lead_dict,
            diagnostic_data=diagnostic_dict,
            brand_colors=brand_colors,
            owners_info=owners,
            logo_url=lead.logo_url or lead.image_url,
            archetype_id=chosen_archetype,
        )

        # Salva o prompt customizado
        diagnostic.stitch_prompt = custom_prompt
        diagnostic.brand_colors = json.dumps(brand_colors)
        if owners:
            diagnostic.owners_info = json.dumps(owners)

        # 3. Gera o Código HTML Completo
        html_code = await SiteGeneratorService.generate_landing_page_html(
            prompt=custom_prompt,
            lead_data=lead_dict,
            brand_colors=brand_colors,
            owners=owners,
            logo_url=lead.logo_url or lead.image_url,
            diagnostic_data=diagnostic_dict,
            archetype_id=chosen_archetype,
        )

        diagnostic.generated_site_html = html_code
        db.commit()
        db.refresh(diagnostic)

        return {
            "status": "success",
            "message": "Landing Page gerada com sucesso sob medida!",
            "data": _diag_to_dict(diagnostic),
        }
    except Exception as err:
        logger.error(f"Erro ao gerar Landing Page para o lead {lead_id}: {err}")
        db.rollback()
        raise HTTPException(status_code=500, detail={"error": "site_generation_failed", "message": str(err)})


@router.get("/api/leads/{lead_id}/lp-preview", summary="Visualiza a Landing Page gerada pelo lead", response_class=HTMLResponse)
@router.get("/leads/{lead_id}/lp-preview", response_class=HTMLResponse, include_in_schema=False)
def preview_landing_page(lead_id: str, db: Session = Depends(get_db)):
    """GET /api/leads/:leadId/lp-preview — Renderiza o HTML da Landing Page gerada."""
    diagnostic = db.query(Diagnostic).filter(Diagnostic.lead_id == lead_id).first()
    if not diagnostic or not diagnostic.generated_site_html:
        return HTMLResponse(
            content="""<!DOCTYPE html>
            <html class="dark">
            <head><title>Landing Page não gerada</title><script src="https://cdn.tailwindcss.com"></script></head>
            <body class="bg-gray-950 text-white flex items-center justify-center min-h-screen">
                <div class="p-8 bg-gray-900 border border-gray-800 rounded-2xl text-center max-w-md shadow-2xl">
                    <div class="text-4xl mb-4">⏳</div>
                    <h2 class="text-xl font-bold mb-2">Landing Page ainda não foi gerada</h2>
                    <p class="text-gray-400 text-sm mb-6">Abra o diagnóstico deste lead no CRM e clique no botão <strong>"🚀 Gerar Landing Page Sob Medida"</strong>.</p>
                </div>
            </body>
            </html>""",
            status_code=404,
        )

    return HTMLResponse(content=diagnostic.generated_site_html, status_code=200)


