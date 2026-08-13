require('dotenv').config({ path: './backend/.env' });
const leadProvider = require('./backend/src/providers/leads');
const aiProvider = require('./backend/src/providers/ai');
const pagespeedProvider = require('./backend/src/providers/pagespeed');

async function runSimulation() {
  console.log('=== SIMULAÇÃO: Clínica de Estética em São Paulo ===\n');

  try {
    // 1. Captura de Leads
    console.log('1. Captando Leads...');
    const leads = await leadProvider.searchLeads({ keyword: 'Clínica de Estética', location: 'São Paulo, SP' });
    console.log(`Foram encontrados ${leads.length} leads.`);
    
    if (leads.length === 0) {
      console.log('Nenhum lead encontrado pelo provider atual.');
      return;
    }
    
    const targetLead = leads[0];
    console.log(`Lead selecionado: ${targetLead.name}`);
    console.log(`Website: ${targetLead.website}`);
    
    // 2. Triagem Digital (PageSpeed)
    let pageSpeedResult = { score: null };
    if (targetLead.website) {
      console.log('\n2. Rodando diagnóstico de PageSpeed...');
      pageSpeedResult = await pagespeedProvider.analyze(targetLead.website);
      console.log(`PageSpeed Score: ${pageSpeedResult.score}`);
    } else {
      console.log('\n2. Lead não possui website para testar PageSpeed.');
    }
    
    // 3. Diagnóstico e Recomendação (AI)
    console.log('\n3. Gerando Diagnóstico com IA...');
    const aiAnalysis = await aiProvider.generateDiagnostic(targetLead);
    console.log('\nResultado do Diagnóstico:');
    console.log(aiAnalysis);
    
    // 4. Criação do Site/Landing Page (AI / Stitch - mockado se não houver no código)
    console.log('\n4. Gerando Prompt para o Google Stitch...');
    // Se não tiver função pronta, vamos mockar a intenção
    const promptStitch = await aiProvider.generateSitePrompt ? await aiProvider.generateSitePrompt(aiAnalysis) : "Funcionalidade de prompt para Stitch ainda não implementada no provider.";
    console.log(promptStitch);
    
  } catch (err) {
    console.error('Erro durante a simulação:', err);
  }
}

runSimulation();
