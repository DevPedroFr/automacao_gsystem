from typing import Optional
from app.core.config import settings
from app.core.interfaces.social_triage import SocialMediaChecker
from app.models.triage import InstagramProfileResult
from app.integrations.base import BaseHTTPClient


class InstagramIntegration(SocialMediaChecker, BaseHTTPClient):
    """[Etapa 2] Instagram Triage.
    
    Primary Provider: Meta Graph API (Instagram Business Discovery)
    Fallback Provider: RapidAPI / ScrapeCreators (covers personal & non-business accounts)
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        ig_account_id: Optional[str] = None,
        rapidapi_key: Optional[str] = None,
    ):
        super().__init__(provider_name="Instagram Integration", base_url="https://graph.facebook.com/v19.0")
        self.access_token = access_token or settings.META_GRAPH_ACCESS_TOKEN
        self.ig_account_id = ig_account_id or settings.META_INSTAGRAM_ACCOUNT_ID
        self.rapidapi_key = rapidapi_key or settings.RAPIDAPI_KEY
        self.rapidapi_host = settings.RAPIDAPI_HOST or "instagram-data-api.p.rapidapi.com"

    async def get_instagram_profile(self, handle_or_username: str) -> InstagramProfileResult:
        username = handle_or_username.strip("@").strip()
        if not username:
            return InstagramProfileResult(handle="", found=False, error="Handle não fornecido")

        # 1. Try Primary Official Provider: Meta Graph API Business Discovery
        if self.access_token and self.ig_account_id:
            try:
                endpoint = f"/{self.ig_account_id}"
                params = {
                    "fields": f"business_discovery.username({username}){{id,username,biography,followers_count,media_count}}",
                    "access_token": self.access_token,
                }
                data = await self._request("GET", endpoint, params=params)
                discovery = data.get("business_discovery", {})
                if discovery:
                    return InstagramProfileResult(
                        handle=username,
                        found=True,
                        is_business_account=True,
                        followers_count=discovery.get("followers_count"),
                        posts_count=discovery.get("media_count"),
                        biography=discovery.get("biography"),
                        provider_used="Meta Graph API (Official)",
                    )
            except Exception:
                # Primary failed or account is not Business/Creator -> Fallback to RapidAPI
                pass

        # 2. Try Fallback Provider: RapidAPI / ScrapeCreators for Personal/Public Profiles
        if self.rapidapi_key:
            try:
                fallback_client = BaseHTTPClient(
                    provider_name="RapidAPI Instagram Fallback",
                    base_url=f"https://{self.rapidapi_host}",
                )
                headers = {
                    "X-RapidAPI-Key": self.rapidapi_key,
                    "X-RapidAPI-Host": self.rapidapi_host,
                }
                fb_data = await fallback_client._request(
                    "GET",
                    f"/user/info?username={username}",
                    headers=headers,
                )
                user_info = fb_data.get("data", {})
                return InstagramProfileResult(
                    handle=username,
                    found=True,
                    is_business_account=user_info.get("is_business", False),
                    followers_count=user_info.get("follower_count"),
                    posts_count=user_info.get("media_count"),
                    biography=user_info.get("biography"),
                    provider_used="RapidAPI Fallback",
                )
            except Exception as fb_err:
                return InstagramProfileResult(
                    handle=username,
                    found=False,
                    error=f"Falha no provedor oficial e no fallback: {str(fb_err)}",
                )

        # 3. Default Mock Profile if no API credentials configured
        return InstagramProfileResult(
            handle=username,
            found=True,
            is_business_account=True,
            followers_count=1250,
            posts_count=45,
            biography=f"Perfil oficial de {username}. Atendimento presencial e online.",
            provider_used="Mock Integration Mode",
        )
