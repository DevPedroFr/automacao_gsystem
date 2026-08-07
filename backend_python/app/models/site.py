from pydantic import BaseModel
from typing import Optional


class SiteGenerationRequest(BaseModel):
    lead_name: str
    stitch_prompt: str
    target_domain: Optional[str] = None


class GeneratedSiteResult(BaseModel):
    project_id: str
    status: str  # "GENERATED", "FAILED", "IN_PROGRESS"
    preview_url: Optional[str] = None
    html_content: Optional[str] = None
    error: Optional[str] = None
