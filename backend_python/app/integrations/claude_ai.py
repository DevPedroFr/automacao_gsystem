import json
from typing import Optional

try:
    import anthropic
except ImportError:
    anthropic = None

from app.core.config import settings
from app.core.interfaces.llm_service import LLMService
from app.models.triage import FullTriageReport
from app.models.diagnosis import (
    DiagnosisResult, DiagnosticFact, DiagnosticInference,
    RecommendationItem, SalesRecommendation, StitchPromptResult
)


class ClaudeAIIntegration(LLMService):
    """[Etapa 3 & 4] Anthropic Claude API Integration (Haiku 4.5)."""

    def _build_local_diagnosis(self, report: FullTriageReport) -> DiagnosisResult:
        lead = report.lead
        ps = report.pagespeed
        sec = report.security
        ig = report.instagram

        needs_new_site = (
            lead.website_uri is None
            or (ps and ps.performance_score and ps.performance_score < 50)
            or (sec and not sec.ssl_valid)
        )

        facts = []
        inferences = []
        recommendations = []

        if lead.rating:
            facts.append(DiagnosticFact(pilar="google", text=f"Avaliação no Google: {lead.rating}/5.0 com {lead.user_rating_count or 0} avaliações."))
            inferences.append(DiagnosticInference(pilar="google", text="Excelente autoridade de marca no Google Maps."))
        if lead.national_phone_number:
            facts.append(DiagnosticFact(pilar="google", text=f"Telefone cadastrado: {lead.national_phone_number}."))
        if lead.formatted_address:
            facts.append(DiagnosticFact(pilar="google", text=f"Endereço: {lead.formatted_address}."))

        if not lead.website_uri:
            facts.append(DiagnosticFact(pilar="website", text="Nenhum site cadastrado no Google Empresa."))
            inferences.append(DiagnosticInference(pilar="website", text="Falta de site próprio gera perda diária de leads para concorrentes."))
            recommendations.append(RecommendationItem(
                category="Website", severity="HIGH",
                finding="O lead não possui site cadastrado.",
                action_item="Criar uma landing page de alta conversão.",
            ))
        elif ps:
            facts.append(DiagnosticFact(pilar="website", text=f"Site ativo: {lead.website_uri}. PageSpeed: {ps.performance_score}/100."))

        if ig and (ig.found or ig.is_business_account):
            facts.append(DiagnosticFact(pilar="social", text=f"Instagram ativo: @{ig.handle}."))
        else:
            facts.append(DiagnosticFact(pilar="social", text="Nenhum perfil oficial de Instagram identificado."))

        sales_rec = SalesRecommendation(
            approach_angle="Apresentar auditoria da presença digital demonstrando oportunidades imediatas de captação de clientes",
            pain_points=[
                "Perda de clientes que pesquisam pelo serviço no Google no celular",
                "Falta de canal próprio de captação funcionando 24h por dia",
                "Concorrentes locais com presença digital mais moderna e rápida",
            ],
            talking_points=[
                "Um site rápido e otimizado para celular converte até 3x mais visitantes em contatos no WhatsApp",
                "A excelente nota no Google já é uma prova de autoridade pronta para ser usada no site",
                "Landing page profissional fecha negócios fora do horário comercial",
            ],
            value_proposition=f"Construir uma presença digital moderna que converte buscas no Google em clientes reais para {lead.name}",
        )

        return DiagnosisResult(
            lead_name=lead.name,
            overall_summary=f"Auditoria de presença digital para {lead.name}.",
            recommendations=recommendations,
            needs_new_website=needs_new_site,
            facts=facts,
            inferences=inferences,
            sales_recommendation=sales_rec,
        )

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = settings.CLAUDE_MODEL
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key) if (anthropic and self.api_key) else None

    async def generate_diagnosis(self, report: FullTriageReport) -> DiagnosisResult:
        if not self.client:
            # Fallback mock diagnosis logic
            needs_new_site = (
                report.lead.website_uri is None
                or (report.pagespeed and report.pagespeed.performance_score and report.pagespeed.performance_score < 50)
                or (report.security and not report.security.ssl_valid)
            )

            recs = []
            if not report.lead.website_uri:
                recs.append(
                    RecommendationItem(
                        category="Website",
                        severity="HIGH",
                        finding="O lead não possui site cadastrado.",
                        action_item="Criar um site moderno e responsivo via Google Stitch.",
                    )
                )
            elif report.pagespeed and report.pagespeed.performance_score and report.pagespeed.performance_score < 50:
                recs.append(
                    RecommendationItem(
                        category="Performance",
                        severity="HIGH",
                        finding=f"Pontuação de velocidade baixa ({report.pagespeed.performance_score}/100).",
                        action_item="Refatorar a estrutura web ou gerar nova landing page otimizada.",
                    )
                )

            if report.security and not report.security.ssl_valid:
                recs.append(
                    RecommendationItem(
                        category="Segurança SSL",
                        severity="HIGH",
                        finding="Certificado SSL ausente ou expirado.",
                        action_item="Configurar HTTPS imediatamente para evitar bloqueios no navegador.",
                    )
                )

            return DiagnosisResult(
                lead_name=report.lead.name,
                overall_summary=f"Diagnóstico técnico completo para {report.lead.name}.",
                recommendations=recs,
                needs_new_website=needs_new_site,
            )

        prompt_system = (
            "Você é um consultor especialista em presença digital e engenharia web. "
            "Analise os dados técnicos do lead e retorne estritamente um JSON com a estrutura:\n"
            "{\n"
            '  "overall_summary": "...",\n'
            '  "needs_new_website": true/false,\n'
            '  "recommendations": [\n'
            '     {"category": "...", "severity": "HIGH/MEDIUM/LOW", "finding": "...", "action_item": "..."}\n'
            "  ]\n"
            "}"
        )

        user_content = f"Dados do Lead:\n{report.model_dump_json(indent=2)}"

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=prompt_system,
                messages=[{"role": "user", "content": user_content}],
            )
            raw_text = response.content[0].text
            data = json.loads(raw_text)
        except Exception:
            return self._build_local_diagnosis(report)

        recs = [RecommendationItem(**item) for item in data.get("recommendations", [])]
        return DiagnosisResult(
            lead_name=report.lead.name,
            overall_summary=data.get("overall_summary", ""),
            recommendations=recs,
            needs_new_website=data.get("needs_new_website", False),
        )

    async def generate_stitch_prompt(
        self, report: FullTriageReport, diagnosis: DiagnosisResult
    ) -> StitchPromptResult:
        from app.services.niche_profiles import (
            detect_niche_profile,
            build_impeccable_site_prompt,
            build_brand_identity_summary,
        )

        lead = report.lead
        category = getattr(lead, "category", None)
        profile = detect_niche_profile(lead.name, category, lead.formatted_address)

        if not self.client:
            fallback_prompt = build_impeccable_site_prompt(lead, profile, diagnosis)
            fallback_brand = build_brand_identity_summary(lead, profile, diagnosis)
            return StitchPromptResult(
                lead_name=lead.name,
                stitch_prompt=fallback_prompt,
                suggested_components=[
                    "HeroSectionWithSplitLayout",
                    "TrustBadgesRow",
                    "ServicesGridWithIconBadges",
                    "CompetitiveEdgeMatrix",
                    "GoogleReputationShowcase",
                    "InteractiveLocalMapAndHours",
                    "StickyMobileWhatsAppBar",
                    "CleanFooterWithLegalInfo"
                ],
                brand_identity=fallback_brand,
            )

        rating_info = (
            f"Nota {lead.rating}/5.0 baseada em {lead.user_rating_count or 0} avaliações reais verificadas no Google Maps"
            if lead.rating
            else "Negócio com reputação local em consolidação"
        )
        sales = diagnosis.sales_recommendation
        val_prop = sales.value_proposition if sales and sales.value_proposition else profile["sample_headline"]
        pain_points_txt = ", ".join(sales.pain_points) if sales and sales.pain_points else ", ".join(profile["pain_points"])
        talking_points_txt = ", ".join(sales.talking_points) if sales and sales.talking_points else ", ".join(profile["value_triggers"])

        system_prompt = (
            "Você é o Arquiteto Líder de UI/UX e Especialista Sênior em Otimização de Conversão (CRO) da Google e Stitch AI. "
            "Sua missão é gerar uma ESPECIFICAÇÃO DE PROMPT COMPLETA, CIRÚRGICA E ULTRA-DETALHADA em INGLÊS para gerar a Landing Page definitiva do negócio. "
            "O prompt NÃO pode ser genérico. Ele deve conter dados reais, paleta de cores HEX exatas, tipografia, seções modulares e botões de WhatsApp.\n\n"
            "Retorne estritamente um JSON no seguinte formato:\n"
            "{\n"
            '  "stitch_prompt": "O prompt técnico completo em inglês com todas as seções (Hero, Services, Differentials, Google Reviews, Map, Sticky WhatsApp) minuciosamente detalhadas",\n'
            '  "suggested_components": ["HeroSectionWithSplitLayout", "TrustBadgesRow", "ServicesGridWithIconBadges", "CompetitiveEdgeMatrix", "GoogleReputationShowcase", "InteractiveLocalMapAndHours", "StickyMobileWhatsAppBar", "CleanFooterWithLegalInfo"],\n'
            '  "brand_identity": "Resumo executivo em português da identidade da marca (paleta HEX, tom de voz, tipografia e proposta de valor)"\n'
            "}"
        )

        user_content = (
            f"Nome da Empresa: {lead.name}\n"
            f"Segmento de Atuação: {profile['niche_pt']} ({profile['industry_en']})\n"
            f"Público-Alvo: {profile['target_audience']}\n"
            f"Localização: {lead.formatted_address or lead.city or 'Brasil'}\n"
            f"WhatsApp / Telefone: {lead.national_phone_number or 'Disponível no botão'}\n"
            f"Reputação Google: {rating_info}\n"
            f"Proposta de Valor: {val_prop}\n"
            f"Dores do Consumidor: {pain_points_txt}\n"
            f"Diferenciais da Empresa: {talking_points_txt}\n"
            f"Diagnóstico Técnico: {diagnosis.overall_summary}\n"
            f"Paleta de Cores Recomendada: {profile['color_palette']}\n"
            f"Tipografia: {profile['typography']}\n"
        )

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            raw_text = response.content[0].text
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            data = json.loads(clean_text.strip())
            stitch_val = data.get("stitch_prompt", "").strip()
            if not stitch_val or len(stitch_val) < 250:
                stitch_val = build_impeccable_site_prompt(lead, profile, diagnosis)

            brand_val = data.get("brand_identity") or build_brand_identity_summary(lead, profile, diagnosis)
            components_val = data.get("suggested_components") or [
                "HeroSectionWithSplitLayout",
                "TrustBadgesRow",
                "ServicesGridWithIconBadges",
                "CompetitiveEdgeMatrix",
                "GoogleReputationShowcase",
                "InteractiveLocalMapAndHours",
                "StickyMobileWhatsAppBar",
                "CleanFooterWithLegalInfo"
            ]

            return StitchPromptResult(
                lead_name=lead.name,
                stitch_prompt=stitch_val,
                suggested_components=components_val,
                brand_identity=brand_val,
            )
        except Exception:
            fallback_prompt = build_impeccable_site_prompt(lead, profile, diagnosis)
            fallback_brand = build_brand_identity_summary(lead, profile, diagnosis)
            return StitchPromptResult(
                lead_name=lead.name,
                stitch_prompt=fallback_prompt,
                suggested_components=[
                    "HeroSectionWithSplitLayout",
                    "TrustBadgesRow",
                    "ServicesGridWithIconBadges",
                    "CompetitiveEdgeMatrix",
                    "GoogleReputationShowcase",
                    "InteractiveLocalMapAndHours",
                    "StickyMobileWhatsAppBar",
                    "CleanFooterWithLegalInfo"
                ],
                brand_identity=fallback_brand,
            )

