const config = require('./config/env');

const express = require('express');
const cors = require('cors');

// Importa banco de dados (wrapper assíncrono)
const db = require('./config/database');

// Importa rotas
const campaignRoutes = require('./routes/campaigns');
const leadRoutes = require('./routes/leads');
const diagnosticRoutes = require('./routes/diagnostics');
const settingsRoutes = require('./routes/settings');
const dashboardRoutes = require('./routes/dashboard');
const deployRoutes = require('./routes/deploy');

// Importa middleware
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = config.PORT;

// ─── Middlewares globais ───────────────────────────────────────────────
app.use(express.json());
app.use(cors({
  origin: config.FRONTEND_URL,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// ─── Health check ──────────────────────────────────────────────────────
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Consultings APD Backend',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// ─── Rotas da API ──────────────────────────────────────────────────────
app.use('/api/campaigns', campaignRoutes);
app.use('/api/settings', settingsRoutes);
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/deploy', deployRoutes);
app.use('/api', leadRoutes);
app.use('/api', diagnosticRoutes);

// ─── 404 para rotas não encontradas ────────────────────────────────────
app.use('/api/*', (req, res) => {
  res.status(404).json({
    error: 'not_found',
    message: `Rota ${req.method} ${req.originalUrl} não encontrada`,
  });
});

// ─── Error handler global ──────────────────────────────────────────────
app.use(errorHandler);

// ─── Inicializa servidor (aguarda banco ficar pronto) ──────────────────
async function start() {
  // Aguarda sql.js inicializar o banco
  await db.ready();

  // Limpa campanhas presas em processamento decorrentes de reinicializações do servidor
  try {
    const updated = await db.prepare(`
      UPDATE campaigns 
      SET status = 'failed', error_message = 'Processamento interrompido devido ao reinício do servidor', updated_at = CURRENT_TIMESTAMP
      WHERE status = 'processing'
    `).run();
    if (updated.changes > 0) {
      console.log(`🧹 Limpeza: ${updated.changes} campanha(s) pendente(s) marcada(s) como falha.`);
    }
  } catch (cleanErr) {
    console.error('⚠️ Falha ao limpar campanhas presas no startup:', cleanErr.message);
  }

  app.listen(PORT, () => {
    console.log('\n');
    console.log('╔══════════════════════════════════════════════════════╗');
    console.log('║                                                      ║');
    console.log('║   🚀  CONSULTINGS APD — Backend                      ║');
    console.log('║                                                      ║');
    console.log(`║   🌐  Servidor rodando em: http://localhost:${PORT}     ║`);
    console.log(`║   📡  CORS habilitado para: ${config.FRONTEND_URL.padEnd(23)}║`);
    console.log('║   🗄️   Banco: SQLite (sql.js / WebAssembly)           ║');
    console.log(`║   📋  API Mocks: ${config.USE_REAL_API ? 'DESATIVADOS (REAL)' : 'ATIVADOS  '}                      ║`);
    console.log('║                                                      ║');
    console.log('╚══════════════════════════════════════════════════════╝');
    console.log('\n');
  });
}

start().catch(err => {
  console.error('❌ Falha ao iniciar servidor:', err);
  process.exit(1);
});

module.exports = app;
