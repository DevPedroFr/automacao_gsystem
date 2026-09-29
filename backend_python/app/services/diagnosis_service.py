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
            from app.services.niche_profiles import (
                detect_niche_profile,
                build_impeccable_site_prompt,
                build_brand_identity_summary,
            )
            lead = report.lead
            category = getattr(lead, "category", None)
            profile = detect_niche_profile(lead.name, category, lead.formatted_address)
            fallback_prompt = build_impeccable_site_prompt(lead, profile, diagnosis)
            fallback_brand = build_brand_identity_summary(lead, profile, diagnosis)
            stitch_prompt = StitchPromptResult(
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

        return diagnosis, stitch_prompt

