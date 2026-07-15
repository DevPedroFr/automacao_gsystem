const express = require('express');
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');
const { processCampaign } = require('../workers/campaignWorker');

const router = express.Router();

/**
 * GET /api/campaigns
 * Lista todas as campanhas, ordenadas por data de criação (mais recente primeiro)
 */
router.get('/', async (req, res) => {
  const campaigns = await db.prepare(`
    SELECT * FROM campaigns ORDER BY created_at DESC
  `).all();

  res.json({ data: campaigns });
});

/**
 * GET /api/campaigns/:id
 * Retorna detalhes de uma campanha específica
 */
router.get('/:id', async (req, res) => {
  const campaign = await db.prepare(`
    SELECT * FROM campaigns WHERE id = ?
  `).get(req.params.id);

  if (!campaign) {
    return res.status(404).json({ error: 'not_found', message: 'Campanha não encontrada' });
  }

  res.json({ data: campaign });
});

/**
 * POST /api/campaigns
 * Cria uma nova campanha e dispara processamento assíncrono
 * Body: { niche: string, location: string }
 */
router.post('/', async (req, res) => {
  const { niche, location, minRating, status, negativeKeywords } = req.body;

  if (!niche || !location) {
    return res.status(400).json({
      error: 'validation_error',
      message: 'Os campos "niche" e "location" são obrigatórios',
    });
  }

  const id = uuidv4();

  // Passamos temporariamente na string 'status' apenas, ou você pode ignorá-los na tabela por enquanto e só passar pro worker
  await db.prepare(`
    INSERT INTO campaigns (id, niche, location, status, total_leads)
    VALUES (?, ?, ?, 'processing', 0)
  `).run(id, niche, location);

  const campaign = await db.prepare('SELECT * FROM campaigns WHERE id = ?').get(id);

  // Dispara processamento assíncrono (não bloqueia a resposta)
  setTimeout(() => {
    processCampaign(id, niche, location, minRating, status, negativeKeywords);
  }, 0);

  res.status(201).json({ data: campaign });
});

/**
 * GET /api/campaigns/:id/stats
 * Retorna estatísticas da campanha: totais, contagem por prioridade, médias de score
 */
router.get('/:id/stats', async (req, res) => {
  const campaign = await db.prepare('SELECT * FROM campaigns WHERE id = ?').get(req.params.id);

  if (!campaign) {
    return res.status(404).json({ error: 'not_found', message: 'Campanha não encontrada' });
  }

  const totalLeads = await db.prepare(`
    SELECT COUNT(*) as count FROM leads WHERE campaign_id = ?
  `).get(req.params.id).count;

  const priorityCounts = await db.prepare(`
    SELECT 
      priority,
      COUNT(*) as count
    FROM leads 
    WHERE campaign_id = ?
    GROUP BY priority
  `).all(req.params.id);

  const priorityMap = { A: 0, B: 0, C: 0 };
  for (const row of priorityCounts) {
    priorityMap[row.priority] = row.count;
  }

  const averages = await db.prepare(`
    SELECT 
      ROUND(AVG(dms), 1) as avg_dms,
      ROUND(AVG(cos), 1) as avg_cos
    FROM leads 
    WHERE campaign_id = ?
  `).get(req.params.id);

  res.json({
    data: {
      campaign_id: req.params.id,
      status: campaign.status,
      total_leads: totalLeads,
      priority_a: priorityMap.A,
      priority_b: priorityMap.B,
      priority_c: priorityMap.C,
      avg_dms: averages.avg_dms || 0,
      avg_cos: averages.avg_cos || 0,
    },
  });
});

module.exports = router;
