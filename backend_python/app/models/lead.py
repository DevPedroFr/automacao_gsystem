from pydantic import BaseModel, Field
from typing import Optional, List


class LeadSearchParams(BaseModel):
    keyword: str = Field(..., description="Search keyword e.g. 'Clínica Odontológica'")
    location: str = Field(..., description="Location/City e.g. 'São Paulo, SP'")
    max_results: int = Field(default=20, ge=1, le=60)


class LeadResult(BaseModel):
    place_id: str
    name: str
    formatted_address: Optional[str] = None
    national_phone_number: Optional[str] = None
    international_phone_number: Optional[str] = None
    website_uri: Optional[str] = None
    google_maps_uri: Optional[str] = None
    rating: Optional[float] = None
    user_rating_count: Optional[int] = None
    business_status: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
