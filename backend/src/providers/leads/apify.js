const { v4: uuidv4 } = require('uuid');
const config = require('../../config/env');
const db = require('../../config/database');
const mockProvider = require('./mock');

/**
 * Registra o log de chamada de API em api_call_logs
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
    console.error('❌ Falha ao registrar log de chamada da Apify API:', err);
  }
}

/**
 * Delay síncrono utilitário para polling
 */
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Busca negócios reais no Google Maps usando a Apify API
 * @param {string} niche - O nicho procurado (ex: "dental clinics")
 * @param {string} location - A cidade/região (ex: "Vancouver, BC")
 * @returns {Promise<Array>} Lista de leads
 */
async function searchBusinesses(niche, location, minRating, searchStatus, negativeKeywords) {
  if (!config.APIFY_API_KEY) {
    throw new Error('Chave de API do Apify (APIFY_API_KEY) não configurada no .env.');
  }

  const actorId = 'compass~crawler-google-places';
  const startEndpoint = `https://api.apify.com/v2/acts/${actorId}/runs?token=${config.APIFY_API_KEY}`;
  console.log(`[Apify Lead Provider] Iniciando Actor no Apify para "${niche}" em "${location}"...`);

  const startTime = Date.now();
  let runId = null;
  let datasetId = null;
  let statusCode = null;

  try {
    // 1. Iniciar o Actor
    const runResponse = await fetch(startEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        searchStringsArray: [niche],
        locationQuery: location,
        maxCrawledPlacesPerSearch: 10,
        language: 'en',
      }),
      signal: AbortSignal.timeout(20000), // timeout de 20s para inicialização
    });

    statusCode = runResponse.status;

    if (!runResponse.ok) {
      const errorText = await runResponse.text();
      throw new Error(`Erro ao iniciar Actor (Status ${runResponse.status}): ${errorText}`);
    }

    const runResult = await runResponse.json();
    runId = runResult.data?.id;
    datasetId = runResult.data?.defaultDatasetId;

    if (!runId || !datasetId) {
      throw new Error('Retorno inválido da API do Apify (runId ou datasetId ausentes)');
    }

    console.log(`[Apify Lead Provider] Actor iniciado. Run ID: ${runId}. Iniciando polling...`);

    // 2. Polling para esperar conclusão
    let finished = false;
    let attempts = 0;
    const maxAttempts = 30; // 30 tentativas * 5s = 150s (2.5 minutos) de limite

    while (!finished && attempts < maxAttempts) {
      attempts++;
      await delay(5000); // espera 5 segundos

      const statusEndpoint = `https://api.apify.com/v2/actor-runs/${runId}?token=${config.APIFY_API_KEY}`;
      const statusResponse = await fetch(statusEndpoint, { signal: AbortSignal.timeout(10000) });

      if (!statusResponse.ok) {
        console.warn(`[Apify Lead Provider] Falha ao verificar status do run ${runId} (Status ${statusResponse.status}). Continuando...`);
        continue;
      }

      const statusResult = await statusResponse.json();
      const status = statusResult.data?.status;

      console.log(`   -> Polling Apify (tentativa ${attempts}/${maxAttempts}): status atual = ${status}`);

      if (['SUCCEEDED', 'FAILED', 'TIMED-OUT', 'ABORTED'].includes(status)) {
        finished = true;
        if (status !== 'SUCCEEDED') {
          throw new Error(`O Actor no Apify terminou com status de falha: ${status}`);
        }
      }
    }

    if (!finished) {
      throw new Error('Limite de tempo atingido esperando pela conclusão do Actor no Apify');
    }

    // 3. Obter itens do Dataset
    const itemsEndpoint = `https://api.apify.com/v2/datasets/${datasetId}/items?token=${config.APIFY_API_KEY}`;
    console.log(`[Apify Lead Provider] Buscando itens do dataset ${datasetId}...`);

    const itemsResponse = await fetch(itemsEndpoint, { signal: AbortSignal.timeout(15000) });
    if (!itemsResponse.ok) {
      throw new Error(`Erro ao buscar itens do dataset (Status ${itemsResponse.status})`);
    }

    const items = await itemsResponse.json();
    const responseTimeMs = Date.now() - startTime;

    // Registrar chamada com sucesso
    logApiCall({
      provider: 'apify',
      serviceType: 'leads',
      endpoint: startEndpoint,
      statusCode,
      responseTimeMs,
      success: true,
    });

    console.log(`[Apify Lead Provider] Busca finalizada. ${items.length} itens extraídos.`);

    // 4. Mapear itens para o formato do banco do sistema
    const mappedItems = items.map((item) => {
      const google_rating = parseFloat(item.totalScore || item.rating || item.stars || '0');
      const google_reviews_count = parseInt(item.reviewsCount || item.reviews || '0', 10);
      
      let imageUrl = item.imageUrl || null;
      if (!imageUrl && item.imageUrls && item.imageUrls.length > 0) {
        imageUrl = item.imageUrls[0];
      }

      return {
        name: item.title || item.name || 'Empresa sem Nome',
        category: item.categoryName || item.subTitle || niche || 'Serviços',
        phone: item.phone || item.phoneUnformatted || null,
        website: item.website || null,
        address: item.address || null,
        city: location,
        google_rating: isNaN(google_rating) ? 0 : google_rating,
        google_reviews_count: isNaN(google_reviews_count) ? 0 : google_reviews_count,
        status: item.permanentlyClosed ? 'closed' : item.temporarilyClosed ? 'temporarily_closed' : 'open',
        image_url: imageUrl,
      };
    });

    // 5. Aplicar filtros locais
    return mappedItems.filter((item) => {
      // Filtro de status
      if (searchStatus === 'open' && item.status !== 'open') return false;

      // Filtro de nota
      if (minRating && item.google_rating < minRating && item.google_rating !== 0) return false;

      // Filtro de palavras negativas
      if (negativeKeywords && negativeKeywords.length > 0) {
        const titleLower = item.name.toLowerCase();
        const hasNegative = negativeKeywords.some((word) => titleLower.includes(word.toLowerCase()));
        if (hasNegative) return false;
      }

      return true;
    });

  } catch (error) {
    const responseTimeMs = Date.now() - startTime;
    console.error(`❌ [Apify Lead Provider] Erro no fluxo real do Apify:`, error.message);

    // Registrar falha
    logApiCall({
      provider: 'apify',
      serviceType: 'leads',
      endpoint: startEndpoint,
      statusCode,
      responseTimeMs,
      success: false,
      errorMessage: error.message,
    });

    throw error;
  }
}

module.exports = { searchBusinesses };
