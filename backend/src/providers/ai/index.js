const config = require('../../config/env');

let provider;

switch (config.AI_PROVIDER) {
  case 'gemini':
    provider = require('./gemini');
    break;
  case 'openai':
    provider = require('./openai');
    break;
  case 'mock':
  default:
    provider = require('./mock');
    break;
}

console.log(`🔌 AI Provider carregado: ${config.AI_PROVIDER.toUpperCase()}`);

module.exports = provider;
