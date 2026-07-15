/**
 * Middleware de tratamento de erros global
 * Captura erros não tratados e retorna resposta JSON padronizada
 */
function errorHandler(err, req, res, _next) {
  // Log detalhado no servidor
  console.error('\n❌ ═══════════════════════════════════════');
  console.error(`   Erro: ${err.message}`);
  console.error(`   Rota: ${req.method} ${req.originalUrl}`);
  console.error(`   Timestamp: ${new Date().toISOString()}`);
  if (err.stack) {
    console.error(`   Stack: ${err.stack}`);
  }
  console.error('═══════════════════════════════════════\n');

  // Status code: usa o status do erro se definido, senão 500
  const statusCode = err.statusCode || 500;

  // Resposta padronizada
  res.status(statusCode).json({
    error: err.code || 'internal_error',
    message: statusCode === 500
      ? 'Erro interno do servidor. Tente novamente mais tarde.'
      : err.message,
  });
}

module.exports = errorHandler;
