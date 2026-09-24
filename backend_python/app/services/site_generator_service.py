import json
import logging
import re
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
    ) -> str:
        """
        Gera o código HTML completo e independente com Tailwind CSS.
        Tenta gerar via Gemini AI e faz fallback para um gerador semântico de elite.
        """
        if settings.GEMINI_API_KEY:
            try:
                gemini = GeminiAIIntegration()
                system_prompt = (
                    "Você é um engenheiro sênior de UI/UX especializado em Landing Pages de altíssima conversão (CRO) "
                    "do Google Stitch. Gere um documento HTML5 completo, único e autônomo (single-file HTML) "
                    "estritamente de acordo com as especificações a seguir.\n\n"
                    "REGRAS OBRIGATÓRIAS:\n"
                    "1. Use Tailwind CSS via <script src=\"https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js\"></script> ou <script src=\"https://cdn.tailwindcss.com\"></script>.\n"
                    "2. Configure as cores fornecidas no tailwind.config dentro de uma tag <script id=\"tailwind-config\">.\n"
                    "3. Use Google Fonts (Playfair Display e Plus Jakarta Sans) e Material Symbols Outlined.\n"
                    "4. Não use textos placeholder (Lorem Ipsum). Use os dados reais fornecidos (nome, sócios, endereço, dores).\n"
                    "5. Adicione o botão flutuante de WhatsApp fixo no canto inferior direito com animação pulse.\n"
                    "6. Retorne APENAS o código HTML completo começando com <!DOCTYPE html> e terminando com </html>, sem explicações em markdown antes ou depois.\n\n"
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
                    return clean_html
            except Exception as e:
                logger.warning(f"Geração de HTML via Gemini falhou ({e}). Usando gerador de elite local.")

        return cls._build_semantic_landing_page(lead_data, brand_colors, owners, logo_url)

    @classmethod
    def _build_semantic_landing_page(
        cls,
        lead_data: Dict[str, Any],
        brand_colors: Dict[str, Any],
        owners: List[Dict[str, str]],
        logo_url: Optional[str] = None,
    ) -> str:
        """Gerador local resiliente que compõe a Landing Page em HTML/Tailwind."""
        name = lead_data.get("name", "Empresa de Excelência")
        phone = lead_data.get("phone") or "(11) 99999-9999"
        clean_phone = "".join(filter(str.isdigit, phone))
        address = lead_data.get("address") or lead_data.get("city") or "Brasil"
        rating = lead_data.get("google_rating") or 4.9
        reviews_count = lead_data.get("google_reviews_count") or 120

        bg = brand_colors.get("background", "#3E0B15")
        primary = brand_colors.get("primary", "#d4af37")
        secondary = brand_colors.get("secondary", "#551320")
        text_color = brand_colors.get("text", "#ffffff")

        # Sócios cards
        owners_html = ""
        if owners:
            owners_cards = []
            for o in owners:
                owners_cards.append(f"""
                <div class="p-6 rounded-2xl bg-surface-container border border-outline-variant/30 flex flex-col items-center text-center">
                    <div class="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center text-primary text-2xl font-bold mb-4 border border-primary/30">
                        {o.get('name', 'Adv')[0]}
                    </div>
                    <h4 class="text-xl font-bold text-on-surface mb-1">{o.get('name')}</h4>
                    <span class="text-xs uppercase tracking-widest text-primary font-semibold">{o.get('role', 'Sócio')}</span>
                </div>
                """)
            owners_html = f"""
            <section class="py-20 bg-background/50 border-t border-outline-variant/20">
                <div class="max-w-[1240px] mx-auto px-6">
                    <div class="text-center max-w-2xl mx-auto mb-14">
                        <span class="text-primary text-xs uppercase tracking-widest font-bold">Liderança & Governança</span>
                        <h3 class="text-3xl font-bold mt-2 text-on-surface">Sócios Fundadores & Corpo Técnico</h3>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-{min(len(owners), 3)} gap-8">
                        {''.join(owners_cards)}
                    </div>
                </div>
            </section>
            """

        logo_elem = f'<img src="{logo_url}" alt="{name}" class="h-12 w-auto object-contain" />' if logo_url else f'<span class="text-xl font-bold text-primary font-serif tracking-wider">{name}</span>'

        return f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark scroll-smooth">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{name} | Excelência & Confiança</title>
    <link rel="preconnect" href="https://fonts.googleapis.com"/>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
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
                        "outline-variant": "rgba(255,255,255,0.15)"
                    }},
                    fontFamily: {{
                        serif: ['"Playfair Display"', 'serif'],
                        sans: ['"Plus Jakarta Sans"', 'sans-serif']
                    }}
                }}
            }}
        }};
    </script>
</head>
<body class="bg-background text-on-surface font-sans antialiased">
    <!-- TOP NAVIGATION -->
    <header class="sticky top-0 z-50 bg-background/85 backdrop-blur-md border-b border-outline-variant">
        <div class="max-w-[1320px] mx-auto px-6 h-20 flex justify-between items-center">
            <div class="flex items-center gap-3">
                {logo_elem}
            </div>
            <nav class="hidden md:flex items-center gap-8 text-sm font-semibold">
                <a href="#solucoes" class="hover:text-primary transition-colors">Soluções</a>
                <a href="#diferenciais" class="hover:text-primary transition-colors">Diferenciais</a>
                <a href="#depoimentos" class="hover:text-primary transition-colors">Avaliações</a>
                <a href="#contato" class="hover:text-primary transition-colors">Localização</a>
            </nav>
            <div class="flex items-center gap-4">
                <a href="tel:{clean_phone}" class="hidden sm:flex items-center gap-2 text-xs font-semibold px-4 py-2 border border-outline-variant rounded-lg hover:border-primary transition-colors">
                    <span class="material-symbols-outlined text-primary text-base">call</span>
                    {phone}
                </a>
                <a href="https://wa.me/{clean_phone}?text=Olá,%20gostaria%20de%20um%20atendimento%20especializado." target="_blank" class="bg-primary text-background font-bold text-xs uppercase tracking-wider px-5 py-2.5 rounded-lg shadow-lg hover:opacity-90 transition-opacity">
                    Agendar Consulta
                </a>
            </div>
        </div>
    </header>

    <!-- HERO SECTION -->
    <section class="py-20 md:py-28 relative overflow-hidden">
        <div class="max-w-[1320px] mx-auto px-6 relative z-10">
            <div class="max-w-4xl mx-auto text-center flex flex-col items-center">
                <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-container border border-primary/30 mb-6 text-xs text-primary font-bold tracking-wider uppercase">
                    <span class="h-2 w-2 rounded-full bg-primary animate-pulse"></span>
                    Atendimento Jurídico & Consultoria Especializada
                </div>
                <h1 class="text-4xl md:text-6xl font-bold font-serif leading-tight mb-6">
                    Advocacia Estratégica, Segurança e <span class="text-primary italic">Defesa Rigorosa</span> dos Seus Direitos.
                </h1>
                <p class="text-lg md:text-xl text-on-surface/80 max-w-2xl mb-10 leading-relaxed">
                    Compromisso inegociável com a excelência técnica, agilidade e sigilo para defender seus interesses patrimoniais e corporativos.
                </p>
                <div class="flex flex-col sm:flex-row gap-4 w-full justify-center">
                    <a href="https://wa.me/{clean_phone}?text=Olá,%20preciso%20de%20uma%20orientação%20jurídica." target="_blank" class="bg-primary text-background font-bold px-8 py-4 rounded-xl shadow-xl hover:scale-105 transition-transform flex items-center justify-center gap-2 text-sm uppercase tracking-wider">
                        <span class="material-symbols-outlined text-lg">chat</span>
                        Falar com Especialista no WhatsApp
                    </a>
                </div>
                <!-- SOCIAL PROOF BADGE -->
                <div class="mt-12 flex items-center justify-center gap-3 text-xs text-on-surface/70">
                    <div class="flex text-amber-400">
                        ★★★★★
                    </div>
                    <span><strong>{rating} de 5.0 estrelas</strong> no Google ({reviews_count}+ avaliações reais)</span>
                </div>
            </div>
        </div>
    </section>

    {owners_html}

    <!-- FOOTER & WHATSAPP FLOATING -->
    <footer class="py-12 bg-background border-t border-outline-variant text-center text-xs text-on-surface/60">
        <p class="mb-2">© 2026 {name}. Todos os direitos reservados. {address}.</p>
        <p>Desenvolvido com foco em alta performance e conformidade técnica.</p>
    </footer>

    <!-- STICKY WHATSAPP BUTTON -->
    <div class="fixed bottom-6 right-6 z-50">
        <a href="https://wa.me/{clean_phone}?text=Olá,%20vim%20pelo%20site%20e%20gostaria%20de%20atendimento." target="_blank" class="flex items-center gap-2.5 bg-[#25D366] hover:bg-[#20ba59] text-gray-950 font-bold px-4 py-3 rounded-full shadow-2xl transition-transform hover:scale-110">
            <span class="relative flex h-3 w-3">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                <span class="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
            </span>
            <span class="material-symbols-outlined text-2xl">chat</span>
            <span class="text-xs uppercase tracking-wider pr-1">Atendimento Online</span>
        </a>
    </div>
</body>
</html>"""
