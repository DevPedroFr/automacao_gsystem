const { v4: uuidv4 } = require('uuid');
const config = require('../../config/env');
const db = require('../../config/database');

/**
 * Grava o log de auditoria da chamada de API
 */
async function logApiCall({ provider, serviceType, endpoint, statusCode, responseTimeMs, success, errorMessage }) {
  try {
    await db.prepare(`
      INSERT INTO api_call_logs (id, provider, service_type, endpoint, status_code, response_time_ms, success, error_message)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      uuidv4(),
      provider,
      serviceType,
      endpoint,
      statusCode || null,
      responseTimeMs || 0,
      success ? 1 : 0,
      errorMessage || null
    );
  } catch (err) {
    console.error('❌ Falha ao registrar log de chamada da API em api_call_logs:', err);
  }
}

/**
 * Monta o prompt detalhado para o OpenAI
 */
function buildPrompt(lead) {
  const addressLower = (lead.address || '').toLowerCase();
  const cityLower = (lead.city || '').toLowerCase();
  const phoneLower = (lead.phone || '').toLowerCase();
  
  // Detecção robusta de país
  const isBrazil = phoneLower.includes('+55') || 
                   addressLower.includes('brazil') || 
                   addressLower.includes('brasil') || 
                   addressLower.includes(', br') ||
                   cityLower.includes('mogi das cruzes') ||
                   cityLower.includes('são paulo') ||
                   cityLower.includes('curitiba') ||
                   cityLower.includes('porto alegre') ||
                   cityLower.includes('florianópolis') ||
                   cityLower.includes('rio de janeiro') ||
                   cityLower.includes('belo horizonte');
                   
  const targetLanguage = isBrazil ? 'PORTUGUESE (Brazil)' : 'ENGLISH';

  return `You are an expert sales consultant for digital agencies.
Analyze the following business lead data:

Lead Data:
- Name: ${lead.name}
- Category/Niche: ${lead.category || 'N/A'}
- City: ${lead.city || 'N/A'}
- Address: ${lead.address || 'N/A'}
- Website: ${lead.website || 'No website'}
- Primary Image URL: ${lead.image_url || 'N/A'}
- Google Maps Rating: ${lead.google_rating || 'N/A'} stars (${lead.google_reviews_count || 0} reviews)
- PageSpeed Insights Mobile Score: ${lead.pagespeed_score || 'N/A'}/100
- Core Web Vitals (Mobile): LCP=${lead.lcp_ms || 'N/A'}ms, INP=${lead.inp_ms || 'N/A'}ms, CLS=${lead.cls || 'N/A'}
- SEO Score: ${lead.seo_score || 'N/A'}/100
- Instagram: ${lead.has_instagram ? 'Yes' : 'No'}
- Facebook: ${lead.has_facebook ? 'Yes' : 'No'}
- Social Media Last Post: ${lead.social_last_post_days !== null ? `${lead.social_last_post_days} days ago` : 'N/A'}
- Digital Maturity Score (DMS): ${lead.dms}/100
- Commercial Opportunity Score (COS): ${lead.cos}/100
- Prioritization Category: ${lead.priority}

Instructions:
1. TARGET LANGUAGE: The target language for outreach drafts is ${targetLanguage}. You MUST generate the email_draft, whatsapp_draft, and instagram_draft in ${targetLanguage}.
2. observed_facts: State facts about their digital presence based ONLY on the data provided. Do NOT invent, assume or extrapolate data that is N/A or missing. Format this as bullet points in Portuguese (Brazil) with a professional tone.
3. inferences: Analyze what these facts mean. If they lack a website or have poor speed, explain the business consequences (lost traffic, drop in search rankings, friction). Format this in Portuguese (Brazil) as paragraphs.
4. recommendations: List actionable, prioritized recommendations based on the gaps. Format this as bullet points in Portuguese (Brazil).
5. email_draft: Draft a highly professional B2B cold outreach email in ${targetLanguage}. Reference their specific digital gaps and explicitly mention that we have attached a PDF diagnostic report of their business. Offer a free 15-minute diagnostic session to discuss the report. Leave placeholders like [Seu Nome]/[Your Name] for the sender.
6. whatsapp_draft: Draft a direct, friendly B2B outreach message for WhatsApp in ${targetLanguage}. Reference that we are sending their digital diagnostic in PDF format. Keep it concise, engaging, and professional. Use emojis appropriately.
7. instagram_draft: Draft a brief, catchy B2B outreach message for Instagram Direct Message (inbox) in ${targetLanguage}. Refer to the diagnostic PDF we have prepared and sent to them. Keep it very short and conversational.
8. stitch_prompt: Generate a high-converting website generation prompt for Google Stitch (an AI website builder) in ${targetLanguage}. This generated prompt will be used directly in Google Stitch to create a complete, premium landing page for the business ${lead.name}. The prompt MUST follow "A Fórmula do Prompt Perfeito" and incorporate strict 2026 B2B/Local conversion rules. Structure it under these 4 specific headings:
   - **Objetivo e Nicho:** Define the specific business purpose for ${lead.name}, their target audience, and the niche (${lead.category || 'Serviços'}).
   - **Estrutura de Seções (Obrigatório seguir estas regras de conversão):** 
     Instruct Google Stitch to create a complete, mobile-first page. DO NOT use placeholder text (lorem ipsum); write actual persuasive, benefit-driven copy in ${targetLanguage} using the PAS (Problem-Agitate-Solve) framework:
     IMPORTANT IMAGE RULE: If "Primary Image URL" is provided in the Lead Data above and is not "N/A", you MUST use it in the Hero Section or Header by injecting exactly \`{{DATA:IMAGE:${lead.image_url}}}\` instead of a generic placeholder like \`{{DATA:IMAGE:IMAGE_1}}\`.
     1. Header Navigation: Clean logo placeholder, links to Services, About, Reviews, and a high-contrast "Agendar" CTA button.
     2. Hero Section (Above the Fold): Must load fast. H1 must be 6-8 words max focusing on a specific outcome/benefit. Subheadline (2-3 lines) explaining how the service delivers. Image: Use the Primary Image URL here if available, otherwise use a relevant placeholder. Primary CTA button in contrasting color with micro-copy underneath (e.g., "Rápido e sem compromisso").
     3. Trust Banner: A grayscale "Trusted by" or "Verified Local Business" banner immediately below the hero to build instant authority.
     4. PAS Copy Section: Acknowledge the core pain point (Problem), highlight the cost of inaction (Agitate), and position ${lead.name} as the easy solution (Solve). 
     5. Serviços (Benefit-Driven): 3-column card layout for services. Focus on outcomes (e.g. "Ganhe mais casos" instead of "Consultoria Jurídica").
     6. Prova Social e Autoridade: A section with their Google Rating ("${lead.google_rating || '4.5'}/5.0 stars based on ${lead.google_reviews_count || '10'} reviews"), 3 realistic testimonials, and trust badges (e.g. SSL, Certifications, "100% Garantido").
     7. Rodapé e Contato (Mobile-First): Integrated booking form, office hours, address, phone. On mobile, instruct to use a Sticky Bottom CTA banner.
   - **Direção de Arte:** Detail visual guidelines: curated color scheme with exact hex codes tailored for this niche, modern font pairs (e.g. Outfit/Inter), generous white space, and a feeling of extreme trust and premium quality.
   - **Elementos Específicos:** Specify button styling (e.g., rounded-full, subtle shadows, hover effects), responsive single-column layouts for mobile, and instructions to ensure maximum visual contrast for CTAs.

Return a JSON object conforming to this schema:
{
  "observed_facts": "string (multiline text in PT-BR)",
  "inferences": "string (multiline text in PT-BR)",
  "recommendations": "string (multiline text in PT-BR)",
  "email_draft": "string (email draft in ${targetLanguage})",
  "whatsapp_draft": "string (whatsapp message in ${targetLanguage})",
  "instagram_draft": "string (instagram inbox message in ${targetLanguage})",
  "stitch_prompt": "string (Google Stitch prompt in ${targetLanguage})"
}
`;
}

/**
 * Faz a chamada real à API da OpenAI
 */
async function callOpenAiApi(lead, modelName = 'gpt-4o-mini') {
  const endpoint = 'https://api.openai.com/v1/chat/completions';
  const promptText = buildPrompt(lead);

  const payload = {
    model: modelName,
    response_format: { type: "json_object" },
    messages: [
      {
        role: "system",
        content: "You are a helpful assistant designed to output strict JSON according to the schema provided in the prompt."
      },
      {
        role: "user",
        content: promptText
      }
    ],
    temperature: 0.7,
  };

  const startTime = Date.now();
  let statusCode = null;

  try {
    if (!config.OPENAI_API_KEY) {
      throw new Error('Chave de API da OpenAI (OPENAI_API_KEY) não configurada no .env.');
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.OPENAI_API_KEY}`
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(60000), // Timeout de 60 segundos
    });

    statusCode = response.status;
    const responseTimeMs = Date.now() - startTime;

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Erro na API da OpenAI (Status ${response.status}): ${errorText}`);
    }

    const data = await response.json();
    const responseText = data.choices?.[0]?.message?.content;

    if (!responseText) {
      throw new Error('Retorno da API da OpenAI não contém o formato esperado de texto.');
    }

    // Parse do JSON retornado pela IA
    const diagnostic = JSON.parse(responseText);

    // Validação de formato/campos obrigatórios
    if (
      !diagnostic.observed_facts || 
      !diagnostic.inferences || 
      !diagnostic.recommendations || 
      !diagnostic.email_draft || 
      !diagnostic.whatsapp_draft || 
      !diagnostic.instagram_draft || 
      !diagnostic.stitch_prompt
    ) {
      throw new Error('JSON retornado pela IA está incompleto (faltam campos obrigatórios).');
    }

    // Registrar chamada com sucesso
    logApiCall({
      provider: 'openai',
      serviceType: 'ai',
      endpoint: `chat/completions:${modelName}`,
      statusCode,
      responseTimeMs,
      success: true,
    });

    return {
      ...diagnostic,
      diagnostic_status: 'completed',
    };

  } catch (err) {
    const responseTimeMs = Date.now() - startTime;
    console.error(`❌ [OpenAI Provider] Falha na chamada da API:`, err.message);

    logApiCall({
      provider: 'openai',
      serviceType: 'ai',
      endpoint: `chat/completions:${modelName}`,
      statusCode,
      responseTimeMs,
      success: false,
      errorMessage: err.message,
    });

    throw err; // Repassa o erro para disparar o retry
  }
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Gera diagnóstico de IA usando o provedor da OpenAI (com retentativa)
 * @param {Object} lead - Dados do lead
 * @returns {Promise<Object>} Diagnóstico estruturado
 */
async function generateDiagnostic(lead) {
  console.log(`[OpenAI Provider] Iniciando diagnóstico com IA para "${lead.name}"...`);

  const maxAttempts = 3;
  let delayMs = 1500;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    let modelToUse = 'gpt-4o-mini';
    if (attempt === 3) {
      modelToUse = 'gpt-4o'; // fallback
    }

    try {
      if (attempt > 1) {
        console.log(`⏳ [OpenAI Provider] Aguardando ${delayMs}ms antes da tentativa ${attempt}/${maxAttempts} (Modelo: ${modelToUse})...`);
        await sleep(delayMs);
        delayMs *= 2;
      }

      console.log(`🤖 [OpenAI Provider] Tentativa ${attempt}/${maxAttempts} usando "${modelToUse}" para "${lead.name}"...`);
      return await callOpenAiApi(lead, modelToUse);
    } catch (error) {
      console.warn(`⚠️ [OpenAI Provider] Tentativa ${attempt}/${maxAttempts} falhou:`, error.message);

      if (attempt === maxAttempts) {
        console.error(`❌ [OpenAI Provider] Todas as ${maxAttempts} tentativas falharam.`);
        return {
          observed_facts: null,
          inferences: null,
          recommendations: null,
          email_draft: null,
          diagnostic_status: 'ai_validation_failed',
          error_message: error.message,
        };
      }
    }
  }
}

module.exports = { generateDiagnostic };
