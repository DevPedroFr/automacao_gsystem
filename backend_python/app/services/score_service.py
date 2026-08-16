"""
Score Service — Porta fiel da lógica de scoring do backend Node.js (scoreService.js).
Calcula DMS (Digital Maturity Score) e COS (Commercial Opportunity Score).
"""


def calculate_dms(lead: dict) -> int:
    """
    Calcula o Digital Maturity Score (0-100).
    Composto por:
      - Google Business Profile (40pts)
      - Performance Web / PageSpeed (35pts)
      - Presença Social (25pts)
    """
    total = 0.0

    # === Google Business Profile (40 pontos max) ===
    rating_score = ((lead.get("google_rating") or 0) / 5) * 20
    reviews_score = (min(lead.get("google_reviews_count") or 0, 100) / 100) * 20
    total += rating_score + reviews_score

    # === Performance Web (35 pontos max) ===
    if lead.get("has_website") and lead.get("pagespeed_score") is not None:
        total += (lead["pagespeed_score"] / 100) * 35

    # === Presença Social (25 pontos max) ===
    if lead.get("has_instagram"):
        total += 10
    if lead.get("has_facebook"):
        total += 10
    last_post = lead.get("social_last_post_days")
    if last_post is not None and last_post < 30:
        total += 5

    return round(total)


def calculate_cos(lead: dict, dms: int) -> int:
    """
    Calcula o Commercial Opportunity Score (0-100).
    Quanto menor a maturidade digital, maior a oportunidade comercial.
    """
    business_validation = 20
    rating = lead.get("google_rating") or 0
    reviews = lead.get("google_reviews_count") or 0

    if rating >= 3.5 and reviews >= 50:
        business_validation = 100
    elif rating >= 3.5 and reviews >= 10:
        business_validation = 75
    elif rating >= 3.0 and reviews >= 5:
        business_validation = 50

    digital_gap = 100 - dms
    cos = (business_validation * 0.4) + (digital_gap * 0.6)
    return round(cos)


def get_priority(cos: int) -> str:
    """Determina a prioridade (A/B/C) com base no COS."""
    if cos > 80:
        return "A"
    if cos >= 50:
        return "B"
    return "C"
