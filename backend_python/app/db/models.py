"""
Modelos SQLAlchemy — Espelha a estrutura do banco antigo Node.js (SQLite).
Mantém compatibilidade com os dados já existentes.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text
)
from sqlalchemy.orm import relationship

from app.db.database import Base


def _uuid():
    return str(uuid.uuid4())


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=_uuid)
    niche = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="processing")   # processing | completed | failed | cancelled
    total_leads = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    leads = relationship("Lead", back_populates="campaign", cascade="all, delete-orphan")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)

    # Dados do negócio
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    # Google Business Profile
    google_rating = Column(Float, nullable=True)
    google_reviews_count = Column(Integer, default=0)

    # Web Performance (PageSpeed)
    has_website = Column(Integer, default=0)   # 0 ou 1 (SQLite não tem boolean nativo)
    pagespeed_score = Column(Integer, nullable=True)
    lcp_ms = Column(Integer, nullable=True)
    inp_ms = Column(Integer, nullable=True)
    cls = Column(Float, nullable=True)
    seo_score = Column(Integer, nullable=True)

    # Presença Social
    has_instagram = Column(Integer, default=0)
    instagram_url = Column(String, nullable=True)
    has_facebook = Column(Integer, default=0)
    has_linkedin = Column(Integer, default=0)
    social_last_post_days = Column(Integer, nullable=True)
    instagram_candidates = Column(Text, nullable=True)

    # Scores calculados
    dms = Column(Integer, default=0)    # Digital Maturity Score (0–100)
    cos = Column(Integer, default=0)    # Commercial Opportunity Score (0–100)
    priority = Column(String, default="C")  # A | B | C

    # Enriquecimento e Ativos
    logo_url = Column(String, nullable=True)
    gallery_urls = Column(Text, nullable=True)       # JSON array de fotos do local
    cnpj = Column(String, nullable=True)
    owners_info = Column(Text, nullable=True)        # JSON array com nomes e cargos dos sócios

    # Status interno e rastreamento
    commercial_status = Column(String, default="new")
    source_provider = Column(String, default="google_places")
    raw_data_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="leads")
    diagnostic = relationship("Diagnostic", back_populates="lead", uselist=False, cascade="all, delete-orphan")


class Diagnostic(Base):
    __tablename__ = "diagnostics"

    id = Column(String, primary_key=True, default=_uuid)
    lead_id = Column(String, ForeignKey("leads.id", ondelete="CASCADE"), unique=True, nullable=False)

    observed_facts = Column(Text, nullable=True)
    inferences = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    sales_approach = Column(Text, nullable=True)
    pain_points = Column(Text, nullable=True)
    talking_points = Column(Text, nullable=True)
    value_proposition = Column(Text, nullable=True)
    email_draft = Column(Text, nullable=True)
    whatsapp_draft = Column(Text, nullable=True)
    instagram_draft = Column(Text, nullable=True)
    stitch_prompt = Column(Text, nullable=True)
    brand_colors = Column(Text, nullable=True)         # JSON com paleta detectada
    owners_info = Column(Text, nullable=True)          # JSON com dados dos sócios/fundadores
    logo_url = Column(String, nullable=True)           # URL ou path da logo
    generated_site_html = Column(Text, nullable=True)  # Código HTML da Landing Page gerada
    diagnostic_status = Column(String, default="completed")
    error_message = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="diagnostic")


class ApiCallLog(Base):
    __tablename__ = "api_call_logs"

    id = Column(String, primary_key=True, default=_uuid)
    provider = Column(String, nullable=False)       # google_places | pagespeed | meta | claude
    service_type = Column(String, nullable=False)   # search | pagespeed | instagram | diagnosis
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    success = Column(Integer, default=1)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=True)
