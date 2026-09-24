import json
import logging
import re
from typing import Optional

import httpx

from app.core.config import settings
from app.core.interfaces.llm_service import LLMService
from app.models.diagnosis import (
    DiagnosisResult, DiagnosticFact, DiagnosticInference,
    RecommendationItem, SalesRecommendation, StitchPromptResult
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
        """Diagnóstico heurístico rico caso a API Gemini não responda."""
        lead = report.lead
        ps = report.pagespeed
        sec = report.security
        ig = report.instagram

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
            facts.append(DiagnosticFact(pilar="google", text=f"Avaliação no Google: {lead.rating}/5.0 com {lead.user_rating_count or 0} avaliações."))
            if lead.rating >= 4.5:
                inferences.append(DiagnosticInference(pilar="google", text=f"Excelente reputação no Google ({lead.rating}★). Exibir avaliações no site transmite confiança imediata e converte até 4x mais."))
            else:
                inferences.append(DiagnosticInference(pilar="google", text=f"Nota {lead.rating}★ no Google. Melhorar a presença digital e incentivar avaliações positivas é prioridade."))
        if lead.national_phone_number:
            facts.append(DiagnosticFact(pilar="google", text=f"Telefone cadastrado: {lead.national_phone_number}."))
        if lead.formatted_address:
            facts.append(DiagnosticFact(pilar="google", text=f"Endereço verificado: {lead.formatted_address}."))

        # Pilar Website
        if not lead.website_uri:
            facts.append(DiagnosticFact(pilar="website", text="Nenhum site cadastrado no Google Empresa."))
            inferences.append(DiagnosticInference(pilar="website", text="A ausência de site próprio é o maior gargalo: o negócio perde leads 24h por dia para concorrentes que aparecem na busca."))
            recommendations.append(RecommendationItem(
                category="Website", severity="HIGH",
                finding="O negócio não possui site ou landing page cadastrado.",
                action_item="Criar uma landing page de alta conversão com botão direto para WhatsApp.",
            ))
        elif ps:
            score = ps.performance_score
            facts.append(DiagnosticFact(pilar="website", text=f"Site ativo: {lead.website_uri}. PageSpeed: {score or 'N/A'}/100."))
            if score and score < 50:
                inferences.append(DiagnosticInference(pilar="website", text=f"Carregamento lento ({score}/100). Mais de 50% dos visitantes desistem antes do site abrir, queimando vendas."))
                recommendations.append(RecommendationItem(
                    category="Performance", severity="HIGH",
                    finding=f"PageSpeed crítico ({score}/100) prejudica o ranqueamento no Google e a conversão.",
                    action_item="Refatorar a estrutura da página ou migrar para landing page ultrarrápida.",
                ))
            else:
                inferences.append(DiagnosticInference(pilar="website", text=f"Performance {score}/100. O site funciona, mas há espaço para otimizar conversão e velocidade mobile."))

        # Pilar Social
        if ig and (ig.found or ig.is_business_account):
            facts.append(DiagnosticFact(pilar="social", text=f"Perfil do Instagram identificado (@{ig.handle})."))
            inferences.append(DiagnosticInference(pilar="social", text="Presença social ativa. Conectar o Instagram ao novo site cria um ecossistema completo de aquisição."))
        else:
            facts.append(DiagnosticFact(pilar="social", text="Nenhum perfil oficial de Instagram identificado no radar."))
            inferences.append(DiagnosticInference(pilar="social", text="Ausência de rede social forte reduz a prova visual da empresa para clientes mais jovens."))

        # Recomendações de Venda
        ps_str = f"com PageSpeed {ps.performance_score}/100" if ps and ps.performance_score else "sem site próprio"
        approach = f"Abordar destacando que concorrentes em {lead.formatted_address or 'sua região'} já captam clientes pelo celular enquanto a empresa está {ps_str}."

        sales_rec = SalesRecommendation(
            approach_angle=approach,
            pain_points=[
                f"Perda diária de clientes que pesquisam por serviços locais no Google e não encontram o negócio",
                "Dependência quase exclusiva de indicações e boca a boca para fechar novos clientes",
                "Falta de um canal automatizado para agendar e tirar dúvidas fora do horário comercial",
            ],
            talking_points=[
                f"A ótima reputação ({lead.rating or 4.5}★ no Google) já é autoridade suficiente para fechar contratos direto no site",
                "Uma página moderna e rápida pode triplicar o volume de contatos no WhatsApp com o mesmo tráfego",
                "Criamos e publicamos o site pronto com botão de WhatsApp e mapa em poucos dias",
            ],
            value_proposition=f"Transformar a presença digital de {lead.name} em uma máquina contínua de atração de novos clientes.",
        )

        # Mensagens de Abordagem
        whatsapp_draft = (
            f"Olá pessoal da {lead.name}! Tudo bem? 👋\n\n"
            f"Estive analisando a presença digital de vocês em {lead.formatted_address or 'sua cidade'} e notei algo que está custando clientes todo dia: "
            f"{'vocês ainda não possuem um site profissional otimizado para celular' if not lead.website_uri else 'o site de vocês está com carregamento lento no celular'}.\n\n"
            f"Vocês já têm uma excelente reputação ({lead.rating or 4.9}★ no Google), mas estão perdendo para concorrentes com presença online mais agressiva.\n\n"
            f"Montei um diagnóstico rápido com 3 melhorias práticas para aumentar os contatos no WhatsApp de vocês. Posso te mandar por aqui? É sem custo nenhum! 🚀"
        )

        email_draft = (
            f"Assunto: Oportunidade de captação digital para {lead.name}\n\n"
            f"Olá equipe da {lead.name},\n\n"
            f"Realizamos uma auditoria técnica na presença digital das principais empresas da sua região e identificamos que {lead.name} possui excelente autoridade no Google ({lead.rating or 4.9} estrelas com {lead.user_rating_count or 0} avaliações).\n\n"
            f"No entanto, identificamos uma oportunidade crítica: {'a ausência de um site institucional de alta conversão' if not lead.website_uri else f'a velocidade de carregamento do site atual ({ps.performance_score if ps else 50}/100)'} está desviando potenciais clientes para concorrentes locais.\n\n"
            f"Criamos uma proposta de landing page personalizada para vocês, com agendamento direto via WhatsApp e integração completa com Google Maps.\n\n"
            f"Podemos agendar uma conversa rápida de 10 minutos esta semana?\n\n"
            f"Atenciosamente,\nConsultoria de Presença Digital"
        )

        instagram_draft = (
            f"Opa, tudo bem? 👋 Estava conferindo o trabalho da {lead.name} aqui no Instagram e achei incrível! "
            f"Notei um ponto bem rápido na presença de vocês no Google que pode estar fazendo vocês perderem clientes. "
            f"Preparei uma ideia prática de como resolver isso com uma página moderna. Posso te mandar o link aqui no direct?"
        )

        site_summary = "Sem site próprio — prioridade máxima." if not lead.website_uri else f"Site com PageSpeed {ps.performance_score if ps else 'N/A'}/100."
        return DiagnosisResult(
            lead_name=lead.name,
            overall_summary=f"Auditoria de presença digital para {lead.name}. {site_summary}",
            recommendations=recommendations,
            needs_new_website=needs_new_site,
            whatsapp_draft=whatsapp_draft,
            email_draft=email_draft,
            instagram_draft=instagram_draft,
            facts=facts,
            inferences=inferences,
            sales_recommendation=sales_rec,
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

        data_context = f"""
DADOS REAIS DO LEAD:
- Nome: {lead.name}
- Endereço / Cidade: {lead.formatted_address or 'Não informado'}
- Telefone: {lead.national_phone_number or 'Ausente'}
- Website atual: {lead.website_uri or 'NENHUM (SEM SITE)'}
- Avaliação Google Maps: {lead.rating or 'N/A'}/5.0 ({lead.user_rating_count or 0} avaliações)
- PageSpeed Score: {ps.performance_score if ps else 'N/A'}/100
- SEO Score: {ps.seo_score if ps else 'N/A'}/100
- Instagram: {'@' + ig.handle if ig and ig.found else 'Não encontrado'}
"""

        prompt = f"""Você é um consultor especialista em presença digital e fechamento de vendas B2B no Brasil.
Analise os dados deste lead e gere um diagnóstico completo, comercial e altamente persuasivo.

{data_context}

Retorne estritamente um JSON com a seguinte estrutura:
{{
  "overall_summary": "Resumo executivo de 2-3 frases sobre o status digital do lead e sua principal oportunidade",
  "needs_new_website": true,
  "facts": [
    {{"pilar": "google", "text": "Fato verificado com número de estrelas e avaliações reais"}},
    {{"pilar": "website", "text": "Fato verificado sobre existência do site, PageSpeed score ou SSL"}},
    {{"pilar": "social", "text": "Fato verificado sobre presença no Instagram ou redes sociais"}},
    {{"pilar": "general", "text": "Outro fato relevante identificado"}}
  ],
  "inferences": [
    {{"pilar": "google", "text": "Análise de impacto da reputação atual nas decisões de compra de novos clientes"}},
    {{"pilar": "website", "text": "Análise de impacto do status do site na perda de clientes para concorrentes"}},
    {{"pilar": "social", "text": "Análise de impacto da presença social no engajamento e validação de marca"}},
    {{"pilar": "general", "text": "Oportunidade central de crescimento identificada"}}
  ],
  "recommendations": [
    {{"category": "Website / Performance", "severity": "HIGH", "finding": "Problema específico identificado", "action_item": "Ação recomendada para resolver"}}
  ],
  "sales_recommendation": {{
    "approach_angle": "Gancho exato de entrada para abordar este cliente no frio, citando dados específicos dele",
    "pain_points": [
      "Ponto de dor 1 específico deste negócio",
      "Ponto de dor 2",
      "Ponto de dor 3"
    ],
    "talking_points": [
      "Argumento de venda 1 irrefutável para usar na reunião",
      "Argumento de venda 2",
      "Argumento de venda 3"
    ],
    "value_proposition": "Proposta de valor central em uma frase forte"
  }},
  "whatsapp_draft": "Mensagem curta, amigável e direta ao ponto para WhatsApp, usando emojis, citando dados dele e terminando com CTA de baixo atrito",
  "email_draft": "Email formal mas persuasivo com 'Assunto:' chamativo, citando dados da auditoria e pedindo reunião de 10 min",
  "instagram_draft": "Mensagem de direct curta, elogiosa e curiosa para puxar conversa"
}}

Regras obrigatórias:
1. facts: liste pelo menos 4 fatos divididos entre os pilares google, website e social.
2. inferences: liste análises profundas de impacto comercial para cada pilar.
3. whatsapp_draft, email_draft e instagram_draft DEVEM conter o nome real do negócio e os dados fornecidos.
4. Responda em português do Brasil sem usar blocos markdown extras.
"""

        try:
            response_text = await self._call_gemini(prompt, max_tokens=3500)
            data = self._extract_json(response_text)
            logger.info(f"Diagnóstico gerado com sucesso via Gemini para {lead.name}")
        except Exception as e:
            logger.error(f"Falha na geração via Gemini ({e}). Usando fallback heurístico rico.")
            return self._build_local_diagnosis(report)

        facts = [DiagnosticFact(**f) for f in data.get("facts", [])]
        inferences = [DiagnosticInference(**i) for i in data.get("inferences", [])]
        recs = [RecommendationItem(**r) for r in data.get("recommendations", [])]

        sales_data = data.get("sales_recommendation")
        sales_rec = SalesRecommendation(**sales_data) if sales_data else None

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
        )

    def _detect_segment(self, name: str) -> str:
        n = name.lower()
        if any(w in n for w in ["advog", "jurid", "direito", "associados", "oab"]):
            return "escritório jurídico de advocacia — foco em autoridade, discrição, conformidade OAB e agendamento de consultas"
        if any(w in n for w in ["odonto", "dent", "implant", "sorriso", "orto"]):
            return "clínica odontológica — foco em estética do sorriso, antes/depois, tecnologia e agendamento rápido via WhatsApp"
        if any(w in n for w in ["clinic", "medic", "doutor", "dr.", "saude", "oftalm", "dermato"]):
            return "clínica médica de saúde — foco em especialidades, corpo clínico qualificado, humanização e agendamento"
        if any(w in n for w in ["restaurante", "pizz", "burger", "bistr", "cafe", "culin"]):
            return "restaurante gastronômico — cardápio visual interativo, fotos atraentes, delivery e reserva de mesas"
        if any(w in n for w in ["salao", "beleza", "barbearia", "estetica", "spa", "hair"]):
            return "centro de beleza e estética — portfólio visual, serviços em destaque e agendamento de horários"
        if any(w in n for w in ["academia", "fitness", "crossfit", "treino", "personal"]):
            return "academia e fitness — planos, modalidades, tour da estrutura e aula experimental grátis"
        return "negócio local profissional — foco em credibilidade, diferenciais competitivos e captação de clientes via WhatsApp"

    async def generate_stitch_prompt(
        self, report: FullTriageReport, diagnosis: DiagnosisResult
    ) -> StitchPromptResult:
        lead = report.lead
        segment = self._detect_segment(lead.name)
        rating_info = f"{lead.rating}★ com {lead.user_rating_count or 0} avaliações no Google" if lead.rating else "negócio bem avaliado"

        prompt = f"""Você é um engenheiro sênior especialista em prompts de UI para o Google Stitch AI.
Crie um prompt em INGLÊS ultra-detalhado, modular e personalizado para o Stitch gerar a landing page perfeita para:

Negócio: {lead.name}
Nicho / Segmento: {segment}
Localização: {lead.formatted_address or 'Brasil'}
WhatsApp / Telefone: {lead.national_phone_number or 'Disponível na página'}
Reputação Google: {rating_info}
Diagnóstico: {diagnosis.overall_summary}

Retorne estritamente um JSON com a estrutura:
{{
  "stitch_prompt": "Prompt em inglês completo com especificações de seções, paleta de cores, tipografia, micro-interações e CTAs de alta conversão",
  "suggested_components": ["HeroBanner", "ValueProposition", "ServicesGrid", "GoogleReviewsSection", "LocationMap", "WhatsAppFloatingCTA", "Footer"],
  "brand_identity": "Descrição em português da identidade de marca sugerida (cores, tom de voz, estilo visual)"
}}
"""

        try:
            response_text = await self._call_gemini(prompt, max_tokens=2000)
            data = self._extract_json(response_text)
            logger.info(f"Stitch prompt gerado com sucesso via Gemini para {lead.name}")
        except Exception as e:
            logger.error(f"Falha na geração do Stitch prompt via Gemini ({e}). Usando fallback rico.")
            rating_str = f" Include a dedicated Google Reviews showcase displaying {lead.rating}/5.0 stars and testimonials from real clients." if lead.rating else ""
            return StitchPromptResult(
                lead_name=lead.name,
                stitch_prompt=(
                    f"Create a high-converting, mobile-first website for '{lead.name}', specialized as {segment}. "
                    f"Location: {lead.formatted_address or 'Brasil'}. Phone/WhatsApp: {lead.national_phone_number or 'Contact via button'}. "
                    f"Design style: Modern, dark mode luxury aesthetic with clean typography, smooth gradients, and high-contrast CTA buttons. "
                    f"Structure: 1) Hero section with strong value proposition, professional imagery, and instant WhatsApp booking CTA. "
                    f"2) Highlights and Trust Badges demonstrating market leadership. "
                    f"3) Interactive Services & Solutions Grid with detailed cards and icon badges. "
                    f"4) Social Proof & Reputation section.{rating_str} "
                    f"5) Location & Hours section with embedded Google Maps interactive view. "
                    f"6) Sticky bottom WhatsApp floating contact button for maximum mobile conversion. "
                    f"7) Clean footer with address, contact numbers, and professional credentials. "
                    f"Technical requirements: 100% responsive, optimized for PageSpeed 95+, accessible WCAG AA standards."
                ),
                suggested_components=["HeroBanner", "TrustBadges", "ServicesGrid", "SocialProof", "GoogleReviews", "LocationMap", "WhatsAppCTA", "Footer"],
                brand_identity=f"Sofisticado, moderno e focado em alta conversão para {lead.name}",
            )

        return StitchPromptResult(
            lead_name=lead.name,
            stitch_prompt=data.get("stitch_prompt", ""),
            suggested_components=data.get("suggested_components", []),
            brand_identity=data.get("brand_identity"),
        )
