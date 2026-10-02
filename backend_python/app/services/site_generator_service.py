import json
import logging
import re
import urllib.parse
from typing import Dict, Any, Optional, List

from app.core.config import settings
from app.integrations.gemini_ai import GeminiAIIntegration
from app.services.lp_prompt_engine import LPPromptEngine

logger = logging.getLogger(__name__)


class SiteGeneratorService:
    """
    Serviço que orquestra a geração do código HTML completo da Landing Page
    a partir do prompt de elite gerado pelas regras de negócio.
    """

    @classmethod
    async def generate_landing_page_html(
        cls,
        prompt: str,
        lead_data: Dict[str, Any],
        brand_colors: Dict[str, Any],
        owners: List[Dict[str, str]],
        logo_url: Optional[str] = None,
        gallery_urls: Optional[List[str]] = None,
        diagnostic_data: Optional[Dict[str, Any]] = None,
        archetype_id: Optional[str] = None,
    ) -> str:
        """
        Gera o código HTML completo e independente com Tailwind CSS.
        Tenta gerar via Gemini AI com regras estritas de nicho e faz fallback
        para o gerador semântico de elite 100% customizado por nicho.
        """
        lead_name = lead_data.get("name", "Empresa")
        category = lead_data.get("category", "")
        niche_key = LPPromptEngine.detect_niche(lead_name, category)
        niche_rule = LPPromptEngine.NICHE_RULES.get(niche_key, LPPromptEngine.NICHE_RULES["geral"])

        if settings.GEMINI_API_KEY:
            try:
                gemini = GeminiAIIntegration()

                photo_instructions = ""
                if gallery_urls:
                    photo_plan = LPPromptEngine.allocate_photos(gallery_urls)
                    photo_instructions = (
                        f"\n8. USO ESTRATÉGICO DE FOTOS REAIS DO GOOGLE PLACES (MANDATÓRIO):\n"
                        f"   - Hero Section: Use a foto '{photo_plan['hero']}' como destaque visual no Hero (Split Hero layout com imagem de capa destacada em container com cantos arredondados e sombra).\n"
                    )
                    if photo_plan['services']:
                        photo_instructions += f"   - Cards de Serviços/Soluções: Use as fotos {photo_plan['services']} como imagem de destaque dentro dos cards de catálogo.\n"
                    if photo_plan['structure_gallery']:
                        photo_instructions += (
                            f"   - Galeria 'Conheça Nossa Estrutura & Ambientes': Crie uma seção com grid responsivo de 3 colunas exibindo as fotos {photo_plan['structure_gallery']}.\n"
                        )
                    if photo_plan['facade']:
                        photo_instructions += f"   - Localização/Fachada: Use a foto '{photo_plan['facade']}' na seção 'Visite Nossa Unidade' junto ao endereço e mapa.\n"
                    photo_instructions += (
                        "   - REGRA CRÍTICA DO LOGOTIPO: NUNCA use fotos de estabelecimentos, fachadas ou produtos como logotipo na barra de navegação! "
                        "Se não houver logotipo oficial, use um badge tipográfico com ícone representativo do nicho.\n"
                    )

                system_prompt = (
                    "Você é um engenheiro sênior de UI/UX especializado em Landing Pages de altíssima conversão (CRO) "
                    "do Google Stitch. Gere um documento HTML5 completo, único e autônomo (single-file HTML) "
                    "estritamente de acordo com as especificações a seguir.\n\n"
                    "REGRAS OBRIGATÓRIAS E INEGOCIÁVEIS:\n"
                    f"1. O NEGÓCIO É EXCLUSIVAMENTE DO RAMO: '{niche_rule['name']}' (Nome da Empresa: {lead_name}, Categoria: {category}).\n"
                    "   É TERMINANTEMENTE PROIBIDO gerar conteúdo de outro segmento. "
                    "   Por exemplo: NUNCA gere termos de advocacia, tribunais ou jurídico se a empresa for depósito de construção, oficina, clínica médica, etc. "
                    "   Todos os títulos, blocos de serviços, diferenciais e CTAs devem ser 100% fiéis a este ramo comercial.\n"
                    "2. Use Tailwind CSS via <script src=\"https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js\"></script> ou <script src=\"https://cdn.tailwindcss.com\"></script>.\n"
                    "3. Configure as cores fornecidas no tailwind.config dentro de uma tag <script id=\"tailwind-config\">.\n"
                    "4. Use Google Fonts (Plus Jakarta Sans) e Material Symbols Outlined.\n"
                    "5. Não use textos placeholder (Lorem Ipsum). Use os dados reais fornecidos (nome, telefone, endereço, dores e diferenciais).\n"
                    "6. Adicione o botão flutuante de WhatsApp fixo no canto inferior direito com animação pulse e link correto wa.me.\n"
                    "7. Retorne APENAS o código HTML completo começando com <!DOCTYPE html> e terminando com </html>, sem explicações em markdown antes ou depois.\n"
                    f"{photo_instructions}\n"
                    f"ESPECIFICAÇÃO COMPLETA DA LANDING PAGE:\n{prompt}"
                )
                html_resp = await gemini.generate_text(system_prompt, max_tokens=7000)

                # Limpar possíveis blocos markdown ```html ... ```
                clean_html = re.sub(r"^```(?:html)?\s*", "", html_resp.strip(), flags=re.IGNORECASE)
                clean_html = re.sub(r"\s*```$", "", clean_html.strip())

                if ("<!DOCTYPE html>" in clean_html or "<html" in clean_html) and "</html>" in clean_html and len(clean_html) >= 2500:
                    # Garantir script CDN do Tailwind compatível com CSP
                    if "cdn.tailwindcss.com" in clean_html:
                        clean_html = clean_html.replace(
                            "https://cdn.tailwindcss.com",
                            "https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"
                        )
                    # Checagem de segurança de nicho: se o nicho NÃO for advocacia mas o modelo colocou 'advocacia' ou 'oab'
                    lower_clean = clean_html.lower()
                    if niche_key != "advocacia" and ("código de ética da oab" in lower_clean or "defesa rigorosa dos seus direitos" in lower_clean or "atendimento jurídico" in lower_clean):
                        logger.warning(f"Gemini alucinou conteúdo jurídico para nicho {niche_key}. Usando gerador de nicho calibrado.")
                    else:
                        clean_html = cls.hydrate_photo_tokens(clean_html, gallery_urls)
                        return clean_html
                elif clean_html:
                    logger.warning(f"Resposta do Gemini truncada ou incompleta ({len(clean_html)} chars). Recorrendo ao gerador calibrado.")
            except Exception as e:
                logger.warning(f"Geração de HTML via Gemini falhou ({e}). Usando gerador de elite local calibrado para {niche_key}.")

        return cls._build_semantic_landing_page(
            lead_data=lead_data,
            brand_colors=brand_colors,
            owners=owners,
            logo_url=logo_url,
            gallery_urls=gallery_urls,
            diagnostic_data=diagnostic_data,
            archetype_id=archetype_id,
        )

    @classmethod
    def _build_semantic_landing_page(
        cls,
        lead_data: Dict[str, Any],
        brand_colors: Dict[str, Any],
        owners: List[Dict[str, str]],
        logo_url: Optional[str] = None,
        gallery_urls: Optional[List[str]] = None,
        diagnostic_data: Optional[Dict[str, Any]] = None,
        archetype_id: Optional[str] = None,
    ) -> str:
        """
        Gerador local resiliente que compõe a Landing Page em HTML/Tailwind
        rigorosamente adaptado ao nicho e aos dados reais do lead, com distribuição
        inteligente de fotos públicas reais em seções estratégicas.
        """
        name = lead_data.get("name", "Empresa de Excelência")
        category = lead_data.get("category", "")
        phone = lead_data.get("phone") or "(11) 99999-9999"
        clean_phone = "".join(filter(str.isdigit, phone))
        address = lead_data.get("address") or lead_data.get("city") or "Brasil"
        rating = lead_data.get("google_rating") or 4.8
        reviews_count = lead_data.get("google_reviews_count") or 85

        # Detectar Nicho & Regras correspondentes
        niche_key = LPPromptEngine.detect_niche(name, category)
        niche_rules = LPPromptEngine.NICHE_RULES.get(niche_key, LPPromptEngine.NICHE_RULES["geral"])

        # Cores (detectadas ou padrão do nicho) com garantia estrita de WCAG AA/AAA
        colors = brand_colors or niche_rules.get("default_colors", {})
        bg = colors.get("background") or niche_rules["default_colors"]["background"]
        primary = colors.get("primary") or niche_rules["default_colors"]["primary"]
        secondary = colors.get("secondary") or niche_rules["default_colors"]["secondary"]
        text_color = colors.get("text") or niche_rules["default_colors"]["text"]
        on_primary = colors.get("on_primary") or LPPromptEngine.get_contrast_text_color(primary)

        # Blindagem de contraste: O card (surface-container) e o texto (on-surface) NUNCA podem ter cores iguais
        card_lum = LPPromptEngine.get_relative_luminance(secondary)
        text_lum = LPPromptEngine.get_relative_luminance(text_color)
        contrast_ratio = (max(card_lum, text_lum) + 0.05) / (min(card_lum, text_lum) + 0.05)
        if contrast_ratio < 4.5:
            # Se o contraste entre card e texto for insuficiente, restaurar superfície calibrada do nicho
            secondary = niche_rules["default_colors"]["secondary"]
            text_color = niche_rules["default_colors"]["text"]

        # Textos e CTAs do nicho
        hero_badge = niche_rules.get("hero_badge", "Excelência & Atendimento Especializado")
        headline = niche_rules.get("headline", f"{name} — Soluções Completas para Você")
        subheadline = niche_rules.get("subheadline", f"Qualidade, garantia e atendimento com quem entende do assunto em {address}.")
        if diagnostic_data and diagnostic_data.get("value_proposition"):
            subheadline = f"{diagnostic_data['value_proposition']} Qualidade garantida e atendimento especializado em {address}."
        cta_label = niche_rules.get("cta_label", "Falar no WhatsApp")
        whatsapp_msg = niche_rules.get("whatsapp_msg", f"Olá! Vim pelo site da {name} e gostaria de mais informações.")
        encoded_whatsapp_msg = urllib.parse.quote(whatsapp_msg)

        # Alocação inteligente de fotos na LP
        photo_plan = LPPromptEngine.allocate_photos(gallery_urls)

        # Montar Cards de Soluções/Produtos do Nicho (com fotos reais quando disponíveis)
        cards_html = ""
        service_photos = photo_plan["services"]
        for idx, card in enumerate(niche_rules.get("solution_cards", []), start=1):
            num_str = f"0{idx}" if idx < 10 else str(idx)
            has_photo = (idx - 1) < len(service_photos)

            if has_photo:
                header_visual = f"""
                <div class="h-44 w-full overflow-hidden rounded-xl mb-4 relative bg-surface border border-outline-variant">
                    <img src="{service_photos[idx - 1]}" alt="{card.get('title')}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
                    <div class="absolute top-2.5 right-2.5 px-2.5 py-1 rounded-lg bg-background/80 backdrop-blur-md border border-outline-variant text-[11px] font-mono font-bold text-primary">
                        {num_str}
                    </div>
                </div>
                """
            else:
                header_visual = f"""
                <div class="flex items-center justify-between mb-4">
                    <div class="w-11 h-11 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                        <span class="material-symbols-outlined text-2xl">{card.get('icon', 'check_circle')}</span>
                    </div>
                    <span class="text-xs font-mono font-bold text-on-surface/30">{num_str}</span>
                </div>
                """

            cards_html += f"""
            <div class="p-5 sm:p-6 rounded-2xl bg-surface-container border border-outline-variant hover:border-primary/50 transition-all duration-300 flex flex-col justify-between group">
                <div>
                    {header_visual}
                    <h4 class="text-lg sm:text-xl font-bold text-on-surface mb-2">{card.get('title')}</h4>
                    <p class="text-xs sm:text-sm text-on-surface/70 leading-relaxed mb-5">{card.get('desc')}</p>
                </div>
                <a href="https://wa.me/{clean_phone}?text={urllib.parse.quote(f'Olá! Gostaria de um orçamento sobre {card.get("title")}.')}" target="_blank" class="w-full py-2.5 px-3 rounded-xl bg-primary/10 hover:bg-primary text-primary hover:text-on-primary font-bold text-xs inline-flex items-center justify-center gap-1.5 transition-all text-center mt-auto">
                    <span>Pedir Cotação</span>
                    <span class="material-symbols-outlined text-sm">arrow_forward</span>
                </a>
            </div>
            """

        # Montar Seção de Liderança / Sócios (se houver)
        owners_html = ""
        if owners and len(owners) > 0:
            owners_cards = []
            for o in owners:
                initial = (o.get('name') or 'S')[0]
                role = o.get('role', 'Sócio Proprietário')
                owners_cards.append(f"""
                <div class="p-6 rounded-2xl bg-surface-container border border-outline-variant flex flex-col items-center text-center">
                    <div class="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center text-primary text-2xl font-bold mb-4 border border-primary/30 shadow-md">
                        {initial}
                    </div>
                    <h4 class="text-lg font-bold text-on-surface mb-1">{o.get('name')}</h4>
                    <span class="text-xs uppercase tracking-wider text-primary font-semibold">{role}</span>
                </div>
                """)
            owners_html = f"""
            <section class="py-16 bg-surface-container/30 border-t border-outline-variant">
                <div class="max-w-[1240px] mx-auto px-6">
                    <div class="text-center max-w-2xl mx-auto mb-12">
                        <span class="text-primary text-xs uppercase tracking-widest font-bold">Liderança & Compromisso</span>
                        <h3 class="text-2xl md:text-3xl font-bold mt-2 text-on-surface">Direção & Responsáveis</h3>
                        <p class="text-xs md:text-sm text-on-surface/70 mt-2">Profissionais comprometidos com o mais alto padrão de atendimento e transparência.</p>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-{min(len(owners), 3)} gap-6 max-w-4xl mx-auto">
                        {''.join(owners_cards)}
                    </div>
                </div>
            </section>
            """

        # Montar Galeria Dedicada de Estrutura & Ambientes (se houver 2+ fotos)
        gallery_section_html = ""
        structure_photos = photo_plan["structure_gallery"]
        if len(structure_photos) >= 2:
            niche_captions = {
                "construcao": ["Área de Estoque & Pronta-Entrega", "Showroom de Acabamentos & Materiais", "Cargas & Logística Ágil", "Espaço de Atendimento Presencial", "Linha Completa de Ferramentas", "Variedade em Hidráulica & Elétrica"],
                "automotivo": ["Boxes de Diagnóstico Computadorizado", "Elevadores & Mecânica Especializada", "Recepção Climatizada & Conforto", "Alinhamento & Balanceamento 3D", "Peças Genuínas & Lubrificantes", "Equipe Técnica Certificada"],
                "odontologia": ["Consultório & Biossegurança", "Recepção Humanizada & Climatizada", "Tecnologia de Escaneamento 3D", "Sala de Reabilitação Oral", "Ambiente Privativo de Avaliação", "Equipamentos de Última Geração"],
                "medicina": ["Consultórios Médicos Especializados", "Recepção Humanizada & Confortável", "Salas de Exames Diagnósticos", "Ambiente Seguro e Confortável", "Equipe de Atendimento Dedicada", "Estrutura Moderna Integrada"],
                "estetica": ["Cabines Privativas de Procedimentos", "Recepção Confortável & Chique", "Aparelhos de Alta Tecnologia Laser", "Espaço Relaxante & Humanizado", "Protocolos Faciais e Corporais", "Conforto e Discrição"],
                "gastronomia": ["Salão Principal Aconchegante", "Pratos Exclusivos & Receitas", "Bar de Coquetéis & Vinhos", "Ambiente Climatizado para Família", "Cozinha Artesanal & Padrão de Higiene", "Momentos & Celebrações"],
            }
            caps = niche_captions.get(niche_key, ["Ambiente & Atendimento Presencial", "Estrutura Completa & Organizada", "Espaço Preparado para Você", "Qualidade e Conforto Garantidos", "Área de Atendimento ao Cliente", "Equipamentos e Serviços"])

            photo_cards = []
            for p_idx, p_url in enumerate(structure_photos):
                cap = caps[p_idx % len(caps)]
                photo_cards.append(f"""
                <div class="group relative rounded-2xl overflow-hidden border border-outline-variant bg-surface-container aspect-[4/3] shadow-md">
                    <img src="{p_url}" alt="{cap} - {name}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" loading="lazy" />
                    <div class="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-transparent opacity-80 group-hover:opacity-100 transition-opacity"></div>
                    <div class="absolute bottom-3 left-3 right-3 flex items-center justify-between text-xs font-semibold text-on-surface">
                        <span class="truncate">{cap}</span>
                        <span class="material-symbols-outlined text-primary text-base">zoom_in</span>
                    </div>
                </div>
                """)

            gallery_section_html = f"""
            <!-- CONHEÇA NOSSA ESTRUTURA & AMBIENTE (FOTOS REAIS DO GOOGLE) -->
            <section id="estrutura" class="py-20 bg-surface-container/20 border-t border-outline-variant">
                <div class="max-w-[1320px] mx-auto px-6">
                    <div class="text-center max-w-2xl mx-auto mb-14">
                        <span class="text-primary text-xs uppercase tracking-widest font-bold">Estrutura & Ambiente</span>
                        <h3 class="text-3xl font-extrabold mt-2 text-on-surface">Conheça Nosso Espaço</h3>
                        <p class="text-sm text-on-surface/70 mt-2">Fotos reais do nosso ambiente, preparado para atender você com o mais alto padrão em {address}.</p>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {''.join(photo_cards)}
                    </div>
                </div>
            </section>
            """

        # Montar Hero Section (Split Hero com foto real quando disponível)
        hero_photo = photo_plan["hero"]
        if hero_photo:
            hero_html = f"""
            <!-- HERO SECTION (SPLIT LAYOUT COM FOTO REAL DE DESTAQUE) -->
            <section class="py-12 sm:py-20 md:py-24 relative overflow-hidden">
                <div class="max-w-[1320px] mx-auto px-4 sm:px-6 relative z-10">
                    <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
                        <div class="lg:col-span-7 flex flex-col items-start text-left">
                            <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-primary/10 border border-primary/30 mb-5 text-[11px] sm:text-xs text-primary font-bold tracking-wider uppercase shadow-sm backdrop-blur-sm">
                                <span class="h-2 w-2 rounded-full bg-primary animate-pulse shrink-0"></span>
                                <span>{hero_badge}</span>
                            </div>
                            <h1 class="text-3xl sm:text-5xl lg:text-5xl xl:text-6xl font-extrabold tracking-tight leading-tight sm:leading-tight mb-5 text-on-surface">
                                {headline}
                            </h1>
                            <p class="text-sm sm:text-base md:text-lg text-on-surface/80 max-w-2xl mb-8 sm:mb-10 leading-relaxed font-normal">
                                {subheadline}
                            </p>
                            <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                                <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="w-full sm:w-auto bg-primary text-on-primary font-extrabold px-7 sm:px-8 py-3.5 sm:py-4 rounded-xl shadow-xl hover:scale-105 active:scale-95 transition-all inline-flex items-center justify-center gap-2 text-xs sm:text-sm uppercase tracking-wider text-center">
                                    <span class="material-symbols-outlined text-lg sm:text-xl">chat</span>
                                    <span>{cta_label}</span>
                                </a>
                                <a href="tel:{clean_phone}" class="w-full sm:w-auto px-5 sm:px-6 py-3.5 sm:py-4 rounded-xl border border-outline-variant bg-surface-container hover:border-primary/50 transition-colors inline-flex items-center justify-center gap-2 text-xs sm:text-sm font-bold text-on-surface text-center">
                                    <span class="material-symbols-outlined text-base sm:text-lg text-primary">call</span>
                                    <span>Ligue: {phone}</span>
                                </a>
                            </div>
                            <div class="mt-8 sm:mt-10 inline-flex items-center gap-2 sm:gap-3 px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-full bg-surface-container border border-outline-variant text-[11px] sm:text-xs text-on-surface/80">
                                <div class="flex text-amber-400 text-xs sm:text-sm tracking-tighter">★★★★★</div>
                                <span><strong>{rating} de 5.0 estrelas</strong> no Google ({reviews_count}+ avaliações reais)</span>
                            </div>
                        </div>
                        <div class="lg:col-span-5">
                            <div class="relative group">
                                <div class="absolute -inset-1 bg-gradient-to-r from-primary/30 to-primary/10 rounded-3xl blur-xl opacity-70 group-hover:opacity-100 transition duration-500"></div>
                                <div class="relative rounded-3xl overflow-hidden border border-outline-variant shadow-2xl bg-surface-container aspect-[4/3] sm:aspect-[16/11]">
                                    <img src="{hero_photo}" alt="{name}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" loading="eager" />
                                    <div class="absolute inset-0 bg-gradient-to-t from-background/90 via-background/20 to-transparent"></div>
                                    <div class="absolute bottom-4 left-4 right-4 flex items-center justify-between p-3 rounded-2xl bg-background/80 backdrop-blur-md border border-outline-variant">
                                        <div class="flex items-center gap-2 min-w-0">
                                            <span class="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
                                            <span class="text-xs font-bold text-on-surface truncate">Unidade Oficial • Atendimento Aberto</span>
                                        </div>
                                        <span class="text-[11px] font-mono font-bold text-primary shrink-0">{rating} ★ Google</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            """
        else:
            hero_html = f"""
            <!-- HERO SECTION (CENTRALIZADO) -->
            <section class="py-12 sm:py-20 md:py-28 relative overflow-hidden">
                <div class="max-w-[1320px] mx-auto px-4 sm:px-6 relative z-10">
                    <div class="max-w-4xl mx-auto text-center flex flex-col items-center">
                        <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-primary/10 border border-primary/30 mb-5 text-[11px] sm:text-xs text-primary font-bold tracking-wider uppercase shadow-sm max-w-full backdrop-blur-sm">
                            <span class="h-2 w-2 rounded-full bg-primary animate-pulse shrink-0"></span>
                            <span class="truncate">{hero_badge}</span>
                        </div>
                        <h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight sm:leading-tight mb-5 text-on-surface">
                            {headline}
                        </h1>
                        <p class="text-sm sm:text-base md:text-lg text-on-surface/80 max-w-2xl mb-8 sm:mb-10 leading-relaxed font-normal">
                            {subheadline}
                        </p>
                        <div class="flex flex-col sm:flex-row gap-3 w-full max-w-md sm:max-w-none sm:w-auto justify-center items-stretch sm:items-center">
                            <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="w-full sm:w-auto bg-primary text-on-primary font-extrabold px-7 sm:px-8 py-3.5 sm:py-4 rounded-xl shadow-xl hover:scale-105 active:scale-95 transition-all inline-flex items-center justify-center gap-2 text-xs sm:text-sm uppercase tracking-wider text-center">
                                <span class="material-symbols-outlined text-lg sm:text-xl">chat</span>
                                <span>{cta_label}</span>
                            </a>
                            <a href="tel:{clean_phone}" class="w-full sm:w-auto px-5 sm:px-6 py-3.5 sm:py-4 rounded-xl border border-outline-variant bg-surface-container hover:border-primary/50 transition-colors inline-flex items-center justify-center gap-2 text-xs sm:text-sm font-bold text-on-surface text-center">
                                <span class="material-symbols-outlined text-base sm:text-lg text-primary">call</span>
                                <span>Ligue: {phone}</span>
                            </a>
                        </div>
                        <div class="mt-8 sm:mt-12 inline-flex items-center gap-2 sm:gap-3 px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-full bg-surface-container border border-outline-variant text-[11px] sm:text-xs text-on-surface/80">
                            <div class="flex text-amber-400 text-xs sm:text-sm tracking-tighter">★★★★★</div>
                            <span><strong>{rating} de 5.0 estrelas</strong> no Google ({reviews_count}+ avaliações reais)</span>
                        </div>
                    </div>
                </div>
            </section>
            """

        # Montar Seção de Localização (com foto real da fachada quando disponível)
        facade_photo = photo_plan["facade"]
        if facade_photo:
            location_html = f"""
            <!-- LOCALIZAÇÃO & CONTATO (COM FOTO REAL DA FACHADA) -->
            <section id="localizacao" class="py-20 border-t border-outline-variant">
                <div class="max-w-[1320px] mx-auto px-6">
                    <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
                        <div class="lg:col-span-6">
                            <div class="relative rounded-3xl overflow-hidden border border-outline-variant shadow-2xl aspect-[4/3] sm:aspect-[16/10] group">
                                <img src="{facade_photo}" alt="Fachada {name}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" loading="lazy" />
                                <div class="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-transparent"></div>
                                <div class="absolute bottom-4 left-4 right-4 flex items-center justify-between p-3 rounded-2xl bg-background/80 backdrop-blur-md border border-outline-variant">
                                    <div class="flex items-center gap-2">
                                        <span class="material-symbols-outlined text-primary text-lg">location_on</span>
                                        <span class="text-xs font-bold text-on-surface truncate">Fachada & Entrada Principal</span>
                                    </div>
                                    <span class="text-[11px] font-mono text-primary font-bold">Fácil Acesso</span>
                                </div>
                            </div>
                        </div>
                        <div class="lg:col-span-6 flex flex-col items-start text-left">
                            <span class="text-primary text-xs uppercase tracking-widest font-bold">Venha nos Conhecer</span>
                            <h3 class="text-3xl sm:text-4xl font-extrabold mt-2 mb-4 text-on-surface">Visite Nossa Unidade</h3>
                            <p class="text-sm text-on-surface/80 mb-6 flex items-start gap-2 leading-relaxed">
                                <span class="material-symbols-outlined text-primary shrink-0 mt-0.5">location_on</span>
                                <span><strong>Endereço:</strong> {address}</span>
                            </p>
                            <div class="p-4 rounded-2xl bg-surface-container border border-outline-variant w-full mb-8">
                                <div class="flex items-center gap-3 text-xs text-on-surface/80">
                                    <span class="material-symbols-outlined text-primary">schedule</span>
                                    <span><strong>Atendimento:</strong> Segunda a Sexta: 08h às 18h | Sábado: 08h às 13h</span>
                                </div>
                            </div>
                            <div class="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
                                <a href="https://maps.google.com/?q={urllib.parse.quote(name + ' ' + address)}" target="_blank" class="px-6 py-3.5 rounded-xl bg-surface-container border border-outline-variant hover:border-primary text-xs font-bold uppercase tracking-wider transition-colors flex items-center justify-center gap-2">
                                    <span class="material-symbols-outlined text-primary text-base">map</span>
                                    Abrir no Google Maps
                                </a>
                                <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="bg-primary text-on-primary px-6 py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider shadow-lg hover:scale-105 transition-transform flex items-center justify-center gap-2">
                                    <span class="material-symbols-outlined text-base">chat</span>
                                    Chamar no WhatsApp
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            """
        else:
            location_html = f"""
            <!-- LOCALIZAÇÃO & CONTATO -->
            <section id="localizacao" class="py-20 border-t border-outline-variant">
                <div class="max-w-[1320px] mx-auto px-6 text-center">
                    <div class="max-w-2xl mx-auto">
                        <span class="text-primary text-xs uppercase tracking-widest font-bold">Venha nos Conhecer</span>
                        <h3 class="text-3xl font-extrabold mt-2 mb-4 text-on-surface">Visite Nossa Unidade</h3>
                        <p class="text-sm text-on-surface/70 mb-8 flex items-center justify-center gap-2">
                            <span class="material-symbols-outlined text-primary">location_on</span>
                            {address}
                        </p>
                        <div class="flex flex-col sm:flex-row gap-4 justify-center">
                            <a href="https://maps.google.com/?q={urllib.parse.quote(name + ' ' + address)}" target="_blank" class="px-6 py-3.5 rounded-xl bg-surface-container border border-outline-variant hover:border-primary text-xs font-bold uppercase tracking-wider transition-colors flex items-center justify-center gap-2">
                                <span class="material-symbols-outlined text-primary text-base">map</span>
                                Abrir no Google Maps
                            </a>
                            <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="bg-primary text-on-primary px-6 py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider shadow-lg hover:scale-105 transition-transform flex items-center justify-center gap-2">
                                <span class="material-symbols-outlined text-base">chat</span>
                                Chamar no WhatsApp
                            </a>
                        </div>
                    </div>
                </div>
            </section>
            """

        # Logotipo na navbar: nunca usar foto de estabelecimento como logo
        clean_logo = logo_url if (logo_url and "lh3.googleusercontent.com" not in logo_url and logo_url not in photo_plan["all_photos"]) else None
        if clean_logo:
            logo_elem = f'<img src="{clean_logo}" alt="{name}" class="h-8 sm:h-10 w-auto object-contain max-w-[140px] sm:max-w-none" />'
        else:
            niche_icon = niche_rules.get("icon", "store")
            logo_elem = f"""
            <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shrink-0 shadow-sm">
                    <span class="material-symbols-outlined text-xl sm:text-2xl">{niche_icon}</span>
                </div>
                <span class="text-sm sm:text-base md:text-lg font-extrabold text-on-surface tracking-tight truncate max-w-[170px] sm:max-w-xs">{name}</span>
            </div>
            """

        estrutura_nav_link = '<a href="#estrutura" class="hover:text-primary transition-colors">Estrutura</a>' if len(structure_photos) >= 2 else ''

        return f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark scroll-smooth">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0"/>
    <title>{name} | {niche_rules['name']}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com"/>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
    <script id="tailwind-config">
        tailwind.config = {{
            darkMode: "class",
            theme: {{
                extend: {{
                    colors: {{
                        "background": "{bg}",
                        "surface": "{bg}",
                        "surface-container": "{secondary}",
                        "primary": "{primary}",
                        "on-primary": "{on_primary}",
                        "on-surface": "{text_color}",
                        "outline-variant": "rgba(255,255,255,0.12)"
                    }},
                    fontFamily: {{
                        sans: ['"Plus Jakarta Sans"', 'sans-serif']
                    }}
                }}
            }}
        }};
    </script>
</head>
<body class="bg-background text-on-surface font-sans antialiased selection:bg-primary selection:text-on-primary">
    <!-- TOP NAVIGATION (100% RESPONSIVA) -->
    <header class="sticky top-0 z-40 bg-background/90 backdrop-blur-md border-b border-outline-variant">
        <div class="max-w-[1320px] mx-auto px-4 sm:px-6 h-16 sm:h-20 flex justify-between items-center gap-2">
            <div class="flex items-center gap-2 min-w-0">
                {logo_elem}
            </div>
            <nav class="hidden lg:flex items-center gap-7 text-sm font-semibold">
                <a href="#solucoes" class="hover:text-primary transition-colors">Produtos & Serviços</a>
                {estrutura_nav_link}
                <a href="#diferenciais" class="hover:text-primary transition-colors">Diferenciais</a>
                <a href="#avaliacoes" class="hover:text-primary transition-colors">Avaliações</a>
                <a href="#localizacao" class="hover:text-primary transition-colors">Localização</a>
            </nav>
            <div class="flex items-center gap-2 sm:gap-3 shrink-0">
                <a href="tel:{clean_phone}" class="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-2 border border-outline-variant rounded-lg hover:border-primary transition-colors">
                    <span class="material-symbols-outlined text-primary text-base">call</span>
                    <span>{phone}</span>
                </a>
                <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="bg-primary text-on-primary font-bold text-[11px] sm:text-xs uppercase tracking-wider px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg shadow-md hover:opacity-95 active:scale-95 transition-all inline-flex items-center gap-1.5 whitespace-nowrap">
                    <span class="material-symbols-outlined text-sm sm:text-base">chat</span>
                    <span>{cta_label}</span>
                </a>
            </div>
        </div>
    </header>

    {hero_html}

    <!-- PRODUTOS / SERVIÇOS DO NICHO -->
    <section id="solucoes" class="py-20 bg-surface-container/20 border-t border-outline-variant">
        <div class="max-w-[1320px] mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-16">
                <span class="text-primary text-xs uppercase tracking-widest font-bold">Catálogo & Soluções</span>
                <h3 class="text-3xl font-extrabold mt-2 text-on-surface">O que oferecemos com máxima qualidade</h3>
                <p class="text-sm text-on-surface/70 mt-2">Linha completa, pronta-entrega e atendimento rápido para sua necessidade.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {cards_html}
            </div>
        </div>
    </section>

    {gallery_section_html}

    <!-- DIFERENCIAIS -->
    <section id="diferenciais" class="py-20 border-t border-outline-variant">
        <div class="max-w-[1320px] mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-16">
                <span class="text-primary text-xs uppercase tracking-widest font-bold">Por Que Escolher a {name}?</span>
                <h3 class="text-3xl font-extrabold mt-2 text-on-surface">Compromisso com o seu melhor resultado</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="p-8 rounded-2xl bg-surface-container border border-outline-variant text-center">
                    <div class="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary text-2xl mx-auto mb-5">
                        <span class="material-symbols-outlined text-3xl">bolt</span>
                    </div>
                    <h4 class="text-xl font-bold mb-2">Agilidade & Pronta-Entrega</h4>
                    <p class="text-sm text-on-surface/70 leading-relaxed">Processamento rápido do seu pedido com entrega garantida e pontual para não atrasar seu cronograma.</p>
                </div>
                <div class="p-8 rounded-2xl bg-surface-container border border-outline-variant text-center">
                    <div class="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary text-2xl mx-auto mb-5">
                        <span class="material-symbols-outlined text-3xl">verified</span>
                    </div>
                    <h4 class="text-xl font-bold mb-2">Marcas de Confiança</h4>
                    <p class="text-sm text-on-surface/70 leading-relaxed">Trabalhamos exclusivamente com fornecedores homologados e produtos com certificação e garantia de fábrica.</p>
                </div>
                <div class="p-8 rounded-2xl bg-surface-container border border-outline-variant text-center">
                    <div class="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary text-2xl mx-auto mb-5">
                        <span class="material-symbols-outlined text-3xl">support_agent</span>
                    </div>
                    <h4 class="text-xl font-bold mb-2">Cotação Instantânea no WhatsApp</h4>
                    <p class="text-sm text-on-surface/70 leading-relaxed">Nossa equipe atende prontamente para tirar dúvidas técnicas e enviar propostas comerciais sem burocracia.</p>
                </div>
            </div>
        </div>
    </section>

    {owners_html}

    <!-- AVALIAÇÕES / PROVA SOCIAL -->
    <section id="avaliacoes" class="py-20 bg-surface-container/20 border-t border-outline-variant">
        <div class="max-w-[1320px] mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-14">
                <span class="text-primary text-xs uppercase tracking-widest font-bold">Reputação Comprovada</span>
                <h3 class="text-3xl font-extrabold mt-2 text-on-surface">Reconhecido pelos nossos clientes</h3>
            </div>
            <div class="max-w-3xl mx-auto bg-surface-container p-8 rounded-3xl border border-outline-variant flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
                <div>
                    <div class="flex items-center gap-3 mb-2">
                        <span class="text-3xl font-extrabold text-primary">{rating}</span>
                        <div class="flex text-amber-400 text-lg">★★★★★</div>
                    </div>
                    <p class="text-sm text-on-surface font-semibold">Avaliação consolidada no Google Business</p>
                    <p class="text-xs text-on-surface/60 mt-1">Mais de {reviews_count} clientes satisfeitos com atendimento, preço e qualidade.</p>
                </div>
                <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="shrink-0 bg-primary text-on-primary font-bold text-xs uppercase tracking-wider px-6 py-3.5 rounded-xl shadow-lg hover:scale-105 transition-transform flex items-center gap-2">
                    <span class="material-symbols-outlined text-lg">chat</span>
                    Solicitar Atendimento VIP
                </a>
            </div>
        </div>
    </section>

    {location_html}

    <!-- FOOTER -->
    <footer class="py-12 bg-background border-t border-outline-variant text-center text-xs text-on-surface/60">
        <div class="max-w-[1320px] mx-auto px-6">
            <p class="mb-2 font-medium">© 2026 {name}. Todos os direitos reservados. {address}.</p>
            <p class="text-[11px] text-on-surface/40">Desenvolvido com foco em alta performance, velocidade e conversão.</p>
        </div>
    </footer>

    <!-- STICKY FLOATING WHATSAPP BUTTON (COMPACTO NO MOBILE / EXPANDIDO NO DESKTOP) -->
    <div class="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50">
        <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="flex items-center gap-2 bg-[#25D366] hover:bg-[#20ba59] text-gray-950 font-extrabold p-3 sm:px-4 sm:py-3 rounded-full shadow-[0_4px_25px_rgba(37,211,102,0.4)] transition-all duration-300 hover:scale-110 active:scale-95" title="Falar no WhatsApp">
            <span class="relative flex h-3 w-3">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                <span class="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
            </span>
            <span class="material-symbols-outlined text-2xl sm:text-xl">chat</span>
            <span class="hidden sm:inline text-xs uppercase tracking-wider pr-1">Atendimento WhatsApp</span>
        </a>
    </div>
</body>
</html>"""

    @classmethod
    def hydrate_photo_tokens(cls, html_code: str, gallery_urls: Optional[List[str]]) -> str:
        """
        Substitui os tokens seguros '__PHOTO_...__' pelas URLs reais e perfeitas da CDN do Google Places.
        Também corrige eventuais alucinações de caracteres em URLs do Google Places geradas diretamente pela IA
        e impede que fotos de estabelecimentos vazem para o logotipo na navbar.
        """
        if not html_code:
            return html_code

        token_map = LPPromptEngine.get_photo_token_map(gallery_urls)
        hydrated = html_code

        # 1. Substituição de tokens explícitos
        for token, real_url in token_map.items():
            hydrated = hydrated.replace(token, real_url)

        # 2. Correção de alucinações caso a LLM tenha gerado URLs do Google Places com pequenas alterações de caractere
        if gallery_urls:
            found_lh3 = re.findall(r'https://lh3\.googleusercontent\.com/[^\s"\'<>]+', hydrated)
            for raw_lh3 in found_lh3:
                if raw_lh3 not in gallery_urls:
                    best_match = None
                    best_prefix_len = 0
                    for real_u in gallery_urls:
                        prefix_len = 0
                        while prefix_len < min(len(raw_lh3), len(real_u)) and raw_lh3[prefix_len] == real_u[prefix_len]:
                            prefix_len += 1
                        if prefix_len > best_prefix_len:
                            best_prefix_len = prefix_len
                            best_match = real_u
                    if best_match and best_prefix_len > 30:
                        hydrated = hydrated.replace(raw_lh3, best_match)

        # 3. Blindagem da navbar: Se por acaso alguma foto de galeria foi colocada dentro do <header>, remove
        if "</header>" in hydrated and gallery_urls:
            header_part, rest = hydrated.split("</header>", 1)
            for real_u in gallery_urls:
                if real_u in header_part:
                    header_part = re.sub(rf'<img[^>]+src=["\']{re.escape(real_u)}["\'][^>]*>', '', header_part)
            hydrated = header_part + "</header>" + rest

        return hydrated

