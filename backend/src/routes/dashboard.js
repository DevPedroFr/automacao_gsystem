const express = require('express');
const db = require('../config/database');

const router = express.Router();

/**
 * GET /api/dashboard/stats
 * Retorna dados estatísticos globais e consumo de APIs
 */
router.get('/stats', async (req, res) => {
  try {
    // 1. Leads totais
    const totalLeads = await db.prepare('SELECT COUNT(*) as count FROM leads').get().count;

    // 2. Média DMS geral
    const avgDmsRes = await db.prepare('SELECT AVG(dms) as avg FROM leads WHERE dms IS NOT NULL').get();
    const avgDms = avgDmsRes.avg ? Math.round(avgDmsRes.avg) : 0;

    // 3. Campanhas ativas (em processamento)
    const activeCampaigns = await db.prepare("SELECT COUNT(*) as count FROM campaigns WHERE status = 'processing'").get().count;

    // 4. Total de Diagnósticos finalizados com sucesso
    const totalDiagnostics = await db.prepare("SELECT COUNT(*) as count FROM diagnostics WHERE diagnostic_status = 'completed'").get().count;

    // 5. Distribuição global de prioridades (A/B/C)
    const priorityCounts = await db.prepare("SELECT priority, COUNT(*) as count FROM leads GROUP BY priority").all();
    const priorityMap = { A: 0, B: 0, C: 0 };
    for (const row of priorityCounts) {
      if (row.priority in priorityMap) {
        priorityMap[row.priority] = row.count;
      }
    }

    // 6. Consumo do Apify no mês atual (pesquisas)
    const apifyUsage = await db.prepare(`
      SELECT COUNT(*) as count 
      FROM api_call_logs 
      WHERE provider = 'apify' 
        AND success = 1 
        AND created_at >= date_trunc('month', CURRENT_DATE)
    `).get().count;

    // 7. Consumo do Gemini no dia atual
    const geminiUsage = await db.prepare(`
      SELECT COUNT(*) as count 
      FROM api_call_logs 
      WHERE provider = 'gemini' 
        AND success = 1 
        AND created_at >= CURRENT_DATE
    `).get().count;

    // 8. Consumo do Google PageSpeed no dia atual
    const pagespeedUsage = await db.prepare(`
      SELECT COUNT(*) as count 
      FROM api_call_logs 
      WHERE provider = 'google' 
        AND service_type = 'pagespeed' 
        AND success = 1 
        AND created_at >= CURRENT_DATE
    `).get().count;

    res.json({
      success: true,
      data: {
        totalLeads,
        avgDms,
        activeCampaigns,
        totalDiagnostics,
        priorityDistribution: [
          { name: 'Prioridade A', value: priorityMap.A, color: '#22C55E' },
          { name: 'Prioridade B', value: priorityMap.B, color: '#F59E0B' },
          { name: 'Prioridade C', value: priorityMap.C, color: '#EF4444' },
        ].filter(d => d.value > 0),
        apiUsage: {
          apify: {
            used: apifyUsage,
            limit: 50, // Estimativa do plano gratuito ($5/mês)
            unit: 'pesquisas'
          },
          gemini: {
            used: geminiUsage,
            limit: 1500, // Limite diário do plano gratuito do Gemini 2.5/2.0 Flash
            unit: 'requisições'
          },
          pagespeed: {
            used: pagespeedUsage,
            limit: 25000, // Limite diário gratuito da PageSpeed API
            unit: 'auditorias'
          }
        }
      }
    });
  } catch (err) {
    console.error('❌ Erro ao calcular estatísticas do dashboard:', err);
    res.status(500).json({ error: 'internal_error', message: err.message });
  }
});

module.exports = router;
