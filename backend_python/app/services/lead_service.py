from typing import List, Optional
from app.core.interfaces.lead_search import LeadSearchProvider
from app.models.lead import LeadSearchParams, LeadResult
from app.integrations.google_places import GooglePlacesIntegration


class LeadService:
    """Service orchestrating Lead Search (Stage 1).
    
    Depends on abstract LeadSearchProvider (Dependency Inversion Principle).
    """

    def __init__(self, provider: Optional[LeadSearchProvider] = None):
        self.provider = provider or GooglePlacesIntegration()

    async def find_leads(self, keyword: str, location: str, max_results: int = 20) -> List[LeadResult]:
        params = LeadSearchParams(keyword=keyword, location=location, max_results=max_results)
        return await self.provider.search_leads(params)
