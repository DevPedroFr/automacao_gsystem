const db = require('../config/database');

/**
 * Dispara um webhook para a URL cadastrada nas configurações
 * @param {string} event - Nome do evento (ex: 'campaign_completed', 'diagnostic_generated')
 * @param {Object} payload - Dados do payload a serem enviados
 */
async function triggerWebhook(event, payload) {
  try {
    // Busca a webhook_url salva no banco
    const row = await db.prepare("SELECT value FROM settings WHERE key = 'webhook_url'").get();
    const webhookUrl = row?.value;

    if (!webhookUrl) {
      console.log(`ℹ️ [Webhook Service] Nenhum webhook configurado. Pulando evento "${event}".`);
      return;
    }

    console.log(`📡 [Webhook Service] Enviando evento "${event}" para: ${webhookUrl}`);

    const body = {
      event: event,
      timestamp: new Date().toISOString(),
      data: payload,
    };

    // Executa a chamada em background
    fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10000), // Timeout de 10s
    })
      .then(async (response) => {
        if (!response.ok) {
          const text = await response.text().catch(() => '');
          console.warn(`⚠️ [Webhook Service] Falha no receptor (Status ${response.status}): ${text}`);
        } else {
          console.log(`✅ [Webhook Service] Evento "${event}" enviado com sucesso!`);
        }
      })
      .catch((err) => {
        console.error(`❌ [Webhook Service] Erro ao enviar requisição HTTP do webhook:`, err.message);
      });

  } catch (err) {
    console.error(`❌ [Webhook Service] Falha ao disparar webhook:`, err.message);
  }
}

module.exports = { triggerWebhook };
