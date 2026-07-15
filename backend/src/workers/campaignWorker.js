const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');
const config = require('../config/env');
const { searchBusinesses } = require('../services/apifyService');
const { analyzeWebsite } = require('../services/pagespeedService');
const { analyzeSocialPresence } = require('../services/socialService');
const { fetchOgImage } = require('../services/imageService');
const { calculateDMS, calculateCOS, getPriority } = require('../services/scoreService');
const { triggerWebhook } = require('../services/webhookService');

/**
 * Campaign Worker — Processa uma campanha de prospecção de forma assíncrona
 * Busca negócios, analisa presença digital, calcula scores e salva leads no banco.
 */

/**
 * Processa uma campanha completa
 * @param {string} campaignId - ID da campanha
 * @param {string} niche - Nicho de mercado
 * @param {string} location - Localização para busca
 * @param {number} minRating - Nota mínima
 * @param {string} searchStatus - Status (open/all)
 * @param {string[]} negativeKeywords - Palavras-chave negativas
 */
async function processCampaign(campaignId, niche, location, minRating, searchStatus, negativeKeywords) {
  try {
    console.log(`\n🔄 Processando campanha ${campaignId}...`);
    console.log(`   Nicho: ${niche} | Local: ${location} | Rating: ${minRating}+ | Status: ${searchStatus}`);

    // 1. Buscar negócios via Apify (mock ou real)
    const businesses = await searchBusinesses(niche, location, minRating, searchStatus, negativeKeywords);
    console.log(`   📍 ${businesses.length} negócios encontrados`);

    // Prepared statement para inserção de leads
    const insertLead = await db.prepare(`
      INSERT INTO leads (
        id, campaign_id, name, category, phone, website, address, city,
        google_rating, google_reviews_count, has_website,
        pagespeed_score, lcp_ms, inp_ms, cls, seo_score,
        has_instagram, instagram_url, has_facebook, has_linkedin, social_last_post_days,
        dms, cos, priority, commercial_status, source_provider, raw_data_path, image_url
      ) VALUES (
        @id, @campaign_id, @name, @category, @phone, @website, @address, @city,
        @google_rating, @google_reviews_count, @has_website,
        @pagespeed_score, @lcp_ms, @inp_ms, @cls, @seo_score,
        @has_instagram, @instagram_url, @has_facebook, @has_linkedin, @social_last_post_days,
        @dms, @cos, @priority, @commercial_status, @source_provider, @raw_data_path, @image_url
      )
    `);

    // 2. Processar negócios em paralelo com atraso escalonado (para respeitar rate limits de API)
    const processPromises = businesses.map(async (biz, index) => {
      // Atraso escalonado de 1.5s por item para não disparar chamadas simultâneas exatas
      await delay(index * 1500);

      // 2a. Analisar website
      const hasWebsite = biz.website != null;
      let webMetrics = null;
      if (hasWebsite) {
        try {
          webMetrics = await analyzeWebsite(biz.website);
        } catch (webErr) {
          console.error(`⚠️ Falha ao analisar website para ${biz.name}:`, webErr.message);
          // webMetrics permanece null, gravando nulos sem travar o processamento
        }
      }

      // 2b. Analisar presença social
      let socialData = { has_instagram: 0, instagram_url: null, has_facebook: 0, has_linkedin: 0, social_last_post_days: null };
      try {
        socialData = await analyzeSocialPresence(biz.name, biz.website);
      } catch (socialErr) {
        console.error(`⚠️ Falha ao analisar presença social para ${biz.name}:`, socialErr.message);
        // socialData permanece com valores zerados por padrão
      }

      // 2b-2. Tentar extrair a foto real (og:image) do site se ele existir
      let siteOgImage = null;
      if (hasWebsite) {
        siteOgImage = await fetchOgImage(biz.website);
        if (siteOgImage) {
          console.log(`   📸 [OG:Image] Foto original encontrada no site de ${biz.name}`);
        }
      }

      // 2c. Montar dados do lead
      const leadData = {
        ...biz,
        has_website: hasWebsite,
        pagespeed_score: webMetrics?.pagespeed_score || null,
        lcp_ms: webMetrics?.lcp_ms || null,
        inp_ms: webMetrics?.inp_ms || null,
        cls: webMetrics?.cls || null,
        seo_score: webMetrics?.seo_score || null,
        image_url: siteOgImage || biz.image_url || null, // Prioriza foto do site > Google Maps
        ...socialData,
      };

      // 2d. Calcular scores
      const dms = calculateDMS(leadData);
      const cos = calculateCOS(leadData, dms);
      const priority = getPriority(cos);

      // 2e. Inserir no banco
      insertLead.run({
        id: uuidv4(),
        campaign_id: campaignId,
        name: biz.name,
        category: biz.category,
        phone: biz.phone,
        website: biz.website,
        address: biz.address,
        city: biz.city,
        google_rating: biz.google_rating,
        google_reviews_count: biz.google_reviews_count,
        has_website: hasWebsite ? 1 : 0,
        pagespeed_score: webMetrics?.pagespeed_score || null,
        lcp_ms: webMetrics?.lcp_ms || null,
        inp_ms: webMetrics?.inp_ms || null,
        cls: webMetrics?.cls || null,
        seo_score: webMetrics?.seo_score || null,
        has_instagram: socialData.has_instagram,
        instagram_url: socialData.instagram_url || null,
        has_facebook: socialData.has_facebook,
        has_linkedin: socialData.has_linkedin || 0,
        social_last_post_days: socialData.social_last_post_days,
        dms,
        cos,
        priority,
        commercial_status: 'new',
        source_provider: config.LEAD_PROVIDER,
        raw_data_path: webMetrics?.raw_data_path || null,
        image_url: leadData.image_url,
      });

      console.log(`   ✅ [${index + 1}/${businesses.length}] ${biz.name} — DMS: ${dms} | COS: ${cos} | ${priority}`);
    });

    // Aguarda o término de todas as promessas de leads
    await Promise.all(processPromises);

    // 3. Atualizar campanha como concluída
    db.prepare(`
      UPDATE campaigns 
      SET status = 'completed', total_leads = ?, updated_at = CURRENT_TIMESTAMP 
      WHERE id = ?
    `).run(businesses.length, campaignId);

    console.log(`\n🎉 Campanha ${campaignId} concluída! ${businesses.length} leads processados.\n`);

    // Dispara o webhook de sucesso em background
    try {
      const campaignData = await db.prepare('SELECT * FROM campaigns WHERE id = ?').get(campaignId);
      const campaignLeads = await db.prepare('SELECT * FROM leads WHERE campaign_id = ?').all(campaignId);
      await triggerWebhook('campaign_completed', {
        campaign: campaignData,
        leads: campaignLeads
      });
    } catch (webErr) {
      console.error('⚠️ Falha ao coletar dados para webhook campaign_completed:', webErr.message);
    }

  } catch (error) {
    console.error(`❌ Erro ao processar campanha ${campaignId}:`, error);

    // Marca a campanha como falha e grava a mensagem de erro real
    await db.prepare(`
      UPDATE campaigns 
      SET status = 'failed', error_message = ?, updated_at = CURRENT_TIMESTAMP 
      WHERE id = ?
    `).run(error.message, campaignId);

    // Dispara o webhook de falha
    try {
      const failedCampaign = await db.prepare('SELECT * FROM campaigns WHERE id = ?').get(campaignId);
      await triggerWebhook('campaign_failed', {
        campaign: failedCampaign,
        error: error.message
      });
    } catch (webErr) {
      console.error('⚠️ Falha ao disparar webhook campaign_failed:', webErr.message);
    }
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { processCampaign };
