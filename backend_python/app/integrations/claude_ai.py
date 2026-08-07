import json
from typing import Optional

try:
    import anthropic
except ImportError:
    anthropic = None

from app.core.config import settings
from app.core.interfaces.llm_service import LLMService
from app.models.triage import FullTriageReport
from app.models.diagnosis import DiagnosisResult, RecommendationItem, StitchPromptResult


class ClaudeAIIntegration(LLMService):
    """[Etapa 3 & 4] Anthropic Claude API Integration (Haiku 4.5)."""

    def _build_local_diagnosis(self, report: FullTriageReport) -> DiagnosisResult:
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
            overall_summary=f"Diagnóstico técnico completo para {report.lead.name} (modo local).",
            recommendations=recs,
            needs_new_website=needs_new_site,
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
        if not self.client:
            return StitchPromptResult(
                lead_name=report.lead.name,
                stitch_prompt=(
                    f"Create a high-converting, modern landing page for '{report.lead.name}'. "
                    f"Location: {report.lead.formatted_address or 'Brasil'}. "
                    f"Include hero section, service overview, customer testimonials, and direct WhatsApp contact CTA. "
                    f"Style: Ultra sleek dark mode with vibrant accent colors."
                ),
                suggested_components=["Hero", "ServicesGrid", "Testimonials", "ContactForm", "Footer"],
                brand_identity=f"Profissional e moderno para {report.lead.name}",
            )

        system_prompt = (
            "Você é um engenheiro especialista em geração de UI via Google Stitch. "
            "Crie um prompt detalhado e estruturado para o Google Stitch criar um site incrível para o lead. "
            "Retorne um JSON com a estrutura:\n"
            "{\n"
            '  "stitch_prompt": "...",\n'
            '  "suggested_components": ["..."],\n'
            '  "brand_identity": "..."\n'
            "}"
        )

        user_content = (
            f"Lead: {report.lead.name}\n"
            f"Endereço: {report.lead.formatted_address}\n"
            f"Telefone: {report.lead.national_phone_number}\n"
            f"Diagnóstico: {diagnosis.overall_summary}\n"
        )

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            data = json.loads(response.content[0].text)
        except Exception:
            return StitchPromptResult(
                lead_name=report.lead.name,
                stitch_prompt=(
                    f"Create a high-converting, modern landing page for '{report.lead.name}'. "
                    f"Location: {report.lead.formatted_address or 'Brasil'}. "
                    f"Include hero section, service overview, customer testimonials, and direct WhatsApp contact CTA."
                ),
                suggested_components=["Hero", "ServicesGrid", "Testimonials", "ContactForm", "Footer"],
                brand_identity=f"Profissional e moderno para {report.lead.name}",
            )

        return StitchPromptResult(
            lead_name=report.lead.name,
            stitch_prompt=data.get("stitch_prompt", ""),
            suggested_components=data.get("suggested_components", []),
            brand_identity=data.get("brand_identity"),
        )
