import json
import logging
import re
from typing import Optional

import httpx

from app.core.config import settings
from app.core.interfaces.llm_service import LLMService
from app.models.diagnosis import (
    DiagnosisResult, DiagnosticFact, DiagnosticInference,
    RecommendationItem, SalesRecommendation, StitchPromptResult,
    CriticalBlunder, TransformationItem, RevenueLeak
)
from app.models.triage import FullTriageReport

logger = logging.getLogger(__name__)


class GeminiAIIntegration(LLMService):
    """Agente de IA para geração de diagnóstico rico, estratégias comerciais e prompts para Google Stitch via Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def _build_local_diagnosis(self, report: FullTriageReport) -> DiagnosisResult:
        """Diagnóstico heurístico rico caso a API Gemini não responda.
        Utiliza o MarketingIntelligence para detecção de gafes, vazamento e matriz."""
        lead = report.lead
        ps = report.pagespeed
        sec = report.security
        ig = report.instagram

        from app.services.marketing_intelligence import MarketingIntelligence
        from app.services.lp_prompt_engine import LPPromptEngine

        niche_key = LPPromptEngine.detect_niche(lead.name, "")
        has_website = bool(lead.website_uri)
        pagespeed_score = ps.performance_score if ps else None

        needs_new_site = bool(
            lead.website_uri is None
            or (ps and ps.performance_score is not None and ps.performance_score < 50)
            or (sec and not sec.ssl_valid)
        )

        facts = []
        inferences = []
        recommendations = []

        # Pilar Google
        if lead.rating:
            facts.append(DiagnosticFact(pilar="google", text=f"{lead.name} possui {lead.rating}/5.0 no Google Maps com {lead.user_rating_count or 0} avaliações verificadas."))
            if lead.rating >= 4.5:
                inferences.append(DiagnosticInference(pilar="google", text=f"Excelente reputação ({lead.rating} estrelas). Esta nota é um ativo comercial valioso: clientes que veem 4.5+ estrelas convertem 270% mais. Porém, sem site profissional, esta autoridade fica escondida no momento da decisão de compra."))
            elif lead.rating >= 4.0:
                inferences.append(DiagnosticInference(pilar="google", text=f"Boa reputação ({lead.rating} estrelas), mas há espaço para melhorar. Cada 0.1 estrela a mais representa até 9% mais cliques. Uma LP exibindo estas avaliações amplifica o efeito de confiança."))
            else:
                inferences.append(DiagnosticInference(pilar="google", text=f"Nota {lead.rating} estrelas está abaixo da média competitiva do setor. Priorizar a gestão de reputação e exibir os melhores depoimentos na LP."))
        if lead.national_phone_number:
            facts.append(DiagnosticFact(pilar="google", text=f"Telefone comercial cadastrado: {lead.national_phone_number}. Funciona como ponto de contato, mas não é o canal preferido do consumidor mobile (WhatsApp é 3x mais usado)."))
        if lead.formatted_address:
            facts.append(DiagnosticFact(pilar="google", text=f"Endereço verificado no Google: {lead.formatted_address}. Perfil localizado na busca regional."))

        # Pilar Website
        if not lead.website_uri:
            facts.append(DiagnosticFact(pilar="website", text=f"{lead.name} NÃO possui site próprio cadastrado no Google Empresa. Quando um cliente pesquisa e clica, não há para onde ir."))
            inferences.append(DiagnosticInference(pilar="website", text=f"A ausência de site é o problema #1: {lead.name} está completamente invisível para quem pesquisa no Google fora do horário comercial. Concorrentes com site captam esses clientes automaticamente 24h."))
            recommendations.append(RecommendationItem(
                category="Presença Digital", severity="HIGH",
                finding=f"{lead.name} não possui nenhum site ou landing page, perdendo 100% do tráfego digital.",
                action_item="Criar landing page de alta conversão com botão WhatsApp em 1 toque, catálogo de serviços e prova social com avaliações do Google.",
            ))
        elif ps:
            score = ps.performance_score
            facts.append(DiagnosticFact(pilar="website", text=f"Site existente: {lead.website_uri}. PageSpeed: {score or 'N/A'}/100. SEO: {ps.seo_score or 'N/A'}/100."))
            if score and score < 50:
                inferences.append(DiagnosticInference(pilar="website", text=f"PageSpeed de {score}/100 significa carregamento de 4-8 segundos no celular. 53% dos visitantes mobile abandonam acima de 3s. {lead.name} está queimando vendas pela lentidão."))
                recommendations.append(RecommendationItem(
                    category="Performance & CRO", severity="HIGH",
                    finding=f"Site com score {score}/100 afugenta mais da metade dos visitantes antes da página carregar.",
                    action_item="Substituir por landing page ultrarrápida (PageSpeed 95+) com Tailwind CSS inline e zero dependências pesadas.",
                ))
            else:
                inferences.append(DiagnosticInference(pilar="website", text=f"Performance {score}/100 é aceitável, mas há espaço significativo para otimizar a conversão mobile e a velocidade de carregamento."))

        # Pilar Social
        if ig and (ig.found or ig.is_business_account):
            facts.append(DiagnosticFact(pilar="social", text=f"Instagram ativo: @{ig.handle}. {'Conta comercial configurada.' if ig.is_business_account else 'Conta pessoal (não comercial).'}"))
            inferences.append(DiagnosticInference(pilar="social", text="Presença social ativa é positiva, mas Instagram sozinho não converte vendas complexas. Conectar o perfil a uma LP com WhatsApp cria um funil completo: descoberta → interesse → contato → venda."))
        else:
            facts.append(DiagnosticFact(pilar="social", text=f"Nenhum perfil oficial de Instagram identificado para {lead.name}."))
            inferences.append(DiagnosticInference(pilar="social", text="Sem rede social ativa, o negócio depende 100% do boca a boca e Google Maps. Uma LP com galeria visual e link para redes funciona como vitrine digital permanente."))

        # Pilar Marketing
        facts.append(DiagnosticFact(pilar="marketing", text=f"Nicho identificado: {niche_key}. A análise considera padrões de busca e comportamento do consumidor específicos deste setor na região."))
        inferences.append(DiagnosticInference(pilar="marketing", text=f"O principal gargalo de {lead.name} é a desconexão entre a qualidade do serviço (comprovada pelas avaliações) e a capacidade de captar novos clientes digitalmente. Uma LP resolve esse gargalo em dias, não meses."))

        recommendations.append(RecommendationItem(
            category="Conversão & CRO", severity="HIGH",
            finding="Ausência de botão WhatsApp com 1 toque na presença digital.",
            action_item=f"Implementar botão WhatsApp flutuante com mensagem pré-preenchida contextual para o nicho de {niche_key}.",
        ))
        recommendations.append(RecommendationItem(
            category="Prova Social", severity="MEDIUM",
            finding=f"Avaliações do Google ({lead.user_rating_count or 0}) não são exibidas no momento da decisão de compra.",
            action_item="Incluir seção de prova social na LP com nota, estrelas e depoimentos reais do Google.",
        ))
        recommendations.append(RecommendationItem(
            category="Funil de Vendas", severity="HIGH",
            finding="Sem captação automatizada fora do horário comercial (35-45% das buscas são à noite/fim de semana).",
            action_item="LP com formulário de cotação expressa e WhatsApp 24h para capturar leads noturnos.",
        ))
        recommendations.append(RecommendationItem(
            category="Competitividade Local", severity="MEDIUM",
            finding=f"Concorrentes digitais na região de {lead.formatted_address or 'sua cidade'} já captam clientes que deveriam ser de {lead.name}.",
            action_item="LP indexada no Google com SEO local para competir nas buscas regionais do setor.",
        ))

        # Motor de Inteligência de Marketing
        detected_blunders = MarketingIntelligence.detect_blunders(
            has_website=has_website,
            pagespeed_score=pagespeed_score,
            google_rating=lead.rating,
            google_reviews_count=lead.user_rating_count,
            has_instagram=bool(ig and ig.found),
            has_whatsapp_on_site=False,
            niche_key=niche_key,
        )

        revenue_leak_data = MarketingIntelligence.estimate_revenue_leak(
            niche_key=niche_key,
            city=lead.formatted_address,
            google_reviews_count=lead.user_rating_count,
            blunders_count=len(detected_blunders),
        )

        transformation_matrix = MarketingIntelligence.build_transformation_matrix(detected_blunders)

        pydantic_blunders = []
        for b in detected_blunders:
            pydantic_blunders.append(CriticalBlunder(
                id=b["id"], title=b["title"], icon=b["icon"],
                severity=b["severity"], description=b["description"],
                detected_reason=b.get("detected_reason", b["description"]),
                financial_impact=b["financial_impact"], lp_solution=b["lp_solution"],
            ))

        pydantic_matrix = [TransformationItem(**t) for t in transformation_matrix]
        pydantic_revenue = RevenueLeak(**revenue_leak_data)

        # Estratégia de Venda Consultiva
        ps_str = f"com PageSpeed {ps.performance_score}/100" if ps and ps.performance_score else "sem site próprio"
        blunders_count = len(detected_blunders)
        approach = (
            f"Abordagem consultiva: '{lead.name}' possui {lead.rating or 4.5} estrelas no Google, "
            f"mas detectamos {blunders_count} falhas críticas na presença digital que estão custando "
            f"entre R$ {revenue_leak_data['estimated_revenue_lost']['low']:,.0f} e "
            f"R$ {revenue_leak_data['estimated_revenue_lost']['high']:,.0f} em oportunidades perdidas por mês."
        )

        sales_rec = SalesRecommendation(
            approach_angle=approach,
            pain_points=[
                f"{lead.name} está {ps_str}, perdendo clientes para concorrentes com presença digital profissional",
                f"Detectamos {blunders_count} gafes comerciais ativas que desviam clientes todos os dias",
                f"35-45% das pesquisas na região acontecem fora do horário comercial — sem site, {lead.name} é invisível nessas horas",
                f"O vazamento financeiro estimado é de até R$ {revenue_leak_data['estimated_revenue_lost']['high']:,.0f}/mês em orçamentos não realizados",
            ],
            talking_points=[
                f"Com {lead.rating or 4.5} estrelas e {lead.user_rating_count or 0} avaliações, {lead.name} já tem a credibilidade — só falta o canal digital para converter",
                "Uma landing page de alta conversão se paga com 1-2 novos clientes captados pelo WhatsApp no primeiro mês",
                "O site é feito sob medida para o nicho, usando dados reais da auditoria, não um template genérico",
                "Botão WhatsApp com 1 toque + catálogo visual + prova social = funil completo de vendas automatizado 24h",
            ],
            value_proposition=f"Transformar a excelente reputação de {lead.name} em um motor digital de captação de novos clientes, eliminando {blunders_count} falhas que custam até R$ {revenue_leak_data['estimated_revenue_lost']['high']:,.0f}/mês.",
        )

        whatsapp_draft = (
            f"Olá, tudo bem? Aqui é da equipe de Consultoria Digital! 👋\n\n"
            f"Estive analisando a presença online da {lead.name} em {lead.formatted_address or 'sua cidade'} "
            f"e encontrei {blunders_count} pontos que estão custando clientes todo dia.\n\n"
            f"Vocês já têm uma reputação excelente no Google ({lead.rating or 4.9} estrelas, "
            f"{lead.user_rating_count or 0} avaliações!), mas sem "
            f"{'um site profissional' if not lead.website_uri else 'um site rápido e otimizado'}, "
            f"essa autoridade fica invisível na hora da decisão de compra.\n\n"
            f"Preparei um diagnóstico gratuito com as {blunders_count} falhas e como resolver cada uma. "
            f"Posso te enviar por aqui? 🚀"
        )

        email_draft = (
            f"Assunto: {lead.name} - {blunders_count} oportunidades de captação digital identificadas\n\n"
            f"Olá equipe da {lead.name},\n\n"
            f"Realizamos uma auditoria técnica completa da presença digital da {lead.name} e identificamos:\n\n"
            f"- Reputação: {lead.rating or 4.5} estrelas com {lead.user_rating_count or 0} avaliações (excelente!)\n"
            f"- Gafes detectadas: {blunders_count} falhas críticas que desviam clientes para concorrentes\n"
            f"- Vazamento estimado: até R$ {revenue_leak_data['estimated_revenue_lost']['high']:,.0f}/mês em orçamentos perdidos\n\n"
            f"A boa notícia: todas essas falhas podem ser resolvidas com uma Landing Page profissional "
            f"feita sob medida para o setor de {niche_key}, com botão WhatsApp, catálogo visual e prova social.\n\n"
            f"Podemos agendar 10 minutos para mostrar o diagnóstico completo?\n\n"
            f"Atenciosamente,\nConsultoria de Presença Digital"
        )

        instagram_draft = (
            f"Oi, tudo bem? 👋 Estava conferindo o perfil da {lead.name} e fiquei impressionado com a qualidade! "
            f"Notei {blunders_count} pontos na presença digital que podem estar custando clientes. "
            f"Preparei um diagnóstico rápido e gratuito — posso te enviar por aqui?"
        )

        niche_insight = (
            f"No setor de {niche_key}, os consumidores pesquisam ativamente no Google antes de decidir. "
            f"Empresas com landing page otimizada e botão WhatsApp captam em média 3-5x mais contatos "
            f"que aquelas que dependem apenas do Google Maps. A combinação de prova social "
            f"({lead.rating or 4.5} estrelas) com página de alta conversão é o diferencial competitivo "
            f"mais eficaz para {lead.name} na região."
        )

        return DiagnosisResult(
            lead_name=lead.name,
            overall_summary=(
                f"Auditoria consultiva 360° para {lead.name}. "
                f"{'Não possui site próprio — prioridade máxima.' if not lead.website_uri else f'Site com PageSpeed {pagespeed_score or 0}/100.'} "
                f"Detectamos {blunders_count} gafes comerciais críticas. "
                f"Vazamento financeiro estimado: até R$ {revenue_leak_data['estimated_revenue_lost']['high']:,.0f}/mês."
            ),
            recommendations=recommendations,
            needs_new_website=needs_new_site,
            whatsapp_draft=whatsapp_draft,
            email_draft=email_draft,
            instagram_draft=instagram_draft,
            facts=facts,
            inferences=inferences,
            sales_recommendation=sales_rec,
            critical_blunders=pydantic_blunders if pydantic_blunders else None,
            transformation_matrix=pydantic_matrix if pydantic_matrix else None,
            revenue_leak=pydantic_revenue,
            niche_insights=niche_insight,
        )

    async def generate_text(self, prompt: str, max_tokens: int = 8000) -> str:
        """Gera texto livre / HTML sem imposição de schema JSON estruturado."""
        if not self.api_key:
            raise RuntimeError("Gemini API key not configured")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": max_tokens,
            },
        }
        logger.info(f"Gerando texto livre via Gemini ({self.model})...")
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return text or ""

    async def _call_gemini(self, prompt: str, max_tokens: int = 3500) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini API key not configured")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        schema = {
            "type": "OBJECT",
            "properties": {
                "overall_summary": {"type": "STRING"},
                "needs_new_website": {"type": "BOOLEAN"},
                "facts": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "pilar": {"type": "STRING"},
                            "text": {"type": "STRING"}
                        }
                    }
                },
                "inferences": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "pilar": {"type": "STRING"},
                            "text": {"type": "STRING"}
                        }
                    }
                },
                "recommendations": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "category": {"type": "STRING"},
                            "severity": {"type": "STRING"},
                            "finding": {"type": "STRING"},
                            "action_item": {"type": "STRING"}
                        }
                    }
                },
                "sales_recommendation": {
                    "type": "OBJECT",
                    "properties": {
                        "approach_angle": {"type": "STRING"},
                        "pain_points": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "talking_points": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "value_proposition": {"type": "STRING"}
                    }
                },
                "whatsapp_draft": {"type": "STRING"},
                "email_draft": {"type": "STRING"},
                "instagram_draft": {"type": "STRING"}
            },
            "required": ["overall_summary", "needs_new_website", "facts", "inferences", "recommendations", "sales_recommendation", "whatsapp_draft", "email_draft", "instagram_draft"]
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": max_tokens,
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        }

        logger.info(f"Chamando Gemini ({self.model})...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return text or ""

    def _extract_json(self, text: str) -> dict:
        """Extrai e sanitiza JSON retornado pelo Gemini."""
        print("GEMINI OUTPUT:\n", text)
        text = text.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        clean = match.group(0) if match else text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)

    async def generate_diagnosis(self, report: FullTriageReport) -> DiagnosisResult:
        lead = report.lead
        ps = report.pagespeed
        sec = report.security
        ig = report.instagram

        # Importações do motor de inteligência
        from app.services.marketing_intelligence import MarketingIntelligence
        from app.services.lp_prompt_engine import LPPromptEngine

        niche_key = LPPromptEngine.detect_niche(lead.name, "")
        has_website = bool(lead.website_uri)
        pagespeed_score = ps.performance_score if ps else None

        # 1. Detectar Gafes Comerciais via Motor de Marketing
        detected_blunders = MarketingIntelligence.detect_blunders(
            has_website=has_website,
            pagespeed_score=pagespeed_score,
            google_rating=lead.rating,
            google_reviews_count=lead.user_rating_count,
            has_instagram=bool(ig and ig.found),
            has_whatsapp_on_site=False,
            niche_key=niche_key,
        )

        # 2. Estimar Vazamento Financeiro
        revenue_leak_data = MarketingIntelligence.estimate_revenue_leak(
            niche_key=niche_key,
            city=lead.formatted_address,
            google_reviews_count=lead.user_rating_count,
            blunders_count=len(detected_blunders),
        )

        # 3. Gerar Matriz de Transformação
        transformation_matrix = MarketingIntelligence.build_transformation_matrix(detected_blunders)

        # 4. Formatar contexto completo de gafes para o prompt da IA
        blunders_context = ""
        if detected_blunders:
            blunders_lines = []
            for b in detected_blunders:
                blunders_lines.append(
                    f"  - [{b['severity']}] {b['title']}: {b.get('detected_reason', b['description'])}"
                )
            blunders_context = "\n".join(blunders_lines)

        data_context = f"""
DADOS REAIS DO LEAD (AUDITORIA TÉCNICA COMPLETA):
- Nome do Negócio: {lead.name}
- Endereço / Cidade: {lead.formatted_address or 'Não informado'}
- Telefone: {lead.national_phone_number or 'Ausente'}
- Website atual: {lead.website_uri or 'NENHUM (SEM SITE PRÓPRIO)'}
- Avaliação Google Maps: {lead.rating or 'N/A'}/5.0 ({lead.user_rating_count or 0} avaliações)
- PageSpeed Score: {pagespeed_score if pagespeed_score else 'N/A'}/100
- SEO Score: {ps.seo_score if ps else 'N/A'}/100
- SSL Válido: {'Sim' if sec and sec.ssl_valid else 'Não ou Sem site'}
- Instagram: {'@' + ig.handle + (' (conta comercial)' if ig.is_business_account else '') if ig and ig.found else 'Não encontrado'}
- Nicho Detectado: {niche_key}

GAFES COMERCIAIS DETECTADAS PELA AUDITORIA AUTOMATIZADA ({len(detected_blunders)} gafes):
{blunders_context or '  Nenhuma gafe crítica detectada.'}

VAZAMENTO FINANCEIRO ESTIMADO:
  - {revenue_leak_data['summary']}
"""

        prompt = f"""Você é um CONSULTOR SÊNIOR de Marketing Digital, CRO (Conversion Rate Optimization) e Vendas B2B com mais de 15 anos de experiência fechando contratos de presença digital no Brasil.

Sua missão é analisar os dados abaixo e produzir um DIAGNÓSTICO CONSULTIVO DE ELITE — não um resumo genérico, mas uma análise profunda, persuasiva e irrefutável que convença o dono da empresa a investir em uma Landing Page profissional.

{data_context}

Você deve agir como um consultor que:
1. IDENTIFICA gafes e erros graves que o negócio comete na presença digital (com linguagem de impacto comercial).
2. TRADUZ cada falha técnica em PERDA REAL DE CLIENTES E DINHEIRO com números e percentuais.
3. MOSTRA como uma Landing Page de alto desempenho resolve cada problema específico.
4. CRIA scripts de abordagem irrefutáveis para WhatsApp, e-mail e Instagram usando dados reais do negócio.
5. É ESPECÍFICO ao ramo de "{niche_key}" — nunca use termos de outro segmento.

Retorne estritamente um JSON com a seguinte estrutura:
{{
  "overall_summary": "Resumo executivo IMPACTANTE de 4-5 frases: status digital atual, principais gafes encontradas, potencial de receita perdida e a oportunidade central. Use dados reais do lead.",
  "needs_new_website": true,
  "facts": [
    {{"pilar": "google", "text": "Fato verificado detalhado sobre a presença no Google, com análise de como a nota e quantidade de avaliações se comparam ao padrão do setor"}},
    {{"pilar": "google", "text": "Fato sobre como os clientes encontram (ou não) este negócio quando pesquisam por {niche_key} na região"}},
    {{"pilar": "website", "text": "Fato verificado sobre existência, velocidade, responsividade e usabilidade do site. Se não tem site, analisar o impacto de estar invisível"}},
    {{"pilar": "website", "text": "Fato sobre a experiência do visitante: se consegue ver serviços, preços, entrar em contato em 1 clique, se carrega no 4G"}},
    {{"pilar": "social", "text": "Fato verificado sobre presença no Instagram: se é ativa, se tem bio comercial, link na bio, frequência de posts"}},
    {{"pilar": "social", "text": "Análise se a rede social atual funciona como funil de vendas ou é apenas vitrine sem conversão"}},
    {{"pilar": "marketing", "text": "Análise de posicionamento: o que diferencia este negócio dos concorrentes e se isso está visível digitalmente"}},
    {{"pilar": "marketing", "text": "Análise de funil: quais etapas da jornada do cliente estão quebrando (descoberta → interesse → contato → fechamento)"}}
  ],
  "inferences": [
    {{"pilar": "google", "text": "Análise PROFUNDA de como a reputação no Google impacta financeiramente: quantos clientes decidem baseado nas estrelas e como isso pode ser alavancado"}},
    {{"pilar": "website", "text": "Análise de IMPACTO COMERCIAL direto da presença (ou ausência) de site: quantos clientes a empresa está perdendo por dia/mês para concorrentes com site rápido"}},
    {{"pilar": "social", "text": "Análise de impacto da presença social no ciclo de decisão de compra e prova visual da marca"}},
    {{"pilar": "marketing", "text": "A GRANDE OPORTUNIDADE central: como uma Landing Page de alto desempenho resolve o principal gargalo e destrava crescimento"}},
    {{"pilar": "marketing", "text": "Projeção de resultado: o que muda concretamente nos próximos 3 meses com presença digital profissional"}}
  ],
  "recommendations": [
    {{"category": "Presença Digital", "severity": "HIGH", "finding": "Problema ESPECÍFICO e grave identificado", "action_item": "Ação concreta e detalhada para resolver"}},
    {{"category": "Conversão & CRO", "severity": "HIGH", "finding": "Gafe de conversão que está custando vendas reais", "action_item": "Solução prática com resultado esperado"}},
    {{"category": "Marketing & Posicionamento", "severity": "MEDIUM", "finding": "Oportunidade de posicionamento mal aproveitada", "action_item": "Como se destacar dos concorrentes na região"}},
    {{"category": "Funil de Vendas", "severity": "HIGH", "finding": "Etapa do funil onde o cliente abandona", "action_item": "Como a LP fecha esse buraco no funil"}},
    {{"category": "Competitividade Local", "severity": "MEDIUM", "finding": "Análise de como concorrentes digitais captam clientes que deveriam ser dele", "action_item": "Estratégia de captação direta"}}
  ],
  "sales_recommendation": {{
    "approach_angle": "Gancho IRREFUTÁVEL de entrada, citando dados REAIS e específicos do lead: nota do Google, quantidade de reviews, existência (ou não) de site, e impacto financeiro estimado",
    "pain_points": [
      "Dor 1: problema ESPECÍFICO deste negócio com impacto financeiro concreto",
      "Dor 2: o que os clientes dele estão fazendo quando não encontram atendimento digital rápido",
      "Dor 3: como os concorrentes da mesma rua/bairro estão capturando os clientes dele",
      "Dor 4: o custo silencioso de estar invisível fora do horário comercial"
    ],
    "talking_points": [
      "Argumento 1: usar a nota do Google como prova de que o negócio é bom, mas a presença digital não acompanha a qualidade",
      "Argumento 2: dado concreto de quanto tráfego a região gera para esse nicho e quanto está sendo desperdiçado",
      "Argumento 3: mostrar que a LP se paga com 1-2 clientes novos capturados pelo WhatsApp em 1 clique",
      "Argumento 4: diferencial da LP versus sites genéricos — feita sob medida para o nicho e com dados dele"
    ],
    "value_proposition": "Proposta de valor IRRESISTÍVEL em uma frase que conecta a qualidade já comprovada do negócio com a captura digital de novos clientes"
  }},
  "niche_insights": "Insight ESTRATÉGICO profundo e específico do segmento {niche_key}: tendências de busca, comportamento do consumidor local, o que os melhores competidores fazem e como se diferenciar com presença digital",
  "whatsapp_draft": "Mensagem de WhatsApp COMPLETA e persuasiva (5-7 linhas) usando emojis estratégicos, citando DADOS REAIS do lead (nome, nota Google, número de avaliações, existência ou não de site), gerando CURIOSIDADE e terminando com CTA de baixo atrito. NÃO ser genérico.",
  "email_draft": "Email profissional e consultivo com 'Assunto:' chamativo. Corpo com: 1) Elogio genuíno ao negócio com dados, 2) Identificação de 2-3 gafes concretas com impacto financeiro, 3) Proposta de solução concreta (Landing Page sob medida), 4) CTA para conversa de 10 min",
  "instagram_draft": "Direct do Instagram criativo, pessoal e estratégico: elogio genuíno + curiosidade sobre um 'ponto que pode estar custando clientes' + CTA suave"
}}

REGRAS OBRIGATÓRIAS:
1. Todos os textos DEVEM conter o NOME REAL da empresa "{lead.name}" e dados verificados (nota, reviews, cidade, etc.)
2. NUNCA use textos genéricos como "sua empresa" ou "seu negócio" — sempre cite o nome "{lead.name}".
3. Os fatos devem ter no MÍNIMO 8 itens distribuídos entre os pilares (google, website, social, marketing).
4. As inferências devem ter no MÍNIMO 5 itens com análise de IMPACTO COMERCIAL, não técnico.
5. As recomendações devem ter no MÍNIMO 5 itens com ações CONCRETAS e específicas.
6. O tom é de um consultor sênior que quer FECHAR O CONTRATO, não de um relatório acadêmico.
7. Responda em português do Brasil. Tudo deve ser contextualizado ao ramo "{niche_key}".
"""

        try:
            response_text = await self._call_gemini(prompt, max_tokens=4500)
            data = self._extract_json(response_text)
            logger.info(f"Diagnóstico consultivo 360° gerado com sucesso via Gemini para {lead.name}")
        except Exception as e:
            logger.error(f"Falha na geração via Gemini ({e}). Usando fallback heurístico rico.")
            return self._build_local_diagnosis(report)

        facts = [DiagnosticFact(**f) for f in data.get("facts", [])]
        inferences = [DiagnosticInference(**i) for i in data.get("inferences", [])]
        recs = [RecommendationItem(**r) for r in data.get("recommendations", [])]

        sales_data = data.get("sales_recommendation")
        sales_rec = SalesRecommendation(**sales_data) if sales_data else None

        # Converter gafes detectadas para modelos Pydantic
        pydantic_blunders = []
        for b in detected_blunders:
            pydantic_blunders.append(CriticalBlunder(
                id=b["id"], title=b["title"], icon=b["icon"],
                severity=b["severity"], description=b["description"],
                detected_reason=b.get("detected_reason", b["description"]),
                financial_impact=b["financial_impact"], lp_solution=b["lp_solution"],
            ))

        pydantic_matrix = []
        for t in transformation_matrix:
            pydantic_matrix.append(TransformationItem(**t))

        pydantic_revenue = RevenueLeak(**revenue_leak_data)

        return DiagnosisResult(
            lead_name=lead.name,
            overall_summary=data.get("overall_summary", f"Auditoria de presença digital para {lead.name}."),
            recommendations=recs,
            needs_new_website=data.get("needs_new_website", True),
            whatsapp_draft=data.get("whatsapp_draft"),
            email_draft=data.get("email_draft"),
            instagram_draft=data.get("instagram_draft"),
            facts=facts if facts else None,
            inferences=inferences if inferences else None,
            sales_recommendation=sales_rec,
            critical_blunders=pydantic_blunders if pydantic_blunders else None,
            transformation_matrix=pydantic_matrix if pydantic_matrix else None,
            revenue_leak=pydantic_revenue,
            niche_insights=data.get("niche_insights"),
        )

    def _detect_segment(self, name: str, category: Optional[str] = None, address: Optional[str] = None) -> str:
        from app.services.niche_profiles import detect_niche_profile
        profile = detect_niche_profile(name, category, address)
        return f"{profile['niche_pt']} ({profile['industry_en']}) — Foco em {profile['target_audience']}"

    async def generate_stitch_prompt(
        self, report: FullTriageReport, diagnosis: DiagnosisResult
    ) -> StitchPromptResult:
        from app.services.niche_profiles import (
            detect_niche_profile,
            build_impeccable_site_prompt,
            build_brand_identity_summary,
        )

        lead = report.lead
        category = getattr(lead, "category", None)
        profile = detect_niche_profile(lead.name, category, lead.formatted_address)

        rating_info = (
            f"Nota {lead.rating}/5.0 baseada em {lead.user_rating_count or 0} avaliações reais verificadas no Google Maps"
            if lead.rating
            else "Negócio com reputação local em consolidação"
        )

        sales = diagnosis.sales_recommendation
        val_prop = sales.value_proposition if sales and sales.value_proposition else profile["sample_headline"]
        pain_points_txt = ", ".join(sales.pain_points) if sales and sales.pain_points else ", ".join(profile["pain_points"])
        talking_points_txt = ", ".join(sales.talking_points) if sales and sales.talking_points else ", ".join(profile["value_triggers"])

        photos = getattr(lead, "image_urls", None) or []
        hero_photo = getattr(lead, "image_url", None) or (photos[0] if photos else None)
        photos_info = (
            f"Foto Principal Hero: '{hero_photo}' | Galeria Pública do Google Places: {photos[:4]}"
            if (hero_photo or photos)
            else "Nenhuma foto pública anexada (usar direção de arte fotográfica do nicho)"
        )

        prompt = f"""Você é o Arquiteto Líder de UI/UX e Especialista Sênior em Otimização de Conversão (CRO) da Google e Stitch AI.
Sua missão é gerar uma ESPECIFICAÇÃO DE PROMPT COMPLETA, CIRÚRGICA E ULTRA-DETALHADA em INGLÊS para gerar a Landing Page definitiva do negócio abaixo.
O prompt NÃO pode ser genérico. Ele deve conter os dados reais, o tom de voz do nicho, cores com códigos HEX exatos, títulos chamativos (copywriting de resposta direta), dores específicas dos clientes e componentes de alta conversão.

[DADOS REAIS DA EMPRESA]:
- Nome Oficial da Marca: {lead.name}
- Nicho / Segmento Específico: {profile['niche_pt']} ({profile['industry_en']})
- Público-Alvo: {profile['target_audience']}
- Localização: {lead.formatted_address or lead.city or 'Brasil'}
- WhatsApp / Contato Direto: {lead.national_phone_number or 'Disponível no botão'}
- Reputação Google Maps: {rating_info}
- Fotos Públicas Reais do Google Places: {photos_info}
- Proposta de Valor Central: {val_prop}
- Dores Reais do Consumidor deste Nicho: {pain_points_txt}
- Diferenciais e Argumentos de Venda: {talking_points_txt}
- Diagnóstico Técnico Atual: {diagnosis.overall_summary}
- Paleta Cromática Sugerida: {profile['color_palette']}
- Tipografia Recomendada: {profile['typography']}

[ESTRUTURA OBRIGATÓRIA QUE O SEU STITCH_PROMPT DEVE CONTER EM INGLÊS]:
O campo "stitch_prompt" deve ser um documento técnico de alto padrão formatado com Markdown contendo minuciosamente:
1. PROJECT SPECIFICATION & ART DIRECTION: Identidade de marca ({lead.name}), atmosfera visual, paleta cromática completa com códigos HEX ({profile['color_palette']['primary']}, {profile['color_palette']['secondary']}, {profile['color_palette']['accent']}), tipografia ({profile['typography']['headings']} e {profile['typography']['body']}) e layout espaçoso sem poluição visual.
2. HERO SECTION & REAL IMAGERY: Headline irresistível com promessa concreta sem clichês, subheadline resolvendo a maior dor do cliente, botão primário CTA com micro-copy persuasivo apontando para WhatsApp, e 3 Badges de Autoridade (estrelas reais do Google Maps, atendimento rápido, localização). SE HOUVER FOTOS REAIS DO GOOGLE, instruir explicitamente o uso da foto pública real ({hero_photo}) no hero split layout / fundo e fotos da galeria no showcase.
3. SPECIALIZED SERVICES GRID: 4 a 6 serviços reais do nicho ({profile['core_services']}) com nomes específicos, benefício claro e botão individual de consulta.
4. COMPETITIVE DIFFERENTIALS (WHY CHOOSE US): 3 a 4 pilares operacionais que resolvem as dores dos clientes e demonstram excelência.
5. GOOGLE REPUTATION & REAL SOCIAL PROOF: Destaque da nota {lead.rating or 5.0}★ do Google Maps com 3 depoimentos autênticos contextualizados para este nicho.
6. LOCATION CONVENIENCE & INTERACTIVE MAP: Endereço completo ({lead.formatted_address or 'Localidade'}), mapa incorporado, horários de atendimento e instruções de acesso/estacionamento.
7. STICKY MOBILE CONVERSION BAR: Barra flutuante inferior fixa para dispositivos móveis com botão de ligar e botão pulsante de WhatsApp com link pronto.
8. TECHNICAL EXCELLENCE: 100% responsivo, PageSpeed 95+, First Contentful Paint < 1.0s, sem elementos que causem Cumulative Layout Shift (CLS).

Retorne ESTRITAMENTE um JSON no seguinte formato:
{{
  "stitch_prompt": "O prompt técnico completo em inglês com todas as 8 seções minuciosamente detalhadas",
  "suggested_components": [
    "HeroSectionWithSplitLayout",
    "TrustBadgesRow",
    "ServicesGridWithIconBadges",
    "CompetitiveEdgeMatrix",
    "GoogleReputationShowcase",
    "InteractiveLocalMapAndHours",
    "StickyMobileWhatsAppBar",
    "CleanFooterWithLegalInfo"
  ],
  "brand_identity": "Resumo executivo em português da identidade da marca (paleta HEX, tom de voz, tipografia e proposta de valor)"
}}
"""

        try:
            response_text = await self._call_gemini(prompt, max_tokens=3000)
            data = self._extract_json(response_text)
            stitch_prompt_val = data.get("stitch_prompt", "").strip()

            # Se o retorno for pequeno ou incompleto, complementa com o construtor avançado
            if not stitch_prompt_val or len(stitch_prompt_val) < 250:
                logger.warning(f"Stitch prompt gerado via Gemini ficou muito curto ({len(stitch_prompt_val)} chars). Usando construtor especializado.")
                stitch_prompt_val = build_impeccable_site_prompt(lead, profile, diagnosis)

            brand_id_val = data.get("brand_identity") or build_brand_identity_summary(lead, profile, diagnosis)
            components_val = data.get("suggested_components") or [
                "HeroSectionWithSplitLayout",
                "TrustBadgesRow",
                "ServicesGridWithIconBadges",
                "CompetitiveEdgeMatrix",
                "GoogleReputationShowcase",
                "InteractiveLocalMapAndHours",
                "StickyMobileWhatsAppBar",
                "CleanFooterWithLegalInfo"
            ]

            logger.info(f"Stitch prompt ultra-personalizado gerado com sucesso via Gemini para {lead.name} (Nicho: {profile['niche_pt']})")
            return StitchPromptResult(
                lead_name=lead.name,
                stitch_prompt=stitch_prompt_val,
                suggested_components=components_val,
                brand_identity=brand_id_val,
            )

        except Exception as e:
            logger.error(f"Falha na geração do Stitch prompt via Gemini ({e}). Usando gerador arquitetural especializado.")
            fallback_prompt = build_impeccable_site_prompt(lead, profile, diagnosis)
            fallback_brand = build_brand_identity_summary(lead, profile, diagnosis)
            return StitchPromptResult(
                lead_name=lead.name,
                stitch_prompt=fallback_prompt,
                suggested_components=[
                    "HeroSectionWithSplitLayout",
                    "TrustBadgesRow",
                    "ServicesGridWithIconBadges",
                    "CompetitiveEdgeMatrix",
                    "GoogleReputationShowcase",
                    "InteractiveLocalMapAndHours",
                    "StickyMobileWhatsAppBar",
                    "CleanFooterWithLegalInfo"
                ],
                brand_identity=fallback_brand,
            )

