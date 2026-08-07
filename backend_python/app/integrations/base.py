import httpx
from typing import Optional, Dict, Any
from app.core.exceptions import IntegrationBaseException, ProviderUnavailableException, RateLimitExceededException


class BaseHTTPClient:
    """Base HTTP client wrapper built on httpx for robust API communications."""

    def __init__(self, provider_name: str, base_url: Optional[str] = None, timeout: float = 15.0):
        self.provider_name = provider_name
        self.base_url = base_url
        self.timeout = timeout

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}" if self.base_url else endpoint

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers,
                )

                if response.status_code == 429:
                    raise RateLimitExceededException(self.provider_name)

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as exc:
                raise IntegrationBaseException(
                    message=f"HTTP error {exc.response.status_code}: {exc.response.text}",
                    provider=self.provider_name,
                    status_code=exc.response.status_code,
                )
            except httpx.RequestError as exc:
                raise ProviderUnavailableException(self.provider_name, details=str(exc))
