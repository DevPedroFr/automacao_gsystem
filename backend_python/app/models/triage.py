from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.models.lead import LeadResult


class PageSpeedResult(BaseModel):
    url: str
    performance_score: Optional[float] = None  # 0 to 100
    seo_score: Optional[float] = None          # 0 to 100
    mobile_friendly: bool = False
    loading_experience: Optional[str] = None
    error: Optional[str] = None


class DomainSecurityResult(BaseModel):
    domain: str
    has_ssl: bool = False
    ssl_valid: bool = False
    ssl_issuer: Optional[str] = None
    days_to_expiration: Optional[int] = None
    is_domain_active: bool = False
    dns_resolved: bool = False
    error: Optional[str] = None


class InstagramProfileResult(BaseModel):
    handle: str
    found: bool = False
    is_business_account: bool = False
    followers_count: Optional[int] = None
    posts_count: Optional[int] = None
    biography: Optional[str] = None
    provider_used: str = "Meta Graph API"  # or Fallback RapidAPI
    error: Optional[str] = None


class FullTriageReport(BaseModel):
    lead: LeadResult
    pagespeed: Optional[PageSpeedResult] = None
    security: Optional[DomainSecurityResult] = None
    instagram: Optional[InstagramProfileResult] = None
    needs_new_website: bool = False
    overall_digital_presence_score: float = 0.0
