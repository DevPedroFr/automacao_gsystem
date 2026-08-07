from typing import Optional
from app.core.interfaces.site_generator import SiteGenerator
from app.models.site import SiteGenerationRequest, GeneratedSiteResult
from app.integrations.stitch import GoogleStitchIntegration


class SiteService:
    """Service orchestrating Site Generation via Google Stitch (Stage 5)."""

    def __init__(self, generator: Optional[SiteGenerator] = None):
        self.generator = generator or GoogleStitchIntegration()

    async def generate_site_for_lead(self, lead_name: str, stitch_prompt: str) -> GeneratedSiteResult:
        request = SiteGenerationRequest(lead_name=lead_name, stitch_prompt=stitch_prompt)
        return await self.generator.generate_site(request)
