from pydantic import BaseModel
from typing import List, Optional


class RecommendationItem(BaseModel):
    category: str  # e.g., "Website Speed", "SSL Security", "Instagram", "New Website Required"
    severity: str  # "HIGH", "MEDIUM", "LOW"
    finding: str
    action_item: str


class SalesRecommendation(BaseModel):
    """Estratégia comercial para abordar o lead com base no diagnóstico digital."""
    approach_angle: str        # Ângulo de entrada na conversa
    pain_points: List[str]     # Pontos de dor identificados
    talking_points: List[str]  # Argumentos-chave para a abordagem
    value_proposition: str     # Proposta de valor central


class DiagnosticFact(BaseModel):
    """Um fato observado durante a auditoria, categorizado por pilar."""
    pilar: str   # "google", "website", "social", "general"
    text: str


class DiagnosticInference(BaseModel):
    """Uma análise de impacto gerada pela IA com base nos fatos."""
    pilar: str   # "google", "website", "social", "general"
    text: str


class DiagnosisResult(BaseModel):
    lead_name: str
    overall_summary: str
    recommendations: List[RecommendationItem]
    needs_new_website: bool
    # Campos de cópia de abordagem
    whatsapp_draft: Optional[str] = None
    email_draft: Optional[str] = None
    instagram_draft: Optional[str] = None
    # Campos de pilares e estratégia de venda
    facts: Optional[List[DiagnosticFact]] = None
    inferences: Optional[List[DiagnosticInference]] = None
    sales_recommendation: Optional[SalesRecommendation] = None


class StitchPromptResult(BaseModel):
    lead_name: str
    stitch_prompt: str
    suggested_components: List[str]
    brand_identity: Optional[str] = None

