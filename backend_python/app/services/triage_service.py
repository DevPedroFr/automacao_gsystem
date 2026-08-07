import asyncio
from typing import Optional
from app.core.interfaces.website_triage import WebsitePerformanceChecker, DomainSecurityChecker
from app.core.interfaces.social_triage import SocialMediaChecker
from app.models.lead import LeadResult
from app.models.triage import FullTriageReport
from app.integrations.pagespeed import PageSpeedIntegration
from app.integrations.domain_checker import DomainSecurityIntegration
from app.integrations.instagram import InstagramIntegration


class TriageService:
    """Service orchestrating Digital Triage (Stage 2: PageSpeed, SSL/Domain, Instagram)."""

    def __init__(
        self,
        pagespeed_checker: Optional[WebsitePerformanceChecker] = None,
        domain_checker: Optional[DomainSecurityChecker] = None,
        social_checker: Optional[SocialMediaChecker] = None,
    ):
        self.pagespeed_checker = pagespeed_checker or PageSpeedIntegration()
        self.domain_checker = domain_checker or DomainSecurityIntegration()
        self.social_checker = social_checker or InstagramIntegration()

    async def execute_triage(self, lead: LeadResult) -> FullTriageReport:
        website = lead.website_uri

        pagespeed_task = self.pagespeed_checker.check_performance(website) if website else None
        security_task = self.domain_checker.verify_domain(website) if website else None
        instagram_task = self.social_checker.get_instagram_profile(lead.name)

        # Run triage checks concurrently
        pagespeed_res = await pagespeed_task if pagespeed_task else None
        security_res = await security_task if security_task else None
        instagram_res = await instagram_task if instagram_task else None

        needs_new_site = (
            website is None
            or (pagespeed_res and pagespeed_res.performance_score and pagespeed_res.performance_score < 50)
            or (security_res and not security_res.ssl_valid)
        )

        return FullTriageReport(
            lead=lead,
            pagespeed=pagespeed_res,
            security=security_res,
            instagram=instagram_res,
            needs_new_website=needs_new_site,
        )
