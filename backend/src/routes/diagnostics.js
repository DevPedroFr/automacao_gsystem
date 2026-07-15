const express = require('express');
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database');
const { generateDiagnostic } = require('../services/aiService');
const { triggerWebhook } = require('../services/webhookService');

const router = express.Router();

/**
 * POST /api/leads/:leadId/diagnostic
 * Gera um diagnóstico via aiService e salva no banco
 * Se já existe um diagnóstico para o lead, retorna erro
 */
router.post('/leads/:leadId/diagnostic', async (req, res, next) => {
  try {
    const { leadId } = req.params;

    // Verifica se o lead existe
    const lead = await db.prepare('SELECT * FROM leads WHERE id = ?').get(leadId);
    if (!lead) {
      return res.status(404).json({ error: 'not_found', message: 'Lead não encontrado' });
    }

    // Verifica se já existe um diagnóstico
    const existing = await db.prepare('SELECT id, diagnostic_status FROM diagnostics WHERE lead_id = ?').get(leadId);
    if (existing) {
      if (existing.diagnostic_status === 'ai_validation_failed') {
        // Se falhou anteriormente, remove o registro para permitir re-geração
        await db.prepare('DELETE FROM diagnostics WHERE id = ?').run(existing.id);
      } else {
        return res.status(409).json({
          error: 'already_exists',
          message: 'Diagnóstico já gerado para este lead. Use GET para consultá-lo.',
        });
      }
    }

    // Gera o diagnóstico via IA (Gemini ou Mock)
    const diagnostic = await generateDiagnostic(lead);

    const id = uuidv4();

    await db.prepare(`
      INSERT INTO diagnostics (
        id, lead_id, observed_facts, inferences, recommendations, 
        email_draft, whatsapp_draft, instagram_draft, stitch_prompt, 
        diagnostic_status, error_message
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      id,
      leadId,
      diagnostic.observed_facts || null,
      diagnostic.inferences || null,
      diagnostic.recommendations || null,
      diagnostic.email_draft || null,
      diagnostic.whatsapp_draft || null,
      diagnostic.instagram_draft || null,
      diagnostic.stitch_prompt || null,
      diagnostic.diagnostic_status || 'completed',
      diagnostic.error_message || null
    );

    const saved = await db.prepare('SELECT * FROM diagnostics WHERE id = ?').get(id);

    // Dispara webhook informando o resultado da geração do diagnóstico
    try {
      if (saved && saved.diagnostic_status !== 'ai_validation_failed') {
        await triggerWebhook('diagnostic_generated', {
          lead: lead,
          diagnostic: saved
        });
      } else if (saved && saved.diagnostic_status === 'ai_validation_failed') {
        await triggerWebhook('diagnostic_failed', {
          lead: lead,
          error: saved.error_message
        });
      }
    } catch (webErr) {
      console.error('⚠️ Falha ao disparar webhook de diagnóstico:', webErr.message);
    }

    res.status(201).json({ data: saved });

  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/leads/:leadId/diagnostic
 * Retorna o diagnóstico existente de um lead
 */
router.get('/leads/:leadId/diagnostic', async (req, res) => {
  const { leadId } = req.params;

  // Verifica se o lead existe
  const lead = await db.prepare('SELECT id FROM leads WHERE id = ?').get(leadId);
  if (!lead) {
    return res.status(404).json({ error: 'not_found', message: 'Lead não encontrado' });
  }

  const diagnostic = await db.prepare('SELECT * FROM diagnostics WHERE lead_id = ?').get(leadId);

  if (!diagnostic) {
    return res.status(404).json({
      error: 'not_found',
      message: 'Diagnóstico ainda não gerado para este lead. Use POST para gerar.',
    });
  }

  res.json({ data: diagnostic });
});

module.exports = router;
