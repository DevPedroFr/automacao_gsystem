const express = require('express');
const { deployToVercel } = require('../services/vercelService');
const db = require('../config/database');

const router = express.Router();

/**
 * Rota para fazer deploy de arquivos para a Vercel
 * Espera receber:
 * {
 *   "leadId": "id-do-lead",
 *   "files": [
 *     { "file": "index.html", "data": "..." },
 *     ...
 *   ]
 * }
 */
router.post('/', async (req, res) => {
  try {
    const { leadId, files } = req.body;

    if (!leadId) {
      return res.status(400).json({ error: 'leadId é obrigatório' });
    }

    if (!files || !Array.isArray(files) || files.length === 0) {
      return res.status(400).json({ error: 'Lista de arquivos (files) é obrigatória' });
    }

    // 1. Buscar o lead para compor o nome do projeto
    const stmt = await db.prepare('SELECT name FROM leads WHERE id = ?');
    const lead = stmt.get(leadId);

    if (!lead) {
      return res.status(404).json({ error: 'Lead não encontrado' });
    }

    // Compor nome do projeto: prefixo + nome limpo + id curto
    const cleanName = lead.name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9-]/g, '-');
    const shortId = leadId.substring(0, 6);
    const projectName = `site-${cleanName}-${shortId}`.substring(0, 52); // Vercel tem limite de caracteres

    // 2. Fazer Deploy
    const deployUrl = await deployToVercel(projectName, files);

    // 3. Opcional: Atualizar o banco de dados do lead com a URL de prévia gerada
    try {
      // Como não temos coluna específica para preview_url ainda, podemos adicionar ou usar um campo extra.
      // Se a coluna não existir, pode ignorar, mas é o ideal adicionar futuramente.
      // db.prepare('UPDATE leads SET preview_url = ? WHERE id = ?').run(deployUrl, leadId);
    } catch (dbErr) {
      console.warn('Campo preview_url não existe ou erro ao salvar url', dbErr.message);
    }

    return res.json({
      success: true,
      message: 'Deploy realizado com sucesso',
      projectName,
      url: deployUrl
    });

  } catch (error) {
    console.error('❌ Erro no endpoint de deploy:', error);
    return res.status(500).json({ 
      error: 'Falha ao realizar deploy na Vercel',
      details: error.message
    });
  }
});

module.exports = router;
