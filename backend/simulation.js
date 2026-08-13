require('dotenv').config({ path: './.env' });
const leadProvider = require('./src/providers/leads');
const aiProvider = require('./src/providers/ai');
const pagespeedProvider = require('./src/providers/pagespeed');

async function runSimulation() {
  console.log('=== SIMULAÇÃO: Clínica de Estética em São Paulo ===\n');

  try {
    // 1. Captura de Leads
    console.log('1. Captando Leads...');
    let leads = [];
    try {
        leads = await leadProvider.searchBusinesses('Clínica de Estética', 'São Paulo, SP');
        console.log(`Foram encontrados ${leads?.length || 0} leads.`);
    } catch (e) {
        console.log('Erro ao captar leads: ' + e.message);
    }
    
    if (!leads || leads.length === 0) {
      console.log('Usando um lead simulado para continuar o teste...');
      leads = [{
          name: 'Clínica de Estética Bela Pele',
          category: 'Clínica de Estética',
          website: 'https://example.com',
          google_rating: 4.5,
          google_reviews_count: 50
      }];
    }
    
    const targetLead = leads[0];
    console.log(`Lead selecionado: ${targetLead.name}`);
    console.log(`Website: ${targetLead.website}`);
    
    // 2. Triagem Digital (PageSpeed)
    let pageSpeedResult = { score: null };
    if (targetLead.website) {
      console.log('\n2. Rodando diagnóstico de PageSpeed...');
      try {
          pageSpeedResult = await pagespeedProvider.analyze(targetLead.website);
          console.log(`PageSpeed Score: ${pageSpeedResult.score}`);
      } catch (e) {
          console.log('Erro ao analisar PageSpeed: ' + e.message);
      }
    } else {
      console.log('\n2. Lead não possui website para testar PageSpeed.');
    }
    
    // 3. Diagnóstico e Recomendação (AI)
    console.log('\n3. Gerando Diagnóstico com IA...');
    try {
        const aiAnalysis = await aiProvider.generateDiagnostic(targetLead);
        console.log('\nResultado do Diagnóstico:');
        console.log(aiAnalysis);
        
        // 4. Criação do Site/Landing Page (AI / Stitch)
        console.log('\n4. Gerando Prompt para o Google Stitch...');
        const promptStitch = aiProvider.generateSitePrompt ? await aiProvider.generateSitePrompt(aiAnalysis) : "Funcionalidade de prompt para Stitch ainda não implementada no provider.";
        console.log(promptStitch);
    } catch (e) {
        console.log('Erro ao gerar diagnostico: ' + e.message);
    }
    
  } catch (err) {
    console.error('Erro geral durante a simulação:', err);
  }
}

runSimulation();
