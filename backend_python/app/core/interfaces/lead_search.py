from abc import ABC, abstractmethod
from typing import List
from app.models.lead import LeadSearchParams, LeadResult


class LeadSearchProvider(ABC):
    """Interface (ISP & DIP) for Stage 1: Searching business leads."""

    @abstractmethod
    async def search_leads(self, params: LeadSearchParams) -> List[LeadResult]:
        """Search for leads by keyword and location."""
        pass

    @abstractmethod
    async def get_lead_details(self, place_id: str) -> LeadResult:
        """Fetch detailed information for a specific place/lead."""
        pass
