from pydantic import BaseModel
from typing import List, Optional, Dict, Any


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


class CriticalBlunder(BaseModel):
    """Uma gafe comercial crítica identificada que custa clientes e dinheiro."""
    id: str                     # ex: "search_leak", "contact_friction"
    title: str                  # ex: "Vazamento de Busca Local"
    icon: str                   # Material Symbol icon name
    severity: str               # "CRITICAL", "HIGH", "MEDIUM"
    description: str            # Explicação geral da gafe
    detected_reason: str        # Motivo específico detectado neste lead
    financial_impact: str       # Impacto financeiro estimado
    lp_solution: str            # Como a Landing Page resolve


class TransformationItem(BaseModel):
    """Item da Matriz de Transformação: problema → impacto → solução → ganho."""
    problem: str
    detected_detail: str
    financial_impact: str
    lp_solution: str
    expected_gain: str


class RevenueLeak(BaseModel):
    """Estimativa de vazamento financeiro de oportunidades perdidas."""
    city_size: str
    monthly_searches: Dict[str, int]
    estimated_visitors: Dict[str, int]
    lost_leads_per_month: Dict[str, int]
    estimated_revenue_lost: Dict[str, int]
    avg_ticket_range: Dict[str, int]
    blunders_detected: int
    loss_severity: str
    summary: str


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
    # ========== NOVOS CAMPOS DO DIAGNÓSTICO CONSULTIVO 360° ==========
    critical_blunders: Optional[List[CriticalBlunder]] = None
    transformation_matrix: Optional[List[TransformationItem]] = None
    revenue_leak: Optional[RevenueLeak] = None
    niche_insights: Optional[str] = None  # Insight estratégico específico do nicho


class StitchPromptResult(BaseModel):
    lead_name: str
    stitch_prompt: str
    suggested_components: List[str]
    brand_identity: Optional[str] = None
