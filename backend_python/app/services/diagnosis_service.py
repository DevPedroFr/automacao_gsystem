from typing import Optional, Tuple
from app.core.interfaces.llm_service import LLMService
from app.models.triage import FullTriageReport
from app.models.diagnosis import DiagnosisResult, StitchPromptResult
from app.integrations.gemini_ai import GeminiAIIntegration


class DiagnosisService:
    """Service orchestrating AI Diagnosis & Stitch Prompting (Stage 3 & Stage 4)."""

    def __init__(self, llm: Optional[LLMService] = None):
        self.llm = llm or GeminiAIIntegration()

    async def run_diagnosis_and_prompt(
        self, report: FullTriageReport
    ) -> Tuple[DiagnosisResult, Optional[StitchPromptResult]]:
        diagnosis = await self.llm.generate_diagnosis(report)

        stitch_prompt = await self.llm.generate_stitch_prompt(report, diagnosis)
        if not stitch_prompt or not stitch_prompt.stitch_prompt.strip():
            lead = report.lead
            rating_str = f" Include a social proof section showcasing Google rating of {lead.rating}/5.0 based on {lead.user_rating_count or 0} client reviews." if lead.rating else ""
            stitch_prompt = StitchPromptResult(
                lead_name=lead.name,
                stitch_prompt=(
                    f"Create a high-converting, mobile-first professional website for '{lead.name}'. "
                    f"Location: {lead.formatted_address or 'Brasil'}. Phone / WhatsApp: {lead.national_phone_number or 'Disponível via formulário'}. "
                    f"Design style: Modern, ultra-clean, high conversion layout with dark mode elegance and vibrant CTA buttons. "
                    f"Key sections: 1) Hero banner with value proposition, high-impact headline, and primary WhatsApp booking button. "
                    f"2) Highlights & Differentials explaining why customers choose {lead.name}. "
                    f"3) Services / Solutions grid with clear descriptions and icon badges. "
                    f"4) Customer testimonials & reputation.{rating_str} "
                    f"5) Interactive contact section with embedded Google Maps location and direct WhatsApp CTA. "
                    f"6) Professional footer with business hours, address, and legal disclaimers. "
                    f"Requirements: 100% mobile-friendly, PageSpeed 95+ optimized, fast loading, accessible WCAG AA standards."
                ),
                suggested_components=["Hero", "Highlights", "ServicesGrid", "SocialProof", "GoogleReviews", "WhatsAppCTA", "ContactForm", "Footer"],
                brand_identity=f"Moderno, confiável e focado em alta conversão para {lead.name}",
            )

        return diagnosis, stitch_prompt
