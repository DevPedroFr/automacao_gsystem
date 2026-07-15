const { v4: uuidv4 } = require('uuid');
const db = require('../../config/database');
const mockProvider = require('./mock');

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
 * Analisa a presença de redes sociais vasculhando o HTML do website do lead (Basic Social Provider)
 * @param {string} businessName - Nome do negócio
 * @param {string} websiteUrl - URL do website
 * @returns {Promise<Object>} Dados de presença social
 */
async function analyzeSocialPresence(businessName, websiteUrl) {
  if (!websiteUrl) {
    return {
      has_instagram: 0,
      instagram_url: null,
      has_facebook: 0,
      has_linkedin: 0,
      social_last_post_days: null,
    };
  }

  console.log(`[Basic Social Provider] Analisando HTML do site "${websiteUrl}" em busca de links de redes sociais...`);

  const startTime = Date.now();
  let statusCode = null;

  try {
    const response = await fetch(websiteUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
      },
      // Timeout seguro de 12 segundos
      signal: AbortSignal.timeout(12000),
    });

    statusCode = response.status;
    const responseTimeMs = Date.now() - startTime;

    if (!response.ok) {
      throw new Error(`Erro ao acessar website (Status ${response.status})`);
    }

    const html = await response.text();

    // 1. Procurar links válidos excluindo rotas de share/plugins comuns
    const instaMatch = html.match(/href=["'](?:https?:\/\/)?(?:www\.)?instagram\.com\/(?!developer|about|legal|p\/|explore)([a-zA-Z0-9_\-\.]+)[\/"']?/i);
    let has_instagram = 0;
    let instagram_url = null;
    if (instaMatch && instaMatch[1]) {
      has_instagram = 1;
      instagram_url = `https://instagram.com/${instaMatch[1]}`;
    }

    const has_facebook = /facebook\.com\/(?!sharer|plugins|dialog|groups|pages\/create)([a-zA-Z0-9_\-\.]+)/i.test(html) ? 1 : 0;
    const has_linkedin = /linkedin\.com\/(?!share|shareArticle|static|legal|jobs|in\/)([a-zA-Z0-9_\-\.]+)/i.test(html) ? 1 : 0;

    // 2. Registrar chamada com sucesso
    logApiCall({
      provider: 'basic',
      serviceType: 'social',
      endpoint: websiteUrl,
      statusCode,
      responseTimeMs,
      success: true,
    });

    console.log(`[Basic Social Provider] Busca concluída para "${businessName}". Encontrados: Instagram=${has_instagram}, Facebook=${has_facebook}, LinkedIn=${has_linkedin}`);

    return {
      has_instagram,
      instagram_url,
      has_facebook,
      has_linkedin,
      social_last_post_days: null, // Scraper básico não obtém posts/tempo
    };

  } catch (error) {
    const responseTimeMs = Date.now() - startTime;
    console.error(`❌ [Basic Social Provider] Erro ao buscar HTML para "${businessName}":`, error.message);

    // Registrar erro em api_call_logs
    logApiCall({
      provider: 'basic',
      serviceType: 'social',
      endpoint: websiteUrl,
      statusCode,
      responseTimeMs,
      success: false,
      errorMessage: error.message,
    });

    // Em caso de falha real, não criamos dados mockados: retornamos presença zerada
    return {
      has_instagram: 0,
      instagram_url: null,
      has_facebook: 0,
      has_linkedin: 0,
      social_last_post_days: null,
    };
  }
}

module.exports = { analyzeSocialPresence };
