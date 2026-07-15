const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const config = require('../../config/env');
const db = require('../../config/database');
const mockProvider = require('./mock');

// Garante que o diretório de dados brutos existe
const rawDir = path.join(__dirname, '..', '..', '..', 'data', 'raw', 'pagespeed');
if (!fs.existsSync(rawDir)) {
  fs.mkdirSync(rawDir, { recursive: true });
}

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
 * Analisa a performance de um site usando a Google PageSpeed Insights API
 * @param {string} url - URL do site
 * @returns {Promise<Object>} Resultado da análise
 */
async function analyzeWebsite(url) {
  if (!url) return null;

  const endpointBase = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed';
  const queryParams = new URLSearchParams({
    url: url,
    strategy: 'mobile',
    // Limita as auditorias apenas a performance e SEO para otimizar velocidade
    category: 'performance',
  });
  // Adiciona SEO se necessário, ou por padrão a API já traz se não filtrado.
  // Vamos filtrar apenas para 'performance' e 'seo'
  queryParams.append('category', 'seo');

  if (config.PAGESPEED_API_KEY) {
    queryParams.set('key', config.PAGESPEED_API_KEY);
  }

  const fullUrl = `${endpointBase}?${queryParams.toString()}`;
  console.log(`[Google PageSpeed Provider] Chamando API real para "${url}"...`);

  const startTime = Date.now();
  let statusCode = null;
  let responseData = null;

  try {
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      // Timeout seguro de 40 segundos
      signal: AbortSignal.timeout(40000),
    });

    statusCode = response.status;
    const responseTimeMs = Date.now() - startTime;

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Erro na API (Status ${response.status}): ${errorText}`);
    }

    responseData = await response.json();

    // 1. Extrair métricas
    const lighthouse = responseData.lighthouseResult || {};
    const performanceCategory = lighthouse.categories?.performance || {};
    const seoCategory = lighthouse.categories?.seo || {};
    const audits = lighthouse.audits || {};

    const pagespeed_score = performanceCategory.score !== undefined ? Math.round(performanceCategory.score * 100) : null;
    const seo_score = seoCategory.score !== undefined ? Math.round(seoCategory.score * 100) : null;
    const lcp_ms = audits['largest-contentful-paint']?.numericValue ? Math.round(audits['largest-contentful-paint'].numericValue) : null;
    const inp_ms = audits['interaction-to-next-paint']?.numericValue ? Math.round(audits['interaction-to-next-paint'].numericValue) : 100; // default safe
    const cls = audits['cumulative-layout-shift']?.numericValue !== undefined ? parseFloat(audits['cumulative-layout-shift'].numericValue.toFixed(2)) : null;

    // 2. Salvar JSON bruto em disco
    const rawFileName = `${uuidv4()}.json`;
    const rawFilePath = path.join(rawDir, rawFileName);
    fs.writeFileSync(rawFilePath, JSON.stringify(responseData, null, 2));
    const raw_data_path = path.join('data', 'raw', 'pagespeed', rawFileName);

    // 3. Registrar chamada com sucesso
    logApiCall({
      provider: 'google',
      serviceType: 'pagespeed',
      endpoint: endpointBase,
      statusCode,
      responseTimeMs,
      success: true,
    });

    console.log(`[Google PageSpeed Provider] Análise concluída com sucesso para "${url}". Score: ${pagespeed_score}/100`);

    return {
      pagespeed_score,
      lcp_ms,
      inp_ms,
      cls,
      seo_score,
      raw_data_path,
    };

  } catch (error) {
    const responseTimeMs = Date.now() - startTime;
    console.error(`❌ [Google PageSpeed Provider] Erro na requisição para "${url}":`, error.message);

    // Registrar erro em api_call_logs
    logApiCall({
      provider: 'google',
      serviceType: 'pagespeed',
      endpoint: endpointBase,
      statusCode,
      responseTimeMs,
      success: false,
      errorMessage: error.message,
    });

    throw error;
  }
}

module.exports = { analyzeWebsite };
