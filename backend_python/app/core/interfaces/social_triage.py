from abc import ABC, abstractmethod
from app.models.triage import InstagramProfileResult


class SocialMediaChecker(ABC):
    """Interface for verifying social media profiles (Stage 2 - Instagram)."""

    @abstractmethod
    async def get_instagram_profile(self, handle_or_username: str) -> InstagramProfileResult:
        """Fetch Instagram profile presence, followers, bio, and activity."""
        pass
