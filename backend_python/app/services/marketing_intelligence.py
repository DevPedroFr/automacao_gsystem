"""
Motor de Inteligência de Marketing & CRO (Conversion Rate Optimization).
Responsável por:
  1. Detectar Gafes Críticas de Negócio (Business Blunders).
  2. Estimar Vazamento Financeiro de Leads.
  3. Gerar a Matriz de Transformação da Landing Page.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
#  Catálogo de Gafes Comerciais (Business Blunders)
# ---------------------------------------------------------------------------
BLUNDER_CATALOG = {
    "search_leak": {
        "id": "search_leak",
        "title": "Vazamento de Busca Local",
        "icon": "search_off",
        "severity": "CRITICAL",
        "description": (
            "Quando alguém pesquisa pelo serviço no Google e clica no perfil da empresa, "
            "não encontra um site rápido ou cai em uma página quebrada/lenta. "
            "O visitante volta para a busca e clica no concorrente que tem site pronto."
        ),
        "financial_impact": "Perda estimada de 30-60% dos visitantes do Google que NÃO voltam.",
        "lp_solution": (
            "Landing Page de alta velocidade (< 2s de carregamento) indexada no Google, "
            "com proposta de valor acima da dobra e botão de ação imediata."
        ),
    },
    "contact_friction": {
        "id": "contact_friction",
        "title": "Fricção de Contato & Barreira de WhatsApp",
        "icon": "phone_disabled",
        "severity": "CRITICAL",
        "description": (
            "O único meio de contato é telefone fixo, formulário longo ou WhatsApp sem link direto. "
            "No mobile, o cliente precisa copiar o número, abrir o WhatsApp e digitar — "
            "a maioria desiste no caminho."
        ),
        "financial_impact": "Até 70% dos potenciais clientes no celular desistem antes de completar o contato.",
        "lp_solution": (
            "Botão WhatsApp flutuante com mensagem pré-preenchida contextual (ex: 'Quero um orçamento de...'). "
            "Zero fricção: 1 toque = conversa aberta com a empresa."
        ),
    },
    "invisible_catalog": {
        "id": "invisible_catalog",
        "title": "Catálogo & Serviços Invisíveis",
        "icon": "visibility_off",
        "severity": "HIGH",
        "description": (
            "O visitante não consegue descobrir rapidamente o que a empresa oferece, "
            "quais marcas trabalha, faixas de preço ou condições comerciais. "
            "Ele desiste silenciosamente e compra onde encontra a informação mais rápido."
        ),
        "financial_impact": "Clientes em fase de decisão abandonam em até 8 segundos sem encontrar o que procuram.",
        "lp_solution": (
            "Grade de Soluções com 4-6 cards visuais detalhados, ícones, descrições e botão "
            "'Pedir Cotação' direto por WhatsApp em cada produto/serviço."
        ),
    },
    "hidden_authority": {
        "id": "hidden_authority",
        "title": "Autoridade & Prova Social Desperdiçada",
        "icon": "star_border",
        "severity": "HIGH",
        "description": (
            "A empresa tem dezenas ou centenas de avaliações positivas no Google, "
            "mas essas provas sociais ficam completamente invisíveis no momento "
            "em que o visitante está decidindo fechar negócio."
        ),
        "financial_impact": "Sem prova social visível, a taxa de conversão cai em até 4x comparada a quem exibe avaliações.",
        "lp_solution": (
            "Seção de Prova Social acima da dobra com nota do Google, estrelas douradas, "
            "quantidade de avaliações reais e depoimentos selecionados."
        ),
    },
    "after_hours_abandonment": {
        "id": "after_hours_abandonment",
        "title": "Abandono Noturno & Fins de Semana",
        "icon": "nightlight",
        "severity": "MEDIUM",
        "description": (
            "Fora do horário comercial, a empresa simplesmente não existe para quem pesquisa. "
            "Clientes que procuram à noite ou nos fins de semana não conseguem nem "
            "iniciar um pedido de orçamento."
        ),
        "financial_impact": "35-45% das pesquisas locais acontecem fora do horário comercial.",
        "lp_solution": (
            "Landing Page disponível 24h com formulário de cotação expressa e botão "
            "WhatsApp que funciona mesmo fora do expediente (o cliente deixa a mensagem e é respondido logo cedo)."
        ),
    },
    "mobile_frustration": {
        "id": "mobile_frustration",
        "title": "Lentidão & Frustração no Celular",
        "icon": "smartphone",
        "severity": "CRITICAL",
        "description": (
            "O site atual demora mais de 3 segundos para carregar no 4G. "
            "Estudos mostram que mais de 53% dos visitantes mobile abandonam "
            "uma página que leva mais de 3s para abrir."
        ),
        "financial_impact": "Cada segundo a mais de carregamento reduz conversões em 7%.",
        "lp_solution": (
            "Landing Page ultrarrápida com Tailwind CSS inline, zero dependências pesadas, "
            "PageSpeed 95+ e otimização agressiva para conexões lentas."
        ),
    },
    "no_objection_breakers": {
        "id": "no_objection_breakers",
        "title": "Falta de Quebra de Objeções & Garantias",
        "icon": "gpp_maybe",
        "severity": "MEDIUM",
        "description": (
            "Ausência de selos de garantia, procedência, prazo de entrega, "
            "credenciais dos fundadores ou políticas de devolução. "
            "O visitante fica inseguro e não fecha."
        ),
        "financial_impact": "Visitantes indecisos (40-60% do tráfego) precisam de gatilhos de confiança para converter.",
        "lp_solution": (
            "Badges de confiança (Garantia de Fábrica, Pronta-Entrega, Empresa Verificada), "
            "seção de liderança com nome e foto dos responsáveis, e selos de procedência."
        ),
    },
    "wasted_traffic": {
        "id": "wasted_traffic",
        "title": "Tráfego Pago ou Orgânico Desperdiçado",
        "icon": "money_off",
        "severity": "HIGH",
        "description": (
            "Se a empresa investe em Google Ads, Instagram Ads ou aparece organicamente no Google, "
            "mas direciona para um site lento, sem CTA claro ou sem WhatsApp direto, "
            "está literalmente jogando dinheiro fora."
        ),
        "financial_impact": "Cada R$ 1 investido em tráfego pago sem página otimizada desperdiça até R$ 0,80.",
        "lp_solution": (
            "Página de destino (landing page) dedicada e otimizada para cada fonte de tráfego, "
            "com CTA agressivo, carregamento instantâneo e rastreamento de conversões."
        ),
    },
}

# ---------------------------------------------------------------------------
#  Estimativas de volume de busca mensal por nicho e porte de cidade
# ---------------------------------------------------------------------------
NICHE_SEARCH_ESTIMATES = {
    "construcao":  {"small": (200, 500),   "medium": (500, 1500),  "large": (1500, 5000)},
    "automotivo":  {"small": (150, 400),   "medium": (400, 1200),  "large": (1200, 4000)},
    "odontologia": {"small": (300, 700),   "medium": (700, 2000),  "large": (2000, 6000)},
    "medicina":    {"small": (250, 600),   "medium": (600, 1800),  "large": (1800, 5500)},
    "advocacia":   {"small": (100, 300),   "medium": (300, 900),   "large": (900, 3000)},
    "alimentacao": {"small": (400, 1000),  "medium": (1000, 3000), "large": (3000, 8000)},
    "beleza":      {"small": (300, 800),   "medium": (800, 2500),  "large": (2500, 7000)},
    "geral":       {"small": (150, 400),   "medium": (400, 1200),  "large": (1200, 3500)},
}

# Ticket médio estimado por nicho (R$)
NICHE_AVG_TICKET = {
    "construcao":  (800, 2500),
    "automotivo":  (400, 1500),
    "odontologia": (600, 3000),
    "medicina":    (300, 1200),
    "advocacia":   (1500, 5000),
    "alimentacao": (50, 200),
    "beleza":      (100, 500),
    "geral":       (200, 1000),
}


class MarketingIntelligence:
    """
    Motor de Inteligência de Marketing para Diagnóstico Consultivo 360°.
    """

    @classmethod
    def detect_blunders(
        cls,
        has_website: bool,
        pagespeed_score: Optional[float],
        google_rating: Optional[float],
        google_reviews_count: Optional[int],
        has_instagram: bool,
        has_whatsapp_on_site: bool = False,
        niche_key: str = "geral",
    ) -> List[Dict[str, Any]]:
        """
        Analisa os dados do lead e detecta quais gafes comerciais estão ativas.
        Retorna lista ordenada por severidade.
        """
        detected = []
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

        # 1. Vazamento de Busca Local
        if not has_website:
            b = dict(BLUNDER_CATALOG["search_leak"])
            b["detected_reason"] = "A empresa NÃO possui site próprio. Quem pesquisa no Google não encontra destino digital."
            detected.append(b)
        elif pagespeed_score is not None and pagespeed_score < 50:
            b = dict(BLUNDER_CATALOG["search_leak"])
            b["detected_reason"] = f"O site atual tem PageSpeed de apenas {pagespeed_score}/100. Mais da metade dos visitantes desiste antes de ver a marca."
            detected.append(b)

        # 2. Fricção de Contato
        if not has_website or not has_whatsapp_on_site:
            b = dict(BLUNDER_CATALOG["contact_friction"])
            if not has_website:
                b["detected_reason"] = "Sem site = sem botão de WhatsApp com 1 clique. O cliente precisa copiar o número do Google e abrir o app manualmente."
            else:
                b["detected_reason"] = "O site atual não possui botão de WhatsApp direto com link wa.me e mensagem pré-configurada."
            detected.append(b)

        # 3. Catálogo / Serviços Invisíveis
        if not has_website:
            b = dict(BLUNDER_CATALOG["invisible_catalog"])
            b["detected_reason"] = "Sem site, não há nenhum local onde o visitante possa ver rapidamente os produtos, serviços, marcas e condições comerciais."
            detected.append(b)
        elif pagespeed_score is not None and pagespeed_score < 40:
            b = dict(BLUNDER_CATALOG["invisible_catalog"])
            b["detected_reason"] = "O site é tão lento que o visitante desiste antes de ver o catálogo de produtos e serviços."
            detected.append(b)

        # 4. Autoridade Escondida
        if google_reviews_count and google_reviews_count >= 10:
            if not has_website:
                b = dict(BLUNDER_CATALOG["hidden_authority"])
                b["detected_reason"] = (
                    f"A empresa tem {google_reviews_count} avaliações no Google "
                    f"({'⭐' + str(google_rating) if google_rating else ''}), "
                    f"mas sem site próprio essas provas sociais ficam completamente ocultas no momento da decisão de compra."
                )
                detected.append(b)

        # 5. Abandono Noturno
        if not has_website:
            b = dict(BLUNDER_CATALOG["after_hours_abandonment"])
            b["detected_reason"] = "Sem presença digital 24h, quem pesquisa à noite ou no fim de semana não consegue iniciar um orçamento."
            detected.append(b)

        # 6. Lentidão Mobile
        if pagespeed_score is not None and pagespeed_score < 50:
            b = dict(BLUNDER_CATALOG["mobile_frustration"])
            b["detected_reason"] = f"PageSpeed {pagespeed_score}/100 significa carregamento de 4-8 segundos no celular com 4G. 53% dos visitantes abandonam acima de 3s."
            detected.append(b)

        # 7. Falta de Quebra de Objeções
        if not has_website:
            b = dict(BLUNDER_CATALOG["no_objection_breakers"])
            b["detected_reason"] = "Sem site, não há selos de garantia, credenciais dos sócios, políticas de entrega ou badges de confiança visíveis."
            detected.append(b)

        # 8. Tráfego Desperdiçado
        if has_website and pagespeed_score is not None and pagespeed_score < 40:
            b = dict(BLUNDER_CATALOG["wasted_traffic"])
            b["detected_reason"] = f"Se a empresa investe em anúncios, cada clique está sendo desperdiçado em um site com score {pagespeed_score}/100."
            detected.append(b)

        # Ordenar por severidade
        detected.sort(key=lambda x: severity_order.get(x.get("severity", "MEDIUM"), 2))

        return detected

    @classmethod
    def estimate_revenue_leak(
        cls,
        niche_key: str,
        city: Optional[str] = None,
        google_reviews_count: Optional[int] = None,
        blunders_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Calcula estimativa de vazamento financeiro mensal de oportunidades perdidas.
        """
        # Determinar porte da cidade (heurística simples)
        city_size = "medium"
        if city:
            city_lower = city.lower()
            large_cities = ["são paulo", "sao paulo", "rio de janeiro", "belo horizonte",
                           "salvador", "brasília", "brasilia", "curitiba", "fortaleza",
                           "recife", "porto alegre", "manaus", "belém", "belem",
                           "goiânia", "goiania", "campinas", "guarulhos"]
            small_indicators = ["interior", "vila", "distrito"]
            if any(c in city_lower for c in large_cities):
                city_size = "large"
            elif any(s in city_lower for s in small_indicators) or (google_reviews_count and google_reviews_count < 20):
                city_size = "small"

        # Buscas estimadas para o nicho na região
        search_range = NICHE_SEARCH_ESTIMATES.get(niche_key, NICHE_SEARCH_ESTIMATES["geral"]).get(city_size, (200, 800))
        monthly_searches_low, monthly_searches_high = search_range

        # Taxa de clique no perfil do Google (CTR médio: 15-30%)
        click_rate = 0.20
        visitors_low = int(monthly_searches_low * click_rate)
        visitors_high = int(monthly_searches_high * click_rate)

        # Taxa de perda por gafes (cada gafe amplifica a perda)
        base_loss_rate = 0.40  # 40% já perdem naturalmente sem site otimizado
        blunder_multiplier = min(1.0, base_loss_rate + (blunders_count * 0.08))
        lost_leads_low = int(visitors_low * blunder_multiplier)
        lost_leads_high = int(visitors_high * blunder_multiplier)

        # Ticket médio do nicho
        ticket_range = NICHE_AVG_TICKET.get(niche_key, NICHE_AVG_TICKET["geral"])
        ticket_low, ticket_high = ticket_range

        # Receita estimada perdida (nem todo lead vira venda — taxa de fechamento ~15-25%)
        close_rate = 0.18
        revenue_lost_low = int(lost_leads_low * close_rate * ticket_low)
        revenue_lost_high = int(lost_leads_high * close_rate * ticket_high)

        return {
            "city_size": city_size,
            "monthly_searches": {"low": monthly_searches_low, "high": monthly_searches_high},
            "estimated_visitors": {"low": visitors_low, "high": visitors_high},
            "lost_leads_per_month": {"low": lost_leads_low, "high": lost_leads_high},
            "estimated_revenue_lost": {"low": revenue_lost_low, "high": revenue_lost_high},
            "avg_ticket_range": {"low": ticket_low, "high": ticket_high},
            "blunders_detected": blunders_count,
            "loss_severity": "CRÍTICO" if blunders_count >= 4 else ("ALTO" if blunders_count >= 2 else "MODERADO"),
            "summary": (
                f"Estimamos que {lost_leads_low} a {lost_leads_high} potenciais clientes da região "
                f"tentam contatar a empresa mensalmente e desistem pelas {blunders_count} falhas identificadas, "
                f"representando R$ {revenue_lost_low:,.0f} a R$ {revenue_lost_high:,.0f} em orçamentos deixados na mesa."
            ),
        }

    @classmethod
    def build_transformation_matrix(
        cls,
        detected_blunders: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """
        Gera a Matriz de Transformação da Landing Page:
        Para cada gafe → qual o impacto → como a LP resolve → ganho esperado.
        """
        matrix = []
        for blunder in detected_blunders:
            matrix.append({
                "problem": blunder["title"],
                "detected_detail": blunder.get("detected_reason", blunder["description"]),
                "financial_impact": blunder["financial_impact"],
                "lp_solution": blunder["lp_solution"],
                "expected_gain": _expected_gain_for(blunder["id"]),
            })
        return matrix


def _expected_gain_for(blunder_id: str) -> str:
    """Retorna o ganho esperado ao resolver a gafe com a LP."""
    gains = {
        "search_leak": "Capturar visitantes do Google que hoje vão para concorrentes. Aumento de 3-5x nos contatos recebidos.",
        "contact_friction": "Multiplicar contatos pelo WhatsApp com 1 toque. Estudos mostram aumento de até 200% na taxa de contato.",
        "invisible_catalog": "Reduzir abandono silencioso. Visitantes que veem os produtos e serviços ficam 4x mais tempo na página.",
        "hidden_authority": "Aumentar confiança instantânea. Exibir avaliações reais do Google aumenta conversão em até 270%.",
        "after_hours_abandonment": "Capturar 35-45% de clientes que pesquisam fora do horário comercial e que hoje não conseguem contato.",
        "mobile_frustration": "Eliminar abandono por lentidão. Site rápido (< 2s) retém até 53% mais visitantes mobile.",
        "no_objection_breakers": "Quebrar objeções de confiança e garantia que impedem 40-60% dos visitantes indecisos de fechar.",
        "wasted_traffic": "Cada R$ 1 investido em tráfego pago passa a gerar até 5x mais retorno com página de destino otimizada.",
    }
    return gains.get(blunder_id, "Melhoria significativa na captação de novos clientes e conversão de visitantes em contatos.")
