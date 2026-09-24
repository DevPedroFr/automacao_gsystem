from app.services.design_archetypes import DesignArchetypes
import json
from typing import Dict, Any, Optional, List


class LPPromptEngine:
    """
    Motor de Geração de Prompts de Elite para Landing Pages.
    Constrói prompts altamente detalhados, contextuais e orientados a conversão (CRO),
    baseados no diagnóstico real, regras de nicho, identidade visual e sócios identificados.
    """

    NICHE_RULES = {
        "construcao": {
            "name": "Depósito de Materiais de Construção, Reforma & Acabamento",
            "style": "High-impact retail & commercial design, solid high-contrast palette (industrial slate/navy with construction safety orange or vibrant amber), sharp typography, highly readable pricing/offer badges.",
            "tone": "Ágil, confiável, focado em pronta-entrega, variedade, economia na obra e atendimento rápido via WhatsApp.",
            "hero_badge": "Materiais para Construção, Reforma & Acabamento",
            "headline": "Tudo para a sua Obra do Básico ao Acabamento com Pronta-Entrega e Preço Justo",
            "subheadline": "Cimento, ferragens, hidráulica, elétrica, tintas e ferramentas com entrega rápida direto no seu canteiro de obras.",
            "cta_label": "Pedir Orçamento Rápido no WhatsApp",
            "whatsapp_msg": "Olá! Gostaria de fazer uma cotação de materiais para minha obra.",
            "key_elements": [
                "Cotação rápida e direta via WhatsApp para profissionais e particulares",
                "Entrega expressa e confiável na região",
                "Linha completa de marcas líderes e materiais de primeira linha",
                "Condições especiais para construtores, pedreiros e reformas"
            ],
            "solution_cards": [
                {"title": "Básico & Estrutural", "desc": "Cimento, areia, brita, blocos, tijolos, vergalhões e ferragens armadas para alvenaria.", "icon": "foundation"},
                {"title": "Hidráulica & Elétrica", "desc": "Tubos, conexões, fios, cabos, disjuntores, caixas d'água e conduítes certificados.", "icon": "plumbing"},
                {"title": "Acabamento & Tintas", "desc": "Argamassas, rejuntes, tintas imobiliárias, impermeabilizantes, vernizes e pincéis.", "icon": "format_paint"},
                {"title": "Ferramentas & Acessórios", "desc": "Ferramentas manuais e elétricas, discos de corte, pás, carrinhos e fixadores.", "icon": "construction"}
            ],
            "default_colors": {"background": "#0F172A", "primary": "#F97316", "secondary": "#1E293B", "text": "#FFFFFF"}
        },
        "automotivo": {
            "name": "Centro Automotivo, Oficina Mecânica & Auto Peças",
            "style": "Modern high-tech automotive aesthetic, deep carbon/graphite background with racing red or electric cyan accents.",
            "tone": "Transparente, técnico, confiável, ágil e focado na segurança do condutor e da família.",
            "hero_badge": "Centro Automotivo & Manutenção Preventiva",
            "headline": "Diagnóstico Preciso, Peças Genuínas e Segurança para o Seu Veículo",
            "subheadline": "Revisão geral, suspensão, freios, injeção eletrônica, pneus e mecânica completa com garantia comprovada.",
            "cta_label": "Agendar Revisão ou Diagnóstico",
            "whatsapp_msg": "Olá! Gostaria de agendar uma revisão para o meu veículo.",
            "key_elements": [
                "Diagnóstico computadorizado com scanners de última geração",
                "Orçamento transparente antes da execução do serviço",
                "Garantia total de peças e mão de obra qualificada",
                "Atendimento ágil com sala de espera confortável"
            ],
            "solution_cards": [
                {"title": "Revisão Preventiva & Óleo", "desc": "Troca de óleo, filtros, velas e checagem de mais de 40 itens de segurança.", "icon": "oil_barrel"},
                {"title": "Freios & Suspensão", "desc": "Pastilhas, discos, amortecedores, molas e alinhamento computadorizado.", "icon": "car_repair"},
                {"title": "Injeção & Motor", "desc": "Diagnóstico via scanner, limpeza de bicos, correias e retífica especializada.", "icon": "precision_manufacturing"},
                {"title": "Ar Condicionado & Elétrica", "desc": "Higienização de ar condicionado, baterias, alternadores e iluminação.", "icon": "ac_unit"}
            ],
            "default_colors": {"background": "#090D16", "primary": "#EF4444", "secondary": "#1E293B", "text": "#FFFFFF"}
        },
        "odontologia": {
            "name": "Clínica Odontológica & Estética do Sorriso",
            "style": "Clean modern aesthetic, luminous foundations with petroleum blue or mint gold accents, high-end healthcare feel.",
            "tone": "Acolhedor, inovador, biosseguro e focado no bem-estar e autoestima do paciente.",
            "hero_badge": "Clínica Odontológica Especializada",
            "headline": "Transforme Seu Sorriso com Tecnologia, Conforto e Segurança",
            "subheadline": "Implantes dentários, alinhadores invisíveis, clareamento e reabilitação oral com dentistas especializados.",
            "cta_label": "Agendar Avaliação no WhatsApp",
            "whatsapp_msg": "Olá! Gostaria de agendar uma avaliação odontológica.",
            "key_elements": [
                "Equipe clínica multidisciplinar com CRO ativo",
                "Tecnologia odontológica avançada (escaneamento digital, conforto sem dor)",
                "Ambiente humanizado e protocolos estritos de biossegurança",
                "Condições facilitadas de pagamento para o seu tratamento"
            ],
            "solution_cards": [
                {"title": "Implantes & Próteses", "desc": "Reabilitação oral completa com dentes fixos de altíssima durabilidade e aspecto natural.", "icon": "dentistry"},
                {"title": "Ortodontia & Alinhadores", "desc": "Alinhadores transparentes e aparelhos modernos para correção rápida e discreta.", "icon": "sentiment_very_satisfied"},
                {"title": "Estética do Sorriso", "desc": "Clareamento a laser, facetas de resina e lentes de contato dental.", "icon": "sparkles"},
                {"title": "Clínica Geral & Prevenção", "desc": "Limpeza profunda, profilaxia, tratamento de canal e restaurações estéticas.", "icon": "health_and_safety"}
            ],
            "default_colors": {"background": "#0C1B2A", "primary": "#2DD4BF", "secondary": "#134E4A", "text": "#FFFFFF"}
        },
        "medicina": {
            "name": "Clínica Médica & Saúde Especializada",
            "style": "Prestigious clinical design, serene deep tones, immaculate white/slate surfaces, warm ambient trust cues.",
            "tone": "Humanizado, técnico, seguro e centrado no paciente (conformidade CFM).",
            "hero_badge": "Medicina Integrada & Consultas Especializadas",
            "headline": "Cuidado Humanizado, Diagnóstico Preciso e Atenção Total à Sua Saúde",
            "subheadline": "Corpo clínico qualificado, exames integrados e atendimento pontual para você e toda a sua família.",
            "cta_label": "Marcar Consulta Especializada",
            "whatsapp_msg": "Olá! Gostaria de agendar uma consulta médica.",
            "key_elements": [
                "Médicos especialistas com CRM e RQE certificados",
                "Estrutura completa com consultórios modernos e exames integrados",
                "Atendimento pontual com hora marcada presencial e telemedicina",
                "Ambiente seguro e acolhedor"
            ],
            "solution_cards": [
                {"title": "Consultas Especializadas", "desc": "Cardiologia, dermatologia, ginecologia, ortopedia e clínica geral.", "icon": "stethoscope"},
                {"title": "Exames Diagnósticos", "desc": "Ultrassonografia, eletrocardiograma, exames laboratoriais e check-ups completos.", "icon": "monitor_heart"},
                {"title": "Check-up Preventivo", "desc": "Avaliações completas de saúde personalizadas para cada fase da vida.", "icon": "fact_check"},
                {"title": "Telemedicina & Retornos", "desc": "Acompanhamento contínuo e consultas online com envio de receitas digitais.", "icon": "devices"}
            ],
            "default_colors": {"background": "#0B1528", "primary": "#38BDF8", "secondary": "#1E293B", "text": "#FFFFFF"}
        },
        "estetica": {
            "name": "Clínica de Estética & Harmonização Facial",
            "style": "Modern luxury boutique aesthetic, velvety deep tones with champagne / rosé gold accents, high-end editorial.",
            "tone": "Sofisticado, acolhedor, focado em beleza natural, rejuvenescimento e autoestima.",
            "hero_badge": "Estética Avançada & Bem-Estar",
            "headline": "Realce Sua Melhor Versão com Protocolos Exclusivos e Tecnologia de Ponta",
            "subheadline": "Harmonização facial, bioestimuladores de colágeno, depilação a laser e tratamentos corporais com segurança.",
            "cta_label": "Agendar Avaliação Personalizada",
            "whatsapp_msg": "Olá! Gostaria de agendar uma avaliação estética personalizada.",
            "key_elements": [
                "Profissionais habilitados em procedimentos minimamente invasivos",
                "Ambiente privativo e protocolos estritos de biossegurança",
                "Produtos homologados pela ANVISA de alto padrão internacional",
                "Plano de tratamento sob medida para os seus objetivos"
            ],
            "solution_cards": [
                {"title": "Harmonização Facial", "desc": "Toxina botulínica (botox), preenchimento com ácido hialurônico e contorno labial.", "icon": "face"},
                {"title": "Bioestimuladores de Colágeno", "desc": "Rejuvenescimento natural, firmeza da pele e melhora do tônus facial e corporal.", "icon": "auto_awesome"},
                {"title": "Depilação a Laser", "desc": "Laser de alta tecnologia, indolor e com resultados visíveis desde a 1ª sessão.", "icon": "flare"},
                {"title": "Estética Corporal", "desc": "Drenagem linfática, massagem modeladora, criomodelagem e tratamento de celulite.", "icon": "spa"}
            ],
            "default_colors": {"background": "#1A1215", "primary": "#F59E0B", "secondary": "#2D1B22", "text": "#FFFFFF"}
        },
        "gastronomia": {
            "name": "Restaurante, Gastronomia & Experiência Culinária",
            "style": "Warm appetite appeal, rich dark textures (terracotta, deep burgundy, aged brass), high-res culinary focus.",
            "tone": "Envolvente, autêntico, saboroso e convidativo.",
            "hero_badge": "Experiência Gastronômica & Pratos Especiais",
            "headline": "Sabores Autênticos, Ingredientes Selecionados e Momentos Inesquecíveis",
            "subheadline": "Pratos artesanais, ambiente aconchegante para a família e opções para reserva imediata ou delivery.",
            "cta_label": "Reservar Mesa ou Fazer Pedido",
            "whatsapp_msg": "Olá! Gostaria de fazer uma reserva / pedido.",
            "key_elements": [
                "Ingredientes frescos de produtores selecionados e receitas exclusivas",
                "Ambiente climatizado e perfeito para encontros e celebrações",
                "Atendimento acolhedor e ágil",
                "Delivery rápido com embalagens térmicas seguras"
            ],
            "solution_cards": [
                {"title": "Pratos Principais & Assados", "desc": "Carnes nobres, massas artesanais, opções vegetarianas e receitas autorais.", "icon": "restaurant"},
                {"title": "Petiscos & Entradas", "desc": "Porções generosas perfeitas para compartilhar com a família e amigos.", "icon": "tapas"},
                {"title": "Carta de Bebidas & Drinks", "desc": "Vinhos selecionados, cervejas artesanais e coquetéis autorais exclusivos.", "icon": "local_bar"},
                {"title": "Sobremesas Artesanais", "desc": "Doces frescos feitos diariamente para fechar sua refeição com perfeição.", "icon": "icecream"}
            ],
            "default_colors": {"background": "#1C100B", "primary": "#F97316", "secondary": "#381A10", "text": "#FFFFFF"}
        },
        "advocacia": {
            "name": "Escritório de Advocacia & Consultoria Jurídica",
            "style": "Dark mode luxury or deep executive palette, high contrast, clean editorial typography (serif titles + sans-serif body).",
            "tone": "Sóbrio, altamente confiável, discreto, elegante e em estrita conformidade com as diretrizes e código de ética da OAB.",
            "hero_badge": "Assessoria Jurídica & Consultoria Estratégica",
            "headline": "Advocacia Estratégica, Segurança e Defesa Rigorosa dos Seus Direitos",
            "subheadline": "Compromisso inegociável com a excelência técnica, agilidade e sigilo para defender seus interesses patrimoniais e corporativos.",
            "cta_label": "Agendar Consulta Jurídica Confidencial",
            "whatsapp_msg": "Olá, gostaria de agendar uma consulta jurídica especializada.",
            "key_elements": [
                "Apresentação formal dos Sócios Fundadores com credenciais OAB",
                "Estrutura de atuação consultiva e contenciosa especializada",
                "Garantia de sigilo profissional e atendimento reservado",
                "Sem promessas de resultado ou mercantilização (Conformidade OAB)"
            ],
            "solution_cards": [
                {"title": "Direito Empresarial & Contratos", "desc": "Blindagem patrimonial, estruturação societária e assessoria preventiva para negócios.", "icon": "gavel"},
                {"title": "Direito Cível & Imobiliário", "desc": "Regularização de imóveis, litígios possessórios, inventários e cobranças judiciais.", "icon": "apartment"},
                {"title": "Direito Trabalhista Patronal", "desc": "Defesa corporativa em reclamatórias trabalhistas e conformidade com a CLT.", "icon": "badge"},
                {"title": "Consultoria Tributária & Fiscal", "desc": "Recuperação de créditos tributários e planejamento fiscal estratégico.", "icon": "payments"}
            ],
            "default_colors": {"background": "#3E0B15", "primary": "#D4AF37", "secondary": "#551320", "text": "#FFFFFF"}
        },
        "imobiliaria": {
            "name": "Imobiliária, Corretores & Gestão de Imóveis",
            "style": "Sophisticated architectural design, modern clean lines, rich real estate imagery cues with midnight navy and gold accents.",
            "tone": "Seguro, consultivo, transparente e focado em realizar excelentes negócios imobiliários.",
            "hero_badge": "Imóveis Selecionados & Assessoria Imobiliária",
            "headline": "Encontre o Imóvel Perfeito para Morar ou Investir com Total Segurança Jurídica",
            "subheadline": "Casas, apartamentos, terrenos e galpões comerciais nas melhores localizações da região com suporte de corretores credenciados.",
            "cta_label": "Falar com um Corretor no WhatsApp",
            "whatsapp_msg": "Olá! Gostaria de informações sobre imóveis disponíveis para compra/aluguel.",
            "key_elements": [
                "Corretores credenciados pelo CRECI",
                "Assessoria jurídica e financeira completa no financiamento",
                "Portfólio atualizado com as melhores opções da cidade",
                "Atendimento personalizado de acordo com o seu perfil de investimento"
            ],
            "solution_cards": [
                {"title": "Venda de Imóveis Residenciais", "desc": "Casas em condomínio, apartamentos prontos e lançamentos na planta.", "icon": "home"},
                {"title": "Locação com Garantia Ágil", "desc": "Aluguel sem fiador, análise de crédito digital rápida e suporte ao inquilino.", "icon": "key"},
                {"title": "Imóveis Comerciais & Galpões", "desc": "Salas, pontos comerciais e áreas industriais para impulsionar seu negócio.", "icon": "domain"},
                {"title": "Avaliação de Imóveis", "desc": "Laudo técnico preciso com valor real de mercado para compra, venda ou partilha.", "icon": "calculate"}
            ],
            "default_colors": {"background": "#0B132B", "primary": "#3B82F6", "secondary": "#1C2541", "text": "#FFFFFF"}
        },
        "geral": {
            "name": "Empresa & Prestação de Serviços de Excelência",
            "style": "High-converting corporate modern design, bold value proposition, crisp contrast and prominent conversion triggers.",
            "tone": "Profissional, ágil, transparente e orientado a resultados.",
            "hero_badge": "Excelência em Atendimento & Qualidade Comprovada",
            "headline": "Soluções Completas com Qualidade, Agilidade e Confiança para Você",
            "subheadline": "Atendimento personalizado, garantia de procedência e os melhores profissionais à disposição do seu projeto.",
            "cta_label": "Falar com um Especialista no WhatsApp",
            "whatsapp_msg": "Olá! Gostaria de mais informações sobre os produtos e serviços de vocês.",
            "key_elements": [
                "Proposta de valor clara acima da dobra",
                "Diferenciais competitivos em relação aos concorrentes da região",
                "Prova social e reputação no Google com avaliações verificadas",
                "Atendimento instantâneo via WhatsApp"
            ],
            "solution_cards": [
                {"title": "Atendimento Sob Medida", "desc": "Orientação técnica dedicada para entender sua necessidade e entregar a melhor solução.", "icon": "handshake"},
                {"title": "Qualidade & Procedência", "desc": "Produtos e serviços que cumprem os mais rigorosos padrões de satisfação.", "icon": "verified"},
                {"title": "Pronta-Entrega & Agilidade", "desc": "Processos otimizados para garantir rapidez no fornecimento e execução.", "icon": "local_shipping"},
                {"title": "Condições Especiais", "desc": "Pagamento facilitado e negociação transparente para fechar o melhor negócio.", "icon": "credit_card"}
            ],
            "default_colors": {"background": "#0F131C", "primary": "#3B82F6", "secondary": "#1E293B", "text": "#FFFFFF"}
        }
    }

    @classmethod
    def detect_niche(cls, name: str, category: Optional[str] = None) -> str:
        text = f"{name} {category or ''}".lower()
        
        # 1. Construção, depósitos, reformas, ferragens, tintas
        if any(w in text for w in ["constru", "material", "materiais", "deposito", "depósito", "tinta", "cimento", "madeira", "ferrag", "hidraul", "hidrául", "eletric", "elétric", "obra", "reforma", "piso", "acabamento", "tijolo", "telha", "gesso", "vidrac", "vidraç"]):
            return "construcao"
            
        # 2. Automotivo, mecânica, auto peças, pneus
        if any(w in text for w in ["auto", "mecanic", "mecânic", "oficina", "pneu", "autope", "funilaria", "pintura automotiva", "revis", "oleo", "óleo", "escapamento", "troca de oleo", "centro automotivo", "moto"]):
            return "automotivo"

        # 3. Advocacia e jurídico
        if any(w in text for w in ["advog", "jurid", "juríd", "direito", "oab", "associados", "tributar", "trabalhista", "previdenc", "civel", "cível"]) and not any(w in text for w in ["material", "deposito", "constru"]):
            return "advocacia"

        # 4. Odontologia
        if any(w in text for w in ["odonto", "dentist", "sorriso", "implant", "orto", "clareamento", "protese", "prótese"]):
            return "odontologia"

        # 5. Medicina e saúde
        if any(w in text for w in ["medic", "clinic", "clínica", "dr.", "doutor", "saude", "saúde", "oftalm", "dermato", "pediatr", "cardiolog", "ortoped", "fisioter", "psicolog"]):
            return "medicina"

        # 6. Estética, beleza, salões
        if any(w in text for w in ["estet", "estét", "beleza", "salao", "salão", "hair", "spa", "laser", "harmoniz", "barbearia", "depila", "sobrancelha", "unha", "esmalt"]):
            return "estetica"

        # 7. Gastronomia, restaurantes, bares
        if any(w in text for w in ["restaurante", "pizz", "burger", "lanche", "bistr", "cafe", "café", "culin", "gastron", "churrasc", "sushi", "padaria", "confeitaria", "bar ", "choperia"]):
            return "gastronomia"

        # 8. Imobiliária
        if any(w in text for w in ["imobil", "imóveis", "imoveis", "corretor", "creci", "locacao", "locação", "loteamento"]):
            return "imobiliaria"

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
        archetype_id: Optional[str] = None,
    ) -> str:
        """
        Gera o prompt em inglês ultra-específico e contextual para a IA / Google Stitch,
        aplicando todas as regras de negócio, dados reais de dor e identidade visual.
        """
        lead_name = lead_data.get("name", "Empresa")
        niche_key = cls.detect_niche(lead_name, lead_data.get("category"))
        rules = cls.NICHE_RULES.get(niche_key, cls.NICHE_RULES["geral"])
        archetype = DesignArchetypes.get_archetype(archetype_id)

        # Cores detectadas ou padrão
        colors = brand_colors or rules["default_colors"]
        bg_color = colors.get("background", "#0F131C")
        primary_color = colors.get("primary", "#F97316")
        secondary_color = colors.get("secondary", "#1E293B")
        text_color = colors.get("text", "#FFFFFF")

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
            owners_list_str = ", ".join([f"{o.get('name')} ({o.get('role', 'Responsável')})" for o in owners_info])
            count_str = f"the {len(owners_info)} Founders & Leaders" if len(owners_info) > 1 else "the Founder & Business Leader"
            owners_clause = (
                f"- Leadership & Team Section: Dedicated showcase of {count_str}: {owners_list_str}. "
                f"Display professional portraits, credentials, and leadership dedication.\n"
            )
        else:
            owners_clause = "- Leadership Section: Professional executive profile of the founding management team.\n"

        # Dores e Argumentos do Diagnóstico
        pain_points = diagnostic_data.get("pain_points") or f"Losing clients to digital-first competitors in the {lead_data.get('city', 'local')} area"
        value_prop = diagnostic_data.get("value_proposition") or f"Deliver unmatched excellence and speed in {rules['name']}"
        approach = diagnostic_data.get("sales_approach") or "Direct instant WhatsApp quote and consultation"
        whatsapp = lead_data.get("phone") or "(11) 99999-9999"
        address = lead_data.get("address") or lead_data.get("city") or "Brasil"

        # Fotos e Logo
        logo_spec = f"Logo: Use official logo at '{logo_url}'." if logo_url else "Logo: Clean modern typographic brand badge."
        gallery_spec = f"Use realistic local photos: {gallery_urls}." if gallery_urls else f"Use high-quality commercial photography strictly matching {rules['name']}."

        prompt = f"""Create an exceptional, high-converting, mobile-first website for '{lead_name}', operating strictly in the '{rules['name']}' industry.

### ARCHITECTURAL INSPIRATION MODEL & DESIGN PATTERN ({archetype['name']} - {archetype['tag']}):
{archetype['prompt_spec']}

### CRITICAL INDUSTRY & BUSINESS CONSTRAINTS:
- Industry Segment: {rules['name']}
- MUST NOT use legal or medical terminology unless the client is an actual law firm or clinic. All copy, services, cards, and CTAs must be 100% focused on {rules['name']}.
- Tone of Voice: {rules['tone']}
- Aesthetics & Visual Theme: {rules['style']}
- Primary CTA: '{rules['cta_label']}' (Linking to WhatsApp)

### CRITICAL BRAND IDENTITY & VISUAL SYSTEM (MUST STRICTLY FOLLOW):
- Foundation / Background: {bg_color}
- Primary Accent & Action Elements: {primary_color}
- Secondary / Container Surfaces: {secondary_color}
- High-Contrast Text: {text_color}
- {logo_spec}
- {gallery_spec}

### BUSINESS INTELLIGENCE & DIAGNOSTIC CONTEXT:
- Business Name: {lead_name}
- Core Value Proposition: {value_prop}
- Customer Pain Points Addressed: {pain_points}
- Strategic Positioning: {approach}
- Authority & Reputation: {reputation_clause}
- Direct WhatsApp Contact: {whatsapp}
- Physical Location: {address}
{owners_clause}
### MANDATORY PAGE ARCHITECTURE (CRO OPTIMIZED):
1. Sticky Header: Logo, navigation anchor links (Soluções, Diferenciais, Avaliações, Contato), phone number badge, and '{rules['cta_label']}' button.
2. High-Impact Hero Section:
   - Badge with pulsing green or accent dot: '{rules['hero_badge']}'
   - Powerful H1 Headline: Tailored to {lead_name} and {rules['name']} (e.g. '{rules['headline']}').
   - Descriptive Subheadline addressing customer pains and advantages.
   - Dual CTAs: Primary prominent WhatsApp button + secondary phone or catalog action.
   - Google Rating & Social Proof badge with 5 golden stars.
3. Solutions / Products Grid: 4 high-converting product/service categories specific to {rules['name']}.
4. Trust & Authority Section: Highlighting Google reviews, fast local delivery or service, and founding leadership.
5. Location & Map CTA: Physical address, opening hours, and direct call-to-action.
6. Footer: Copyright 2026 {lead_name}, address, and contact information.
7. Fixed Floating WhatsApp Button: Pulsing bottom-right button for instant conversions.
"""
        return prompt
