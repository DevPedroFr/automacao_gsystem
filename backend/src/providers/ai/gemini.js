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
}/**
 * Monta o prompt detalhado para o Gemini AI
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
8. stitch_prompt: Generate a high-converting website generation prompt for Google Stitch (an AI website builder) in ${targetLanguage}. This generated prompt will be used directly in Google Stitch to create a complete, premium landing page for the business ${lead.name}. The prompt MUST follow "A Fórmula do Prompt Perfeito" and be structured under these 4 specific headings:
   - **Objetivo e Nicho:** Define the specific business purpose for ${lead.name}, their target audience, and the niche (${lead.category || 'Serviços'}).
   - **Estrutura de Seções:** Instruct Google Stitch to create a complete, multi-section page and list the exact contents from top to bottom (no lorem ipsum, write actual copy in ${targetLanguage}):
     1. Header Navigation: Logo placeholder, links to Services, About, Testimonials, FAQ, and a "Contatar/Agendar" CTA button.
     2. Hero Section: A powerful pre-written H1 title and subheadline in ${targetLanguage} tailored specifically for ${lead.name}, space for a high-quality banner image, and a primary CTA button.
     3. Prova Social / Avaliações: A visual grid or cards displaying the business's Google Rating ("${lead.google_rating || '4.5'}/5.0 stars based on ${lead.google_reviews_count || '10'} reviews") and 3 realistic customer testimonials.
     4. Serviços Grid: A 3-column card layout detailing 3 key services for this niche, each with a pre-written title and description in ${targetLanguage}.
     5. Sobre Nós e Autoridade Local: An about us section detailing their local authority in ${lead.city}, with a placeholder for a team photo.
     6. FAQ (Perguntas Frequentes): 3 common questions and answers in ${targetLanguage} specific to the niche to resolve objections.
     7. Rodapé e Contato: Integrated booking form placeholder, office hours, address, phone, and social links.
   - **Direção de Arte:** Detail the visual guidelines, including a curated color scheme with exact hex codes (primary, secondary, background, and accent/CTA colors) tailored for this niche, modern font pairs (e.g. Outfit and Inter), visual feeling (e.g. clean, premium, trustworthy), and generous padding.
   - **Elementos Específicos:** Specify button styling (e.g., rounded-full, subtle shadows, hover effects, specific CTA texts), responsive layouts, and placeholders/mockups for team and service images.

Return a JSON object conforming to this schema:
{
  "observed_facts": "string (multiline text in PT-BR)",
  "inferences": "string (multiline text in PT-BR)",
  "recommendations": "string (multiline text in PT-BR)",
  "email_draft": "string (email draft in ${targetLanguage})",
  "whatsapp_draft": "string (whatsapp message in ${targetLanguage})",
  "instagram_draft": "string (instagram inbox message in ${targetLanguage})",
  "stitch_prompt": "string (Google Stitch prompt in ${targetLanguage})"
}`;
}

/**
 * Faz a chamada real à API do Gemini
 */
async function callGeminiApi(lead, modelName = config.GEMINI_MODEL) {
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${config.GEMINI_API_KEY}`;
  const promptText = buildPrompt(lead);

  const payload = {
    contents: [
      {
        parts: [
          {
            text: promptText,
          }
        ]
      }
    ],
    generationConfig: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: 'OBJECT',
        properties: {
          observed_facts: { type: 'STRING' },
          inferences: { type: 'STRING' },
          recommendations: { type: 'STRING' },
          email_draft: { type: 'STRING' },
          whatsapp_draft: { type: 'STRING' },
          instagram_draft: { type: 'STRING' },
          stitch_prompt: { type: 'STRING' }
        },
        required: ['observed_facts', 'inferences', 'recommendations', 'email_draft', 'whatsapp_draft', 'instagram_draft', 'stitch_prompt']
      }
    }
  };

  const startTime = Date.now();
  let statusCode = null;

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(60000), // Timeout de 60 segundos
    });

    statusCode = response.status;
    const responseTimeMs = Date.now() - startTime;

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Erro na API do Gemini (Status ${response.status}): ${errorText}`);
    }

    const data = await response.json();
    const responseText = data.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!responseText) {
      throw new Error('Retorno da API do Gemini não contém o formato esperado de texto.');
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
      provider: 'gemini',
      serviceType: 'ai',
      endpoint: `generateContent:${modelName}`,
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
    console.error(`❌ [Gemini AI Provider] Falha na chamada da API:`, err.message);

    logApiCall({
      provider: 'gemini',
      serviceType: 'ai',
      endpoint: `generateContent:${modelName}`,
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
 * Gera diagnóstico de IA usando o provedor do Gemini (com retentativa e fallback)
 * @param {Object} lead - Dados do lead
 * @returns {Promise<Object>} Diagnóstico estruturado
 */
async function generateDiagnostic(lead) {
  console.log(`[Gemini AI Provider] Iniciando diagnóstico com IA para "${lead.name}"...`);

  const maxAttempts = 3;
  let delayMs = 1500;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    // Tenta diferentes modelos a cada tentativa para contornar indisponibilidades ou limites de cota
    let modelToUse = config.GEMINI_MODEL;
    if (attempt === 2) {
      modelToUse = 'gemini-2.0-flash';
    } else if (attempt === 3) {
      modelToUse = 'gemini-flash-latest';
    }

    try {
      if (attempt > 1) {
        console.log(`⏳ [Gemini AI Provider] Aguardando ${delayMs}ms antes da tentativa ${attempt}/${maxAttempts} (Modelo: ${modelToUse})...`);
        await sleep(delayMs);
        delayMs *= 2;
      }

      console.log(`🤖 [Gemini AI Provider] Tentativa ${attempt}/${maxAttempts} usando "${modelToUse}" para "${lead.name}"...`);
      return await callGeminiApi(lead, modelToUse);
    } catch (error) {
      console.warn(`⚠️ [Gemini AI Provider] Tentativa ${attempt}/${maxAttempts} falhou:`, error.message);

      if (attempt === maxAttempts) {
        console.error(`❌ [Gemini AI Provider] Todas as ${maxAttempts} tentativas falharam.`);
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
