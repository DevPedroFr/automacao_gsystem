const express = require('express');
const db = require('../config/database');

const router = express.Router();

/**
 * GET /api/settings
 * Retorna as configurações salvas no banco
 */
router.get('/', async (req, res) => {
  try {
    const rows = await db.prepare('SELECT * FROM settings').all();
    const settings = {};
    
    // Converte linhas para um objeto de chave-valor simples
    rows.forEach(row => {
      settings[row.key] = row.value;
    });

    res.json({ data: settings });
  } catch (err) {
    res.status(500).json({ error: 'db_error', message: 'Erro ao buscar configurações', details: err.message });
  }
});

/**
 * POST /api/settings
 * Grava ou atualiza configurações
 * Body: { [key]: value } (ex: { webhook_url: "http://..." })
 */
router.post('/', async (req, res) => {
  try {
    const body = req.body;
    
    if (!body || typeof body !== 'object') {
      return res.status(400).json({ error: 'validation_error', message: 'Payload inválido' });
    }

    const insertOrUpdate = await db.prepare(`
      INSERT OR REPLACE INTO settings (key, value)
      VALUES (?, ?)
    `);

    // Insere ou atualiza cada chave enviada no body
    Object.entries(body).forEach(([key, value]) => {
      // Grava valor nulo ou string vazia se nulo/undefined, senão converte para string
      const valStr = value === null || value === undefined ? '' : String(value).trim();
      insertOrUpdate.run(key, valStr);
    });

    // Retorna todas as configurações atualizadas
    const rows = db.prepare('SELECT * FROM settings').all();
    const settings = {};
    rows.forEach(row => {
      settings[row.key] = row.value;
    });

    res.json({ data: settings, message: 'Configurações salvas com sucesso' });
  } catch (err) {
    res.status(500).json({ error: 'db_error', message: 'Erro ao salvar configurações', details: err.message });
  }
});

/**
 * POST /api/settings/test-webhook
 * Dispara um webhook de teste para a URL fornecida ou cadastrada no banco
 */
router.post('/test-webhook', async (req, res) => {
  try {
    const { webhook_url } = req.body;
    let urlToTest = webhook_url;
    
    if (!urlToTest) {
      const row = await db.prepare("SELECT value FROM settings WHERE key = 'webhook_url'").get();
      urlToTest = row?.value;
    }

    if (!urlToTest) {
      return res.status(400).json({ error: 'validation_error', message: 'Nenhuma URL de webhook configurada.' });
    }

    const payload = {
      event: 'test_connection',
      timestamp: new Date().toISOString(),
      data: {
        message: 'Conexão de teste realizada com sucesso da plataforma CONSULTINGS APD!',
        system: 'CONSULTINGS APD Automation',
        status: 'active'
      }
    };

    const response = await fetch(urlToTest, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(6000)
    });

    if (response.ok) {
      res.json({ success: true, message: 'Webhook de teste enviado e aceito com sucesso pelo receptor!' });
    } else {
      const text = await response.text().catch(() => '');
      res.status(response.status).json({ 
        success: false, 
        message: `O receptor retornou erro (Status ${response.status})`, 
        details: text 
      });
    }
  } catch (err) {
    res.status(500).json({ 
      success: false, 
      message: 'Falha ao conectar com o webhook: ' + err.message 
    });
  }
});

module.exports = router;
