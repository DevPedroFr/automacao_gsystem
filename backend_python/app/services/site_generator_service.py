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
                    "7. Retorne APENAS o código HTML completo começando com <!DOCTYPE html> e terminando com </html>, sem explicações em markdown antes ou depois.\n\n"
                    f"ESPECIFICAÇÃO COMPLETA DA LANDING PAGE:\n{prompt}"
                )
                html_resp = await gemini.generate_text(system_prompt, max_tokens=7000)
                
                # Limpar possíveis blocos markdown ```html ... ```
                clean_html = re.sub(r"^```(?:html)?\s*", "", html_resp.strip(), flags=re.IGNORECASE)
                clean_html = re.sub(r"\s*```$", "", clean_html.strip())
                
                if "<!DOCTYPE html>" in clean_html or "<html" in clean_html:
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
                        return clean_html
            except Exception as e:
                logger.warning(f"Geração de HTML via Gemini falhou ({e}). Usando gerador de elite local calibrado para {niche_key}.")

        return cls._build_semantic_landing_page(
            lead_data=lead_data,
            brand_colors=brand_colors,
            owners=owners,
            logo_url=logo_url,
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
        diagnostic_data: Optional[Dict[str, Any]] = None,
        archetype_id: Optional[str] = None,
    ) -> str:
        """
        Gerador local resiliente que compõe a Landing Page em HTML/Tailwind
        rigorosamente adaptado ao nicho e aos dados reais do lead.
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

        # Cores (detectadas ou padrão do nicho)
        colors = brand_colors or niche_rules.get("default_colors", {})
        bg = colors.get("background") or niche_rules["default_colors"]["background"]
        primary = colors.get("primary") or niche_rules["default_colors"]["primary"]
        secondary = colors.get("secondary") or niche_rules["default_colors"]["secondary"]
        text_color = colors.get("text") or niche_rules["default_colors"]["text"]

        # Textos e CTAs do nicho
        hero_badge = niche_rules.get("hero_badge", "Excelência & Atendimento Especializado")
        headline = niche_rules.get("headline", f"{name} — Soluções Completas para Você")
        subheadline = niche_rules.get("subheadline", f"Qualidade, garantia e atendimento com quem entende do assunto em {address}.")
        if diagnostic_data and diagnostic_data.get("value_proposition"):
            subheadline = f"{diagnostic_data['value_proposition']} Qualidade garantida e atendimento especializado em {address}."
        cta_label = niche_rules.get("cta_label", "Falar no WhatsApp")
        whatsapp_msg = niche_rules.get("whatsapp_msg", f"Olá! Vim pelo site da {name} e gostaria de mais informações.")
        encoded_whatsapp_msg = urllib.parse.quote(whatsapp_msg)

        # Montar Cards de Soluções/Produtos do Nicho
        cards_html = ""
        for idx, card in enumerate(niche_rules.get("solution_cards", []), start=1):
            num_str = f"0{idx}" if idx < 10 else str(idx)
            cards_html += f"""
            <div class="p-5 sm:p-6 rounded-2xl bg-surface-container border border-outline-variant hover:border-primary/50 transition-all duration-300 flex flex-col justify-between group">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <div class="w-11 h-11 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                            <span class="material-symbols-outlined text-2xl">{card.get('icon', 'check_circle')}</span>
                        </div>
                        <span class="text-xs font-mono font-bold text-on-surface/30">{num_str}</span>
                    </div>
                    <h4 class="text-lg sm:text-xl font-bold text-on-surface mb-2">{card.get('title')}</h4>
                    <p class="text-xs sm:text-sm text-on-surface/70 leading-relaxed mb-5">{card.get('desc')}</p>
                </div>
                <a href="https://wa.me/{clean_phone}?text={urllib.parse.quote(f'Olá! Gostaria de um orçamento sobre {card.get("title")}.')}" target="_blank" class="w-full py-2.5 px-3 rounded-xl bg-primary/10 hover:bg-primary text-primary hover:text-background font-bold text-xs inline-flex items-center justify-center gap-1.5 transition-all text-center mt-auto">
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

        logo_elem = f'<img src="{logo_url}" alt="{name}" class="h-8 sm:h-10 w-auto object-contain max-w-[140px] sm:max-w-none" />' if logo_url else f'<span class="text-sm sm:text-base md:text-lg font-bold text-primary tracking-tight truncate max-w-[170px] sm:max-w-xs">{name}</span>'

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
<body class="bg-background text-on-surface font-sans antialiased selection:bg-primary selection:text-background">
    <!-- TOP NAVIGATION (100% RESPONSIVA) -->
    <header class="sticky top-0 z-40 bg-background/90 backdrop-blur-md border-b border-outline-variant">
        <div class="max-w-[1320px] mx-auto px-4 sm:px-6 h-16 sm:h-20 flex justify-between items-center gap-2">
            <div class="flex items-center gap-2 min-w-0">
                {logo_elem}
            </div>
            <nav class="hidden lg:flex items-center gap-7 text-sm font-semibold">
                <a href="#solucoes" class="hover:text-primary transition-colors">Produtos & Serviços</a>
                <a href="#diferenciais" class="hover:text-primary transition-colors">Diferenciais</a>
                <a href="#avaliacoes" class="hover:text-primary transition-colors">Avaliações</a>
                <a href="#localizacao" class="hover:text-primary transition-colors">Localização</a>
            </nav>
            <div class="flex items-center gap-2 sm:gap-3 shrink-0">
                <a href="tel:{clean_phone}" class="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-2 border border-outline-variant rounded-lg hover:border-primary transition-colors">
                    <span class="material-symbols-outlined text-primary text-base">call</span>
                    <span>{phone}</span>
                </a>
                <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="bg-primary text-background font-bold text-[11px] sm:text-xs uppercase tracking-wider px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg shadow-md hover:opacity-95 active:scale-95 transition-all inline-flex items-center gap-1.5 whitespace-nowrap">
                    <span class="material-symbols-outlined text-sm sm:text-base">chat</span>
                    <span>{cta_label}</span>
                </a>
            </div>
        </div>
    </header>

    <!-- HERO SECTION -->
    <section class="py-12 sm:py-20 md:py-28 relative overflow-hidden">
        <div class="max-w-[1320px] mx-auto px-4 sm:px-6 relative z-10">
            <div class="max-w-4xl mx-auto text-center flex flex-col items-center">
                <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-surface-container border border-primary/30 mb-5 text-[11px] sm:text-xs text-primary font-bold tracking-wider uppercase shadow-sm max-w-full">
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
                    <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="w-full sm:w-auto bg-primary text-background font-extrabold px-7 sm:px-8 py-3.5 sm:py-4 rounded-xl shadow-xl hover:scale-105 active:scale-95 transition-all inline-flex items-center justify-center gap-2 text-xs sm:text-sm uppercase tracking-wider text-center">
                        <span class="material-symbols-outlined text-lg sm:text-xl">chat</span>
                        <span>{cta_label}</span>
                    </a>
                    <a href="tel:{clean_phone}" class="w-full sm:w-auto px-5 sm:px-6 py-3.5 sm:py-4 rounded-xl border border-outline-variant bg-surface-container hover:border-primary/50 transition-colors inline-flex items-center justify-center gap-2 text-xs sm:text-sm font-bold text-on-surface text-center">
                        <span class="material-symbols-outlined text-base sm:text-lg text-primary">call</span>
                        <span>Ligue: {phone}</span>
                    </a>
                </div>
                <!-- SOCIAL PROOF BADGE -->
                <div class="mt-8 sm:mt-12 inline-flex items-center gap-2 sm:gap-3 px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-full bg-surface-container border border-outline-variant text-[11px] sm:text-xs text-on-surface/80">
                    <div class="flex text-amber-400 text-xs sm:text-sm tracking-tighter">
                        ★★★★★
                    </div>
                    <span><strong>{rating} de 5.0 estrelas</strong> no Google ({reviews_count}+ avaliações reais)</span>
                </div>
            </div>
        </div>
    </section>

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
                <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="shrink-0 bg-primary text-background font-bold text-xs uppercase tracking-wider px-6 py-3.5 rounded-xl shadow-lg hover:scale-105 transition-transform flex items-center gap-2">
                    <span class="material-symbols-outlined text-lg">chat</span>
                    Solicitar Atendimento VIP
                </a>
            </div>
        </div>
    </section>

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
                    <a href="https://wa.me/{clean_phone}?text={encoded_whatsapp_msg}" target="_blank" class="bg-primary text-background px-6 py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider shadow-lg hover:scale-105 transition-transform flex items-center justify-center gap-2">
                        <span class="material-symbols-outlined text-base">chat</span>
                        Chamar no WhatsApp
                    </a>
                </div>
            </div>
        </div>
    </section>

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
