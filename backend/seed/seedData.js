/**
 * Seed Script — Popula o banco de dados com dados de demonstração
 * Uso: node seed/seedData.js
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const { v4: uuidv4 } = require('uuid');
const db = require('../src/config/database');
const { searchBusinesses } = require('../src/services/apifyService');
const { analyzeWebsite } = require('../src/services/pagespeedService');
const { analyzeSocialPresence } = require('../src/services/socialService');
const { calculateDMS, calculateCOS, getPriority } = require('../src/services/scoreService');
const { generateDiagnostic } = require('../src/services/aiService');

async function seed() {
  console.log('\n🌱 ═══════════════════════════════════════');
  console.log('   CONSULTINGS APD — Seed de Dados');
  console.log('═══════════════════════════════════════\n');

  // Aguarda banco inicializar (sql.js é assíncrono)
  await db.ready();

  // 1. Limpar todas as tabelas
  console.log('🗑️  Limpando tabelas...');
  db.exec('DELETE FROM diagnostics');
  db.exec('DELETE FROM leads');
  db.exec('DELETE FROM campaigns');
  console.log('   ✅ Tabelas limpas\n');

  // 2. Definir campanhas de demonstração
  const campaignsData = [
    { niche: 'Clínicas Odontológicas', location: 'Curitiba, PR', status: 'completed', generateLeads: true },
    { niche: 'Imobiliárias', location: 'São Paulo, SP', status: 'completed', generateLeads: true },
    { niche: 'Restaurantes', location: 'Florianópolis, SC', status: 'processing', generateLeads: false },
  ];

  const insertCampaign = db.prepare(`
    INSERT INTO campaigns (id, niche, location, status, total_leads, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, datetime('now', ?), datetime('now'))
  `);

  const insertLead = db.prepare(`
    INSERT INTO leads (
      id, campaign_id, name, category, phone, website, address, city,
      google_rating, google_reviews_count, has_website,
      pagespeed_score, lcp_ms, inp_ms, cls,
      has_instagram, has_facebook, has_linkedin, social_last_post_days,
      dms, cos, priority, commercial_status, source_provider, raw_data_path
    ) VALUES (
      @id, @campaign_id, @name, @category, @phone, @website, @address, @city,
      @google_rating, @google_reviews_count, @has_website,
      @pagespeed_score, @lcp_ms, @inp_ms, @cls,
      @has_instagram, @has_facebook, @has_linkedin, @social_last_post_days,
      @dms, @cos, @priority, @commercial_status, @source_provider, @raw_data_path
    )
  `);

  const insertDiagnostic = db.prepare(`
    INSERT INTO diagnostics (id, lead_id, observed_facts, inferences, recommendations, email_draft, diagnostic_status)
    VALUES (?, ?, ?, ?, ?, ?, 'completed')
  `);

  let totalLeadsCreated = 0;
  let totalDiagnosticsCreated = 0;

  for (let i = 0; i < campaignsData.length; i++) {
    const campData = campaignsData[i];
    const campaignId = uuidv4();

    console.log(`📋 Campanha ${i + 1}: "${campData.niche}" em ${campData.location}`);

    if (!campData.generateLeads) {
      // Campanha em processamento, sem leads
      insertCampaign.run(campaignId, campData.niche, campData.location, campData.status, 0, `-${(campaignsData.length - i) * 2} hours`);
      console.log(`   Status: ${campData.status} | Leads: 0\n`);
      continue;
    }

    // Gerar leads para esta campanha
    const businesses = await searchBusinesses(campData.niche, campData.location);

    // Limitar a quantidade desejada
    const targetCount = i === 0 ? 12 : 10;
    const selectedBusinesses = businesses.slice(0, targetCount);

    // Adicionar leads de alta oportunidade (Prioridade A) manualmente
    // São empresas com boa reputação local MAS sem presença digital
    const highOpportunityLeads = [
      {
        name: i === 0 ? 'Dr. Mendonça Implantodontia' : 'Imobiliária Raízes',
        category: campData.niche,
        phone: '(41) 99876-5432',
        website: null,  // SEM site
        address: 'Rua XV de Novembro, 1200',
        city: campData.location,
        google_rating: 4.8,
        google_reviews_count: 280,
      },
      {
        name: i === 0 ? 'Espaço Oral Premium' : 'Grupo Morada Consultoria',
        category: campData.niche,
        phone: '(41) 93456-7890',
        website: null,  // SEM site
        address: 'Av. Brasil, 450',
        city: campData.location,
        google_rating: 4.5,
        google_reviews_count: 150,
      },
      {
        name: i === 0 ? 'OdontoMax Centro' : 'Portal Horizonte SP',
        category: campData.niche,
        phone: '(41) 91234-5678',
        website: null,  // SEM site
        address: 'Rua Marechal Deodoro, 890',
        city: campData.location,
        google_rating: 4.2,
        google_reviews_count: 95,
      },
    ];
    selectedBusinesses.push(...highOpportunityLeads);

    let leadCount = 0;
    const leadsForDiagnostic = [];

    for (const biz of selectedBusinesses) {
      const hasWebsite = biz.website != null;
      const webMetrics = await analyzeWebsite(biz.website);

      // Para leads de alta oportunidade (sem site, alta nota), forçar sem redes sociais
      const isHighOpp = highOpportunityLeads.some(h => h.name === biz.name);
      const socialData = isHighOpp
        ? { has_instagram: 0, has_facebook: 0, social_last_post_days: null }
        : await analyzeSocialPresence(biz.name, biz.website);

      const leadData = {
        ...biz,
        has_website: hasWebsite,
        pagespeed_score: webMetrics?.pagespeed_score || null,
        lcp_ms: webMetrics?.lcp_ms || null,
        inp_ms: webMetrics?.inp_ms || null,
        cls: webMetrics?.cls || null,
        ...socialData,
      };

      const dms = calculateDMS(leadData);
      const cos = calculateCOS(leadData, dms);
      const priority = getPriority(cos);

      const leadId = uuidv4();

      insertLead.run({
        id: leadId,
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
        has_instagram: socialData.has_instagram,
        has_facebook: socialData.has_facebook,
        has_linkedin: socialData.has_linkedin || 0,
        social_last_post_days: socialData.social_last_post_days,
        dms,
        cos,
        priority,
        commercial_status: 'new',
        source_provider: 'mock',
        raw_data_path: null,
      });

      leadCount++;

      // Guarda leads de prioridade A para gerar diagnóstico
      if (priority === 'A') {
        leadsForDiagnostic.push({
          id: leadId,
          ...leadData,
          dms,
          cos,
          priority,
        });
      }

      console.log(`   ✅ ${biz.name} — DMS: ${dms} | COS: ${cos} | ${priority}`);
    }

    // Inserir campanha com total correto
    insertCampaign.run(campaignId, campData.niche, campData.location, campData.status, leadCount, `-${(campaignsData.length - i) * 24} hours`);

    totalLeadsCreated += leadCount;
    console.log(`   📊 ${leadCount} leads criados`);

    // Gerar diagnósticos para leads prioridade A
    if (leadsForDiagnostic.length > 0) {
      console.log(`   🤖 Gerando diagnósticos para ${leadsForDiagnostic.length} leads prioridade A...`);

      for (const lead of leadsForDiagnostic) {
        const diagnostic = await generateDiagnostic(lead);
        insertDiagnostic.run(
          uuidv4(),
          lead.id,
          diagnostic.observed_facts,
          diagnostic.inferences,
          diagnostic.recommendations,
          diagnostic.email_draft,
        );
        totalDiagnosticsCreated++;
        console.log(`      📝 Diagnóstico gerado para: ${lead.name}`);
      }
    }

    console.log('');
  }

  // 3. Resumo final
  console.log('═══════════════════════════════════════');
  console.log('📊 RESUMO DO SEED:');
  console.log(`   • Campanhas criadas: ${campaignsData.length}`);
  console.log(`   • Leads criados: ${totalLeadsCreated}`);
  console.log(`   • Diagnósticos gerados: ${totalDiagnosticsCreated}`);
  console.log('═══════════════════════════════════════\n');

  // Estatísticas extras
  const stats = db.prepare(`
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN priority = 'A' THEN 1 ELSE 0 END) as prio_a,
      SUM(CASE WHEN priority = 'B' THEN 1 ELSE 0 END) as prio_b,
      SUM(CASE WHEN priority = 'C' THEN 1 ELSE 0 END) as prio_c,
      ROUND(AVG(dms), 1) as avg_dms,
      ROUND(AVG(cos), 1) as avg_cos
    FROM leads
  `).get();

  console.log('📈 DISTRIBUIÇÃO DE LEADS:');
  console.log(`   • Prioridade A: ${stats.prio_a} leads`);
  console.log(`   • Prioridade B: ${stats.prio_b} leads`);
  console.log(`   • Prioridade C: ${stats.prio_c} leads`);
  console.log(`   • DMS médio: ${stats.avg_dms}`);
  console.log(`   • COS médio: ${stats.avg_cos}`);
  console.log('\n✅ Seed concluído com sucesso!\n');
}

seed().catch(err => {
  console.error('❌ Erro no seed:', err);
  process.exit(1);
});
