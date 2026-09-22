import json
from typing import Dict, Any, Optional, List


class LPPromptEngine:
    """
    Motor de Geração de Prompts de Elite para Landing Pages.
    Constrói prompts altamente detalhados, contextuais e orientados a conversão (CRO),
    baseados no diagnóstico real, regras de nicho, identidade visual e sócios identificados.
    """

    NICHE_RULES = {
        "advocacia": {
            "name": "Escritório de Advocacia & Consultoria Jurídica",
            "style": "Dark mode luxury or deep executive palette, high contrast, clean editorial typography (serif titles + sans-serif body).",
            "tone": "Sóbrio, altamente confiável, discreto, elegante e em estrita conformidade com as diretrizes e código de ética da OAB.",
            "cta_label": "Agendar Consulta Jurídica Confidencial",
            "key_elements": [
                "Apresentação formal dos Sócios Fundadores com credenciais OAB",
                "Estrutura de atuação consultiva e contenciosa especializada",
                "Garantia de sigilo profissional e atendimento reservado",
                "Sem promessas de resultado ou mercantilização (Conformidade OAB)"
            ],
            "default_colors": {"background": "#3E0B15", "primary": "#d4af37", "secondary": "#551320", "text": "#ffffff"}
        },
        "odontologia": {
            "name": "Clínica Odontológica & Estética do Sorriso",
            "style": "Clean modern aesthetic, luminous foundations with petroleum blue or mint gold accents, high-end healthcare feel.",
            "tone": "Acolhedor, inovador, biosseguro e focado no bem-estar e autoestima do paciente.",
            "cta_label": "Avaliação Inicial pelo WhatsApp",
            "key_elements": [
                "Equipe clínica multidisciplinar e responsáveis técnicos com CRO ativo",
                "Tecnologia odontológica avançada (escaneamento digital, conforto sem dor)",
                "Galeria de procedimentos com foco em saúde e harmonia do sorriso",
                "Agendamento facilitado e localização central acessível"
            ],
            "default_colors": {"background": "#0c1b2a", "primary": "#2dd4bf", "secondary": "#134e4a", "text": "#ffffff"}
        },
        "medicina": {
            "name": "Clínica Médica & Saúde Especializada",
            "style": "Prestigious clinical design, serene deep tones, immaculate white/slate surfaces, warm ambient trust cues.",
            "tone": "Humanizado, técnico, seguro e centrado no paciente (conformidade CFM).",
            "cta_label": "Marcar Consulta Especializada",
            "key_elements": [
                "Corpo clínico qualificado com CRM e RQE explícitos",
                "Estrutura completa com consultórios modernos e exames integrados",
                "Atendimento pontual com hora marcada presencial e telemedicina",
                "Canal direto para dúvidas e preparo pré-consulta"
            ],
            "default_colors": {"background": "#0B1528", "primary": "#38bdf8", "secondary": "#1e293b", "text": "#ffffff"}
        },
        "estetica": {
            "name": "Clínica de Estética & Harmonização Facial",
            "style": "Modern luxury boutique aesthetic, velvety deep tones with champagne / rosé gold accents, high-end editorial.",
            "tone": "Sofisticado, acolhedor, focado em beleza natural, rejuvenescimento e autoestima.",
            "cta_label": "Agendar Diagnóstico Personalizado",
            "key_elements": [
                "Especialistas certificados em procedimentos minimamente invasivos",
                "Ambiente privativo e protocolos de segurança rigorosos",
                "Cardápio visual de tratamentos faciais e corporais",
                "Experiência VIP do paciente com acompanhamento pós-procedimento"
            ],
            "default_colors": {"background": "#1a1215", "primary": "#f59e0b", "secondary": "#2d1b22", "text": "#ffffff"}
        },
        "gastronomia": {
            "name": "Restaurante & Experiência Gastronômica",
            "style": "Warm appetite appeal, rich dark textures (terracotta, deep burgundy, aged brass), high-res culinary focus.",
            "tone": "Envolvente, autêntico, saboroso e convidativo.",
            "cta_label": "Reservar Mesa ou Pedir no WhatsApp",
            "key_elements": [
                "Cardápio interativo com destaques do chef e ingredientes selecionados",
                "Ambiente aconchegante para famílias, encontros e eventos",
                "Atalhos para reservas imediatas e delivery",
                "Avaliações e elogios dos clientes gastronômicos"
            ],
            "default_colors": {"background": "#1c100b", "primary": "#f97316", "secondary": "#381a10", "text": "#ffffff"}
        },
        "geral": {
            "name": "Empresa e Prestação de Serviços Locais",
            "style": "High-converting corporate modern design, bold value proposition, crisp contrast and prominent conversion triggers.",
            "tone": "Profissional, ágil, transparente e orientado a resultados.",
            "cta_label": "Falar com um Especialista Agora",
            "key_elements": [
                "Proposta de valor clara acima da dobra (Hero)",
                "Diferenciais competitivos em relação aos concorrentes da região",
                "Prova social e reputação no Google com avaliações verificadas",
                "Formulário direto e botão de WhatsApp para contato instantâneo"
            ],
            "default_colors": {"background": "#0F131C", "primary": "#3b82f6", "secondary": "#1E293B", "text": "#ffffff"}
        }
    }

    @classmethod
    def detect_niche(cls, name: str, category: Optional[str] = None) -> str:
        text = f"{name} {category or ''}".lower()
        if any(w in text for w in ["advog", "jurid", "direito", "oab", "associados"]):
            return "advocacia"
        if any(w in text for w in ["odonto", "dent", "sorriso", "implant", "orto"]):
            return "odontologia"
        if any(w in text for w in ["medic", "clinic", "dr.", "doutor", "saude", "oftalm", "dermato"]):
            return "medicina"
        if any(w in text for w in ["estet", "beleza", "salao", "hair", "spa", "laser", "harmoniz"]):
            return "estetica"
        if any(w in text for w in ["restaurante", "pizz", "burger", "bistr", "cafe", "culin", "gastron"]):
            return "gastronomia"
        return "geral"

    @classmethod
    def build_custom_prompt(
        cls,
        lead_data: Dict[str, Any],
        diagnostic_data: Dict[str, Any],
        brand_colors: Optional[Dict[str, Any]] = None,
        owners_info: Optional[List[Dict[str, str]]] = None,
        logo_url: Optional[str] = None,
        gallery_urls: Optional[List[str]] = None,
    ) -> str:
        """
        Gera o prompt em inglês ultra-específico e contextual para a IA / Google Stitch,
        aplicando todas as regras de negócio, dados reais de dor e identidade visual.
        """
        lead_name = lead_data.get("name", "Empresa")
        niche_key = cls.detect_niche(lead_name, lead_data.get("category"))
        rules = cls.NICHE_RULES.get(niche_key, cls.NICHE_RULES["geral"])

        # Cores detectadas ou padrão
        colors = brand_colors or rules["default_colors"]
        bg_color = colors.get("background", "#0F131C")
        primary_color = colors.get("primary", "#d4af37")
        secondary_color = colors.get("secondary", "#1E293B")
        text_color = colors.get("text", "#ffffff")

        # Dados de Reputação
        rating = lead_data.get("google_rating")
        reviews_count = lead_data.get("google_reviews_count", 0)
        reputation_clause = (
            f"Social proof highlighting real Google Rating of {rating}/5.0 stars with {reviews_count}+ verified reviews"
            if rating else "High-authority social proof with verified customer testimonials"
        )

        # Sócios / Liderança
        owners_clause = ""
        if owners_info and len(owners_info) > 0:
            owners_list_str = ", ".join([f"{o.get('name')} ({o.get('role', 'Sócio')})" for o in owners_info])
            count_str = f"the {len(owners_info)} Founding Partners" if len(owners_info) > 1 else "the Founding Partner"
            owners_clause = (
                f"- Leadership & Team Section: Dedicated showcase of {count_str}: {owners_list_str}. "
                f"Display professional portraits, credentials, and leadership dedication.\n"
            )
        else:
            owners_clause = "- Leadership Section: Professional executive profile of the founding leadership team.\n"

        # Dores e Argumentos do Diagnóstico
        pain_points = diagnostic_data.get("pain_points") or "Losing clients to digital-first competitors in the local area"
        value_prop = diagnostic_data.get("value_proposition") or f"Deliver unmatched professional excellence for {lead_name}"
        approach = diagnostic_data.get("sales_approach") or "High-touch personalized consultation"
        whatsapp = lead_data.get("phone") or "(11) 99999-9999"
        address = lead_data.get("address") or lead_data.get("city") or "Brasil"

        # Fotos e Logo
        logo_spec = f"Logo: Use official logo at '{logo_url}'." if logo_url else "Logo: Clean elegant branded typographic mark."
        gallery_spec = f"Use realistic local facility photos: {gallery_urls}." if gallery_urls else "Use high-end architectural photography matching the segment."

        prompt = f"""Create an exceptional, high-converting, mobile-first website for '{lead_name}', operating in the {rules['name']} segment.

### CRITICAL BRAND IDENTITY & VISUAL SYSTEM (MUST STRICTLY FOLLOW):
- Foundation / Background: {bg_color}
- Primary Accent & Action Elements: {primary_color}
- Secondary / Container Surfaces: {secondary_color}
- High-Contrast Text: {text_color}
- Aesthetics: {rules['style']}
- Tone of Voice: {rules['tone']}
- {logo_spec}
- {gallery_spec}

### BUSINESS INTELLIGENCE & DIAGNOSTIC CONTEXT:
- Core Value Proposition: {value_prop}
- Customer Pain Points Addressed: {pain_points}
- Strategic Positioning: {approach}
- Authority & Reputation: {reputation_clause}
- Contact / WhatsApp: {whatsapp}
- Location: {address}

### ARCHITECTURAL SECTIONS & CRO FLOW:
1. Top Sticky Navigation: Single unified navbar with brand logo, key section links (Services, Leadership, Reviews, Location), direct phone button, and prominent '{rules['cta_label']}' CTA.
2. High-Impact Hero Section: 
   - Powerful value proposition headline addressing customer needs (ensure no awkward word wrapping on desktop).
   - High-contrast direct WhatsApp booking button.
   - Authority badges (OAB/Compliance accreditation, Google 5-star ratings, 100% confidentiality).
   - Premium imagery showcasing the professional firm or facility.
3. Trust & Core Differentials Grid:
   - 4-card matrix highlighting regulatory compliance, customized service, high-speed execution, and security.
{owners_clause}4. Interactive Services / Practice Areas:
   - Grid of cards with custom icons, clear scope of work, and instant WhatsApp inquiry link per service.
5. Social Proof & Verified Reviews:
   - Google Reviews 5.0 badge, client testimonials, and measurable metrics of success.
6. Location & Access:
   - Complete physical address: {address}.
   - Business hours and embedded interactive map representation.
7. Mobile-First Floating WhatsApp Action Button:
   - Sticky bottom-right pulsating green button linked to wa.me/{''.join(filter(str.isdigit, whatsapp))} with pre-filled greeting.
8. Professional Footer:
   - Business credentials, copyright, regulatory notices, and privacy link.

### TECHNICAL SPECIFICATIONS:
- Framework: Modern Tailwind CSS (fully responsive, mobile-first).
- Compliance: WCAG AA accessibility, zero broken external scripts, clean semantics.
"""
        return prompt.strip()
