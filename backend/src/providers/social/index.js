const config = require('../../config/env');

let provider;

switch (config.SOCIAL_PROVIDER) {
  case 'basic':
    provider = require('./basic');
    break;
  case 'mock':
  default:
    provider = require('./mock');
    break;
}

console.log(`🔌 Social Provider carregado: ${config.SOCIAL_PROVIDER.toUpperCase()}`);

module.exports = provider;
