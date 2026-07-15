const express = require('express');
const db = require('../config/database');

const router = express.Router();

/**
 * GET /api/campaigns/:campaignId/leads
 * Lista leads de uma campanha com filtros e ordenação
 * Query params:
 *   - priority: A, B ou C (filtra por prioridade)
 *   - search: busca parcial no nome
 *   - sort_by: campo para ordenação (dms, cos, google_rating, name, priority)
 *   - sort_order: ASC ou DESC (default: DESC)
 */
router.get('/campaigns/:campaignId/leads', async (req, res) => {
  const { campaignId } = req.params;
  const { priority, search, sort_by, sort_order } = req.query;

  // Verifica se a campanha existe
  const campaign = await db.prepare('SELECT id FROM campaigns WHERE id = ?').get(campaignId);
  if (!campaign) {
    return res.status(404).json({ error: 'not_found', message: 'Campanha não encontrada' });
  }

  // Monta query dinâmica com filtros
  let sql = 'SELECT * FROM leads WHERE campaign_id = ?';
  const params = [campaignId];

  if (priority) {
    sql += ' AND priority = ?';
    params.push(priority.toUpperCase());
  }

  if (search) {
    sql += ' AND name LIKE ?';
    params.push(`%${search}%`);
  }

  // Ordenação segura (whitelist de campos)
  const allowedSortFields = ['dms', 'cos', 'google_rating', 'name', 'priority', 'google_reviews_count', 'pagespeed_score', 'created_at'];
  const sortField = allowedSortFields.includes(sort_by) ? sort_by : 'cos';
  const order = sort_order?.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';
  sql += ` ORDER BY ${sortField} ${order}`;

  const leads = await db.prepare(sql).all(...params);

  res.json({ data: leads, total: leads.length });
});

/**
 * GET /api/leads/:id
 * Retorna detalhes completos de um lead específico
 */
router.get('/leads/:id', async (req, res) => {
  const lead = await db.prepare('SELECT * FROM leads WHERE id = ?').get(req.params.id);

  if (!lead) {
    return res.status(404).json({ error: 'not_found', message: 'Lead não encontrado' });
  }

  // Busca diagnóstico associado, se existir
  const diagnostic = await db.prepare('SELECT * FROM diagnostics WHERE lead_id = ?').get(req.params.id);

  res.json({ data: { ...lead, diagnostic: diagnostic || null } });
});

/**
 * GET /api/campaigns/:campaignId/leads/export
 * Exporta leads da campanha em formato CSV
 */
router.get('/campaigns/:campaignId/leads/export', async (req, res) => {
  const { campaignId } = req.params;

  const campaign = await db.prepare('SELECT * FROM campaigns WHERE id = ?').get(campaignId);
  if (!campaign) {
    return res.status(404).json({ error: 'not_found', message: 'Campanha não encontrada' });
  }

  const leads = await db.prepare(`
    SELECT * FROM leads WHERE campaign_id = ? ORDER BY cos DESC
  `).all(campaignId);

  // Cabeçalho CSV
  const headers = [
    'Nome', 'Categoria', 'Telefone', 'Website', 'Endereço', 'Cidade',
    'Rating Google', 'Avaliações Google', 'Tem Site',
    'PageSpeed', 'LCP (ms)', 'INP (ms)', 'CLS',
    'Instagram', 'Facebook', 'Último Post (dias)',
    'DMS', 'COS', 'Prioridade',
  ];

  const rows = leads.map(lead => [
    `"${(lead.name || '').replace(/"/g, '""')}"`,
    `"${(lead.category || '').replace(/"/g, '""')}"`,
    `"${lead.phone || ''}"`,
    `"${lead.website || ''}"`,
    `"${(lead.address || '').replace(/"/g, '""')}"`,
    `"${(lead.city || '').replace(/"/g, '""')}"`,
    lead.google_rating || '',
    lead.google_reviews_count || 0,
    lead.has_website ? 'Sim' : 'Não',
    lead.pagespeed_score || '',
    lead.lcp_ms || '',
    lead.inp_ms || '',
    lead.cls || '',
    lead.has_instagram ? 'Sim' : 'Não',
    lead.has_facebook ? 'Sim' : 'Não',
    lead.social_last_post_days ?? '',
    lead.dms,
    lead.cos,
    lead.priority,
  ]);

  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');

  // BOM para UTF-8 em Excel
  const bom = '\uFEFF';

  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', `attachment; filename="leads_${campaignId}.csv"`);
  res.send(bom + csv);
});

module.exports = router;
