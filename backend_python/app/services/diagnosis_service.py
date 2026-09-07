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
            stitch_prompt = StitchPromptResult(
                lead_name=report.lead.name,
                stitch_prompt=(
                    f"Create a high-converting, modern landing page for '{report.lead.name}'. "
                    f"Location: {report.lead.formatted_address or 'Brasil'}. "
                    "Include hero section, service overview, testimonials, and a direct WhatsApp contact CTA."
                ),
                suggested_components=["Hero", "ServicesGrid", "Testimonials", "ContactForm", "Footer"],
                brand_identity=f"Profissional e moderno para {report.lead.name}",
            )

        return diagnosis, stitch_prompt
