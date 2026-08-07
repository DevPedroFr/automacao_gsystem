from abc import ABC, abstractmethod
from app.models.site import SiteGenerationRequest, GeneratedSiteResult


class SiteGenerator(ABC):
    """Interface for Stage 5: Generating websites via Google Stitch."""

    @abstractmethod
    async def generate_site(self, request: SiteGenerationRequest) -> GeneratedSiteResult:
        """Trigger site generation from prompt and return HTML/UI output."""
        pass
