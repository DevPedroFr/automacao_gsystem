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
            "default_colors": {"background": "#0F172A", "primary": "#F97316", "secondary": "#1E293B", "text": "#FFFFFF", "on_primary": "#FFFFFF"}
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
            "default_colors": {"background": "#090D16", "primary": "#EF4444", "secondary": "#161F30", "text": "#FFFFFF", "on_primary": "#FFFFFF"}
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
            "default_colors": {"background": "#0C1B2A", "primary": "#14B8A6", "secondary": "#132D42", "text": "#FFFFFF", "on_primary": "#090D16"}
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
            "default_colors": {"background": "#0B1528", "primary": "#38BDF8", "secondary": "#162544", "text": "#FFFFFF", "on_primary": "#090D16"}
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
            "default_colors": {"background": "#140D11", "primary": "#F59E0B", "secondary": "#261720", "text": "#FFFFFF", "on_primary": "#090D16"}
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
            "default_colors": {"background": "#1C100B", "primary": "#F97316", "secondary": "#331E15", "text": "#FFFFFF", "on_primary": "#FFFFFF"}
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
            "default_colors": {"background": "#0B0F17", "primary": "#D4AF37", "secondary": "#18202F", "text": "#FFFFFF", "on_primary": "#090D16"}
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
            "default_colors": {"background": "#0B132B", "primary": "#3B82F6", "secondary": "#1C2541", "text": "#FFFFFF", "on_primary": "#FFFFFF"}
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
            "default_colors": {"background": "#0F131C", "primary": "#3B82F6", "secondary": "#1E293B", "text": "#FFFFFF", "on_primary": "#FFFFFF"}
        }
    }

    @classmethod
    def get_relative_luminance(cls, hex_color: str) -> float:
        """Calcula a luminância relativa WCAG (0.0 a 1.0) de uma cor HEX."""
        if not hex_color or not isinstance(hex_color, str):
            return 0.5
        hex_clean = hex_color.lstrip("#")
        if len(hex_clean) == 3:
            hex_clean = "".join(c * 2 for c in hex_clean)
        if len(hex_clean) != 6:
            return 0.5
        try:
            r = int(hex_clean[0:2], 16) / 255.0
            g = int(hex_clean[2:4], 16) / 255.0
            b = int(hex_clean[4:6], 16) / 255.0
        except ValueError:
            return 0.5

        def adjust(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    @classmethod
    def get_contrast_text_color(cls, bg_hex: str) -> str:
        """
        Retorna '#090D16' (escuro) ou '#FFFFFF' (claro) para garantir conformidade WCAG AA/AAA.
        Se a cor de fundo tiver luminância > 0.40, texto escuro é obrigatório para legibilidade.
        """
        lum = cls.get_relative_luminance(bg_hex)
        return "#090D16" if lum > 0.40 else "#FFFFFF"

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

        # 4. Estética, beleza, salões, estética corporal/facial (PRECEDE medicina para evitar falso-positivo em 'clínica')
        if any(w in text for w in ["estet", "estét", "beleza", "salao", "salão", "hair", "spa", "laser", "harmoniz", "botox", "barbearia", "barber", "depila", "sobrancelha", "unha", "esmalt", "micropigment", "cilios", "cílios", "podolog"]):
            return "estetica"

        # 5. Odontologia e dentistas (PRECEDE medicina para evitar falso-positivo em 'clínica')
        if any(w in text for w in ["odonto", "dentist", "sorriso", "implant", "orto", "clareamento", "protese", "prótese", "endodont", "periodont"]):
            return "odontologia"

        # 6. Medicina e saúde especializada
        if any(w in text for w in ["medic", "médic", "hospital", "dr.", "dra.", "doutor", "doutora", "saude", "saúde", "oftalm", "dermato", "pediatr", "cardiolog", "ortoped", "fisioter", "psicolog", "ginecolog", "urolog", "neurolog", "endocrino", "consulta", "exame", "ultrassom", "laborator", "laboratór"]):
            return "medicina"

        # 7. Gastronomia, restaurantes, bares
        if any(w in text for w in ["restaurante", "pizz", "burger", "lanche", "bistr", "cafe", "café", "culin", "gastron", "churrasc", "sushi", "padaria", "confeitaria", "bar ", "choperia"]):
            return "gastronomia"

        # 8. Imobiliária
        if any(w in text for w in ["imobil", "imóveis", "imoveis", "corretor", "creci", "locacao", "locação", "loteamento"]):
            return "imobiliaria"

        # 9. Fallback clínico: se tiver 'clínica' sem qualificador específico
        if any(w in text for w in ["clinic", "clínica"]):
            return "medicina"

        return "geral"

    @classmethod
    def allocate_photos(cls, gallery_urls: Optional[List[str]]) -> Dict[str, Any]:
        """
        Analisa e distribui estrategicamente as fotos públicas reais coletadas do Google Places
        para posições de alto impacto e conversão (CRO) na Landing Page:
        - hero: Foto principal (visão geral, fachada moderna ou destaque da empresa)
        - services: Lista de fotos para os cards de produtos/serviços
        - structure_gallery: Coleção de fotos para a seção dedicada 'Conheça Nossa Estrutura & Ambientes'
        - facade: Foto da fachada/local para a seção de localização 'Visite Nossa Unidade'
        """
        urls = [u for u in (gallery_urls or []) if u and isinstance(u, str) and u.strip()]
        if not urls:
            return {
                "hero": None,
                "services": [],
                "structure_gallery": [],
                "facade": None,
                "all_photos": [],
                "count": 0,
            }

        total = len(urls)
        if total == 1:
            return {
                "hero": urls[0],
                "services": [],
                "structure_gallery": [],
                "facade": urls[0],
                "all_photos": urls,
                "count": 1,
            }

        if total == 2:
            return {
                "hero": urls[0],
                "services": [urls[1]],
                "structure_gallery": [urls[0], urls[1]],
                "facade": urls[1],
                "all_photos": urls,
                "count": 2,
            }

        if total == 3:
            return {
                "hero": urls[0],
                "services": [urls[1]],
                "structure_gallery": [urls[1], urls[2]],
                "facade": urls[2],
                "all_photos": urls,
                "count": 3,
            }

        if total == 4:
            return {
                "hero": urls[0],
                "services": [urls[1], urls[2]],
                "structure_gallery": [urls[1], urls[2], urls[3]],
                "facade": urls[3],
                "all_photos": urls,
                "count": 4,
            }

        # 5 a 8+ fotos: hero (0), serviços (1 a 3), galeria completa (1 até 7), fachada (foto 4 ou última)
        return {
            "hero": urls[0],
            "services": urls[1:4],
            "structure_gallery": urls[1:min(total, 7)],
            "facade": urls[min(4, total - 1)],
            "all_photos": urls,
            "count": total,
        }

    @classmethod
    def get_photo_token_map(cls, gallery_urls: Optional[List[str]]) -> Dict[str, str]:
        """
        Retorna um dicionário mapeando tokens seguros para LLM (ex: '__PHOTO_HERO__')
        para as URLs exatas da CDN do Google Places. Isso impede que o modelo alucine
        ou corrompa hashes de 180 caracteres na geração de código HTML.
        """
        plan = cls.allocate_photos(gallery_urls)
        tokens = {}
        if plan["hero"]:
            tokens["__PHOTO_HERO__"] = plan["hero"]
        if plan["facade"]:
            tokens["__PHOTO_FACADE__"] = plan["facade"]
        for idx, s_url in enumerate(plan["services"], start=1):
            tokens[f"__PHOTO_SERVICE_{idx}__"] = s_url
        for idx, g_url in enumerate(plan["structure_gallery"], start=1):
            tokens[f"__PHOTO_GALLERY_{idx}__"] = g_url
        return tokens

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
        on_primary_color = colors.get("on_primary") or cls.get_contrast_text_color(primary_color)

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
        niche_insights = diagnostic_data.get("niche_insights") or ""

        # Gafes comerciais detectadas (contextualização para o gerador)
        blunders_context = ""
        blunders_list = diagnostic_data.get("critical_blunders") or []
        if blunders_list:
            blunder_lines = []
            for b in blunders_list:
                if isinstance(b, dict):
                    blunder_lines.append(
                        f"  - BLUNDER [{b.get('severity', 'HIGH')}]: {b.get('title', '')} → "
                        f"LP MUST solve this by: {b.get('lp_solution', '')}"
                    )
            blunders_context = "\n".join(blunder_lines)

        # Alocação inteligente de fotos na LP
        photo_plan = cls.allocate_photos(gallery_urls)

        # Sanatização de Logo: Nunca use foto de fachada/loja como logotipo na navbar
        clean_logo = logo_url if (logo_url and "lh3.googleusercontent.com" not in logo_url and logo_url not in photo_plan["all_photos"]) else None
        logo_spec = f"Logo: Use official brand logo at '{clean_logo}'." if clean_logo else f"Logo: Render a modern typographic brand badge with niche icon."

        if photo_plan["count"] > 0:
            photo_spec_lines = [
                f"### STRATEGIC PHOTO PLACEMENT & VISUAL ARCHITECTURE BLUEPRINT (MANDATORY):",
                f"We gathered {photo_plan['count']} verified, high-resolution public photos of this business from Google Places.",
                f"You MUST distribute them across the landing page with visual intention to maximize credibility and conversion.",
                f"CRITICAL INSTRUCTION: To prevent CDN hash truncation errors, use the exact token placeholders in your <img> src attributes:",
                f"- HERO SHOWCASE IMAGE: Use src=\"__PHOTO_HERO__\" in the Split Hero layout (right column of desktop hero or featured media container with rounded-3xl border, glassmorphism badge 'Estrutura Completa & Atendimento Local', and soft glow).",
            ]
            if photo_plan["services"]:
                for s_idx in range(1, len(photo_plan["services"]) + 1):
                    photo_spec_lines.append(f"- SERVICE CARD {s_idx} IMAGE: Use src=\"__PHOTO_SERVICE_{s_idx}__\" as a visual header inside Solution Card #{s_idx}.")
            if photo_plan["structure_gallery"]:
                tokens_list = [f'src="__PHOTO_GALLERY_{g_idx}__"' for g_idx in range(1, len(photo_plan["structure_gallery"]) + 1)]
                photo_spec_lines.append(
                    f"- DEDICATED STRUCTURE & ATMOSPHERE GALLERY SECTION: Create a dedicated 3-column photo grid section ('Conheça Nossa Estrutura & Ambientes') featuring: {', '.join(tokens_list)}. Each card must have rounded-2xl corners, hover-zoom effect (group-hover:scale-105 transition-transform), and a caption matching {rules['name']}."
                )
            if photo_plan["facade"]:
                photo_spec_lines.append(
                    f"- LOCATION & FACADE SHOWCASE: Use src=\"__PHOTO_FACADE__\" in the 'Visite Nossa Unidade' section, positioned side-by-side with the physical address, opening hours, and Google Maps directions button."
                )
            photo_spec_lines.append(
                f"- CRITICAL LOGO RULE: NEVER use establishment photos as the navbar logo! Navbar MUST display a clean typographic brand badge."
            )
            gallery_spec = "\n".join(photo_spec_lines)
        else:
            gallery_spec = f"Use high-quality commercial photography strictly matching {rules['name']}."

        prompt = f"""Create an exceptional, high-converting, mobile-first website for '{lead_name}', operating strictly in the '{rules['name']}' industry.

### ARCHITECTURAL INSPIRATION MODEL & DESIGN PATTERN ({archetype['name']} - {archetype['tag']}):
{archetype['prompt_spec']}

### CRITICAL INDUSTRY & BUSINESS CONSTRAINTS:
- Industry Segment: {rules['name']}
- MUST NOT use legal or medical terminology unless the client is an actual law firm or clinic. All copy, services, cards, and CTAs must be 100% focused on {rules['name']}.
- Tone of Voice: {rules['tone']}
- Aesthetics & Visual Theme: {rules['style']}
- Primary CTA: '{rules['cta_label']}' (Linking to WhatsApp)

### CRITICAL BRAND IDENTITY & VISUAL SYSTEM (WCAG ACCESSIBILITY & CRO COMPLIANT):
- Foundation / Background: {bg_color}
- Primary Accent & Action Elements: {primary_color}
- Primary Action Text Color (on-primary): {on_primary_color} (MANDATORY: text on {primary_color} buttons MUST use {on_primary_color} — NEVER use background color or low-contrast text!)
- Secondary / Container Surfaces (Cards): {secondary_color} (MUST be a distinct container surface with crystal-clear contrast against text {text_color} — cards and text must NEVER share the same color!)
- High-Contrast Text: {text_color}
- Badges & Pills: Always use bg-primary/10 border border-primary/30 text-primary (NEVER unreadable solid low-contrast badges!)
- {logo_spec}

{gallery_spec}

### BUSINESS INTELLIGENCE & DIAGNOSTIC CONTEXT:
- Business Name: {lead_name}
- Core Value Proposition: {value_prop}
- Customer Pain Points Addressed: {pain_points}
- Strategic Positioning: {approach}
- Authority & Reputation: {reputation_clause}
- Direct WhatsApp Contact: {whatsapp}
- Physical Location: {address}
{owners_clause}
### CRITICAL BUSINESS BLUNDERS DETECTED (The LP MUST address these):
{blunders_context or '  No critical blunders detected — focus on maximum conversion and trust.'}

### NICHE-SPECIFIC STRATEGIC INSIGHT:
{niche_insights or f'Focus on what differentiates {lead_name} from competitors in the {rules["name"]} segment.'}

### MANDATORY PAGE ARCHITECTURE (CRO OPTIMIZED):
1. Sticky Header: Logo (typographic brand badge or official logo, NEVER a building photo), navigation anchor links (Soluções, Diferenciais, Avaliações, Contato), phone number badge, and '{rules['cta_label']}' button.
2. High-Impact Split Hero Section:
   - Badge with pulsing green or accent dot: '{rules['hero_badge']}'
   - Powerful H1 Headline: Tailored to {lead_name} and {rules['name']}. MUST directly address the #1 blunder detected.
   - Descriptive Subheadline addressing customer pains and advantages.
   - Dual CTAs: Primary prominent WhatsApp button + secondary phone or catalog action.
   - Google Rating & Social Proof badge with 5 golden stars.
   - Visual Showcase: Featured photo card with rounded corners and border.
3. Solutions / Products Grid: 4 high-converting product/service categories specific to {rules['name']}. Real photos embedded as card headers when available. Each card MUST have a direct WhatsApp quote button.
4. Dedicated Structure & Facility Showcase: Responsive 3-column photo gallery of the physical store/space with Google Places photos and niche captions.
5. Trust & Authority Section: Highlighting Google reviews, fast local delivery or service, and founding leadership. MUST include trust badges (Garantia, Pronta-Entrega, Empresa Verificada).
6. Location & Map CTA: Split layout with physical facade photo, address, opening hours, and direct call-to-action.
7. Footer: Copyright 2026 {lead_name}, address, and contact information.
8. Fixed Floating WhatsApp Button: Pulsing bottom-right button for instant conversions — ZERO friction contact.
"""
        return prompt
