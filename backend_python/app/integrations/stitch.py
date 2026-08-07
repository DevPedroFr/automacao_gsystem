import uuid
from typing import Optional
from app.core.config import settings
from app.core.interfaces.site_generator import SiteGenerator
from app.models.site import SiteGenerationRequest, GeneratedSiteResult
from app.integrations.base import BaseHTTPClient


class GoogleStitchIntegration(BaseHTTPClient, SiteGenerator):
    """[Etapa 5] Google Stitch API client for generating sites from structured prompts."""

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.GOOGLE_STITCH_API_KEY
        super().__init__(
            provider_name="Google Stitch API",
            base_url=settings.GOOGLE_STITCH_BASE_URL,
            timeout=30.0,
        )
        self.api_key = key

    async def generate_site(self, request: SiteGenerationRequest) -> GeneratedSiteResult:
        project_id = f"stitch_{uuid.uuid4().hex[:8]}"

        if not self.api_key:
            # Mock generator mode if API key is not yet configured
            mock_html = (
                f"<!DOCTYPE html>\n<html>\n<head><title>{request.lead_name}</title></head>\n"
                f"<body><h1>Site Gerado pelo Stitch para {request.lead_name}</h1>\n"
                f"<p>Prompt processado com sucesso!</p></body>\n</html>"
            )
            return GeneratedSiteResult(
                project_id=project_id,
                status="GENERATED",
                preview_url=f"https://stitch.google.com/labs/preview/{project_id}",
                html_content=mock_html,
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": request.stitch_prompt,
            "options": {
                "framework": "HTML/Vanilla",
                "responsive": True,
                "theme": "modern",
            },
        }

        try:
            data = await self._request("POST", "/projects:generate", json_data=payload, headers=headers)
            return GeneratedSiteResult(
                project_id=data.get("projectId", project_id),
                status=data.get("status", "GENERATED"),
                preview_url=data.get("previewUrl"),
                html_content=data.get("htmlContent"),
            )
        except Exception as err:
            return GeneratedSiteResult(
                project_id=project_id,
                status="FAILED",
                error=f"Erro ao chamar Google Stitch API: {str(err)}",
            )
