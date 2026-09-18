from pydantic import BaseModel
from typing import List, Optional


class RecommendationItem(BaseModel):
    category: str  # e.g., "Website Speed", "SSL Security", "Instagram", "New Website Required"
    severity: str  # "HIGH", "MEDIUM", "LOW"
    finding: str
    action_item: str


class DiagnosisResult(BaseModel):
    lead_name: str
    overall_summary: str
    recommendations: List[RecommendationItem]
    needs_new_website: bool
    whatsapp_draft: Optional[str] = None
    email_draft: Optional[str] = None
    instagram_draft: Optional[str] = None


class StitchPromptResult(BaseModel):
    lead_name: str
    stitch_prompt: str
    suggested_components: List[str]
    brand_identity: Optional[str] = None
