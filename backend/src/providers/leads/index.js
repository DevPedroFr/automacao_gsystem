const config = require('../../config/env');

let provider;

switch (config.LEAD_PROVIDER) {
  case 'apify':
    provider = require('./apify');
    break;
  case 'outscraper':
    provider = require('./outscraper');
    break;
  case 'mock':
  default:
    provider = require('./mock');
    break;
}

console.log(`🔌 Lead Provider carregado: ${config.LEAD_PROVIDER.toUpperCase()}`);

module.exports = provider;
