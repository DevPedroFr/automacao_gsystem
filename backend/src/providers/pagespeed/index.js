const config = require('../../config/env');

let provider;

switch (config.PAGESPEED_PROVIDER) {
  case 'google':
    provider = require('./google');
    break;
  case 'mock':
  default:
    provider = require('./mock');
    break;
}

console.log(`🔌 PageSpeed Provider carregado: ${config.PAGESPEED_PROVIDER.toUpperCase()}`);

module.exports = provider;
