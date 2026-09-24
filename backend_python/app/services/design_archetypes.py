from typing import Dict, Any, List, Optional
import urllib.parse


class DesignArchetypes:
    """
    Biblioteca de Modelos de Inspiração Arquitetural para Landing Pages.
    Oferece variedade de layouts, hierarquia visual, tipografia e seções
    para que as páginas nunca fiquem parecidas entre si.
    """

    ARCHETYPES = {
        "cro_high_impact": {
            "id": "cro_high_impact",
            "name": "Moderno de Alto Impacto",
            "tag": "Dark CRO & Conversão",
            "icon": "bolt",
            "description": "Design moderno escuro com contrastes vibrantes, badges luminosos e foco agressivo em conversão via WhatsApp.",
            "prompt_spec": """
- ARCHITECTURAL BLUEPRINT: Modern High-Impact Dark CRO.
- Visual Theme: Deep slate/graphite foundation, vibrant accent highlights (amber, orange or cyan), subtle border glow.
- Header: Minimal sticky glassmorphism header with logo and compact WhatsApp CTA.
- Hero Section: High-energy centered hook with pulsating status badge, bold H1, dual action buttons, and Google rating pill.
- Solutions Grid: 4 cards with glowing icon badges, bullet descriptions, and direct quote buttons.
- Social Proof: Floating trust metrics and verified reviews showcase banner.
- Conversion Triggers: Sticky mobile FAB with pulse ring.
"""
        },
        "clean_editorial": {
            "id": "clean_editorial",
            "name": "Editorial Sofisticado",
            "tag": "Elegante & Minimalista",
            "icon": "auto_stories",
            "description": "Estilo editorial clean com tipografia refinada, numeração estilizada de serviços (01, 02, 03) e espaçamento elegante.",
            "prompt_spec": """
- ARCHITECTURAL BLUEPRINT: Sophisticated Minimalist Editorial.
- Visual Theme: Refined editorial palette, high contrast, subtle hairline dividers, generous white space, serif accents for titles.
- Header: Clean top bar with typographic monogram logo and elegant navigation.
- Hero Section: Asymmetric editorial headline, structured subtitle, single dominant primary CTA with phone link.
- Solutions Grid: Numbered list-cards (01, 02, 03, 04) with high-end micro-interactions.
- Trust Section: Quote-style testimonials and founder signature profile.
"""
        },
        "showcase_catalog": {
            "id": "showcase_catalog",
            "name": "Vitrine Comercial & Cotação",
            "tag": "Varejo & Catálogo Visual",
            "icon": "storefront",
            "description": "Perfeito para depósitos, comércio e produtos. Foco em catálogo de categorias, selos de pronta-entrega e cotação expressa.",
            "prompt_spec": """
- ARCHITECTURAL BLUEPRINT: Commercial Showcase & Instant Quote.
- Visual Theme: Dynamic retail layout with product specification tags (Pronta-Entrega, Em Estoque, Garantia).
- Header: Sticky header with delivery area badge and instant call/WhatsApp trigger.
- Hero Section: Split or centered hero with an interactive-style quick quote card highlighting speed and variety.
- Solutions Grid: Product tiles with category badges, bullet lists of available items, and one-click WhatsApp inquiry buttons.
- Differentials: 3 highlight blocks for delivery speed, factory warranty, and transparent pricing.
"""
        },
        "split_dynamic": {
            "id": "split_dynamic",
            "name": "Split Hero Dinâmico",
            "tag": "2 Colunas & Ação Direta",
            "icon": "view_sidebar",
            "description": "Layout em 2 colunas com proposta de valor à esquerda e card de atendimento/cotação expressa em destaque à direita.",
            "prompt_spec": """
- ARCHITECTURAL BLUEPRINT: 2-Column Split Dynamic Hero.
- Visual Theme: Modern tech/commercial split layout with top announcement ticker.
- Top Ticker: Announcement banner: \"⚡ Atendimento rápido e pronta-entrega na sua região\".
- Hero Section (2 Columns): Left column features bold headline, pain relief bullet points, and Google rating. Right column features a dedicated high-converting \"Atendimento Expresso\" card with immediate WhatsApp action.
- Solutions Grid: Modern horizontal or structured cards with material icons.
"""
        },
        "authority_proof": {
            "id": "authority_proof",
            "name": "Máxima Autoridade & Confiança",
            "tag": "Foco em Prova Social",
            "icon": "verified",
            "description": "Enfatiza notas e avaliações do Google acima da dobra, tempo de tradição, garantia e credenciais dos responsáveis.",
            "prompt_spec": """
- ARCHITECTURAL BLUEPRINT: Maximum Authority & Social Proof.
- Visual Theme: Trust-centric layout featuring golden star ratings, verified badges, and leadership spotlight.
- Hero Section: Headline anchored around trust, reliability, and local leadership. Big star rating counter right above the fold.
- Trust Badges: Strip of 4 credibility seals (Empresa Verificada, Atendimento 5 Estrelas, Garantia de Procedência, Suporte Ágil).
- Solutions: Structured capability cards highlighting experience and client satisfaction.
- Leadership Spotlight: Detailed founder/director profile with credentials.
"""
        }
    }

    @classmethod
    def list_archetypes(cls) -> List[Dict[str, Any]]:
        return list(cls.ARCHETYPES.values())

    @classmethod
    def get_archetype(cls, archetype_id: Optional[str]) -> Dict[str, Any]:
        if archetype_id and archetype_id in cls.ARCHETYPES:
            return cls.ARCHETYPES[archetype_id]
        return cls.ARCHETYPES["cro_high_impact"]
