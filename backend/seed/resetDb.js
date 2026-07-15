const db = require('../src/config/database');

async function resetDatabase() {
  console.log('🧹 Limpando todos os dados do banco de dados (SQLite)...');
  
  try {
    await db.ready();
    
    // Executa deletes nas tabelas principais
    db.prepare('DELETE FROM diagnostics').run();
    db.prepare('DELETE FROM leads').run();
    db.prepare('DELETE FROM campaigns').run();
    db.prepare('DELETE FROM api_call_logs').run();
    
    console.log('✅ Banco de dados limpo com sucesso! Todas as campanhas, leads, diagnósticos e logs foram removidos.');
  } catch (err) {
    console.error('❌ Falha ao limpar o banco de dados:', err);
  }
}

resetDatabase();
