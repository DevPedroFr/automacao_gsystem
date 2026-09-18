import json
from typing import Optional

import httpx

from app.core.config import settings
from app.core.interfaces.llm_service import LLMService
from app.models.diagnosis import DiagnosisResult, RecommendationItem, StitchPromptResult
from app.models.triage import FullTriageReport


class GeminiAIIntegration(LLMService):
    """Agente de IA para geração de diagnóstico e prompts para o Google Stitch via Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def _build_local_diagnosis(self, report: FullTriageReport) -> DiagnosisResult:
        needs_new_site = (
            report.lead.website_uri is None
            or (report.pagespeed and report.pagespeed.performance_score and report.pagespeed.performance_score < 50)
            or (report.security and not report.security.ssl_valid)
        )

        recommendations = []
        if not report.lead.website_uri:
            recommendations.append(
                RecommendationItem(
                    category="Website",
                    severity="HIGH",
                    finding="O lead não possui site cadastrado.",
                    action_item="Criar um site moderno e responsivo via Google Stitch.",
                )
            )
        elif report.pagespeed and report.pagespeed.performance_score and report.pagespeed.performance_score < 50:
            recommendations.append(
                RecommendationItem(
                    category="Performance",
                    severity="HIGH",
                    finding=f"Pontuação de velocidade baixa ({report.pagespeed.performance_score}/100).",
                    action_item="Refatorar a estrutura web ou gerar nova landing page otimizada.",
                )
            )

        if report.security and not report.security.ssl_valid:
            recommendations.append(
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
            recommendations=recommendations,
            needs_new_website=needs_new_site,
        )

    async def _call_gemini(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini API key not configured")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
            },
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return text or ""

    async def generate_diagnosis(self, report: FullTriageReport) -> DiagnosisResult:
        prompt = (
            "Você é o melhor consultor de vendas B2B do Brasil, especialista em vender criação de sites, automações e presença digital. "
            "Você vai analisar os dados deste lead e criar a CÓPIA DE VENDAS PERFEITA (copy) para abordar o cliente no frio (cold outreach). "
            "Seu objetivo com as mensagens é despertar extrema curiosidade e agendar uma reunião rápida. "
            "USE TÉCNICAS DE COPYWRITING: AIDA, SPIN Selling. "
            "AS MENSAGENS DEVEM SER OBRIGATORIAMENTE PERSONALIZADAS com o nome do negócio, Instagram ou cidade do cliente. "
            "Mostre que você estudou o negócio dele. Aponte um erro técnico específico (ex: 'vi que seu site está muito lento', ou 'vi que vocês não têm um site profissional no endereço XYZ...'). "
            "Retorne estritamente um JSON com a estrutura:"
            "{"
            "\"overall_summary\": \"...\", "
            "\"needs_new_website\": true/false, "
            "\"recommendations\": [{\"category\": \"...\", \"severity\": \"HIGH/MEDIUM/LOW\", \"finding\": \"...\", \"action_item\": \"...\"}], "
            "\"whatsapp_draft\": \"... (Mensagem de abordagem pelo WhatsApp, curta, amigável e direta ao ponto, usando emojis)\", "
            "\"email_draft\": \"... (Email formal mas persuasivo, com Assunto forte)\", "
            "\"instagram_draft\": \"... (Mensagem de direct curtíssima e intrigante)\""
            "}"
            f"\n\nDados do Lead:\n{report.model_dump_json(indent=2)}"
        )

        try:
            response_text = await self._call_gemini(prompt)
            # Remove possible markdown formatting from the response
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
        except Exception as e:
            print(f"Erro no parse do JSON da IA: {e}")
            return self._build_local_diagnosis(report)

        recs = [RecommendationItem(**item) for item in data.get("recommendations", [])]
        return DiagnosisResult(
            lead_name=report.lead.name,
            overall_summary=data.get("overall_summary", ""),
            recommendations=recs,
            needs_new_website=data.get("needs_new_website", False),
            whatsapp_draft=data.get("whatsapp_draft"),
            email_draft=data.get("email_draft"),
            instagram_draft=data.get("instagram_draft"),
        )

    async def generate_stitch_prompt(self, report: FullTriageReport, diagnosis: DiagnosisResult) -> StitchPromptResult:
        prompt = (
            "Você é um especialista em geração de UI para Google Stitch. "
            "Crie um prompt detalhado e estruturado para o Google Stitch criar um site incrível para o lead. "
            "Retorne um JSON com a estrutura:"
            "{\"stitch_prompt\": \"...\", \"suggested_components\": [\"...\"], \"brand_identity\": \"...\"}"
            f"\nLead: {report.lead.name}\nEndereço: {report.lead.formatted_address}\nTelefone: {report.lead.national_phone_number}\n"
            f"Diagnóstico: {diagnosis.overall_summary}"
        )

        try:
            response_text = await self._call_gemini(prompt)
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
        except Exception as e:
            print(f"Erro no parse do JSON da IA (Stitch): {e}")
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
