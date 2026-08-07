from abc import ABC, abstractmethod
from app.models.triage import PageSpeedResult, DomainSecurityResult


class WebsitePerformanceChecker(ABC):
    """Interface for inspecting website performance and SEO metrics (Stage 2)."""

    @abstractmethod
    async def check_performance(self, url: str) -> PageSpeedResult:
        """Check site performance, mobile readiness, and SEO score."""
        pass


class DomainSecurityChecker(ABC):
    """Interface for verifying SSL, socket latency, and WHOIS domain status (Stage 2)."""

    @abstractmethod
    async def verify_domain(self, domain: str) -> DomainSecurityResult:
        """Verify SSL certificate validity, domain expiration, and connectivity."""
        pass
