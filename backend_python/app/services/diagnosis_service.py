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

        stitch_prompt = None
        if diagnosis.needs_new_website:
            stitch_prompt = await self.llm.generate_stitch_prompt(report, diagnosis)

        return diagnosis, stitch_prompt
