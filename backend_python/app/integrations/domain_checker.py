import socket
import ssl
import datetime
from urllib.parse import urlparse
from typing import Optional
from app.core.interfaces.website_triage import DomainSecurityChecker
from app.models.triage import DomainSecurityResult


class DomainSecurityIntegration(DomainSecurityChecker):
    """[Etapa 2] Domain & SSL verification using native Python libraries (socket, ssl, datetime)."""

    def __init__(self):
        pass

    async def verify_domain(self, domain_or_url: str) -> DomainSecurityResult:
        if not domain_or_url:
            return DomainSecurityResult(domain="", error="Domínio não informado")

        # Extract hostname from full URL if passed
        parsed = urlparse(domain_or_url)
        hostname = parsed.netloc or parsed.path
        hostname = hostname.split(":")[0].strip("/")

        result = DomainSecurityResult(domain=hostname)

        # 1. DNS Resolution Check
        try:
            ip_address = socket.gethostbyname(hostname)
            result.dns_resolved = True
            result.is_domain_active = True
        except socket.gaierror:
            result.dns_resolved = False
            result.is_domain_active = False
            result.error = "DNS não resolvido (domínio inativo ou inexistente)"
            return result

        # 2. SSL Certificate Check
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5.0) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    result.has_ssl = True
                    result.ssl_valid = True

                    # Extract Issuer
                    issuer = dict(x[0] for x in cert.get("issuer", []))
                    result.ssl_issuer = issuer.get("organizationName") or issuer.get("commonName")

                    # Calculate Expiration Days
                    not_after_str = cert.get("notAfter")
                    if not_after_str:
                        not_after = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                        days_left = (not_after - datetime.datetime.utcnow()).days
                        result.days_to_expiration = days_left
                        if days_left <= 0:
                            result.ssl_valid = False

        except Exception as ssl_err:
            result.has_ssl = False
            result.ssl_valid = False
            result.error = f"Verificação SSL falhou ou SSL ausente: {str(ssl_err)}"

        return result
