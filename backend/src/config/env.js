const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Garante que carrega do diretório backend correto
const envPath = path.join(__dirname, '..', '..', '.env');

if (fs.existsSync(envPath)) {
  dotenv.config({ path: envPath });
} else {
  dotenv.config(); // Fallback padrão
}

const config = {
  PORT: parseInt(process.env.PORT || '3001', 10),
  FRONTEND_URL: process.env.FRONTEND_URL || 'http://localhost:3000',
  USE_REAL_API: process.env.USE_REAL_API === 'true',
  APIFY_API_KEY: process.env.APIFY_API_KEY || '',
  VERCEL_API_TOKEN: process.env.VERCEL_API_TOKEN || '',
  PAGESPEED_API_KEY: process.env.PAGESPEED_API_KEY || '',
  GEMINI_API_KEY: process.env.GEMINI_API_KEY || '',
  OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
  GEMINI_MODEL: process.env.GEMINI_MODEL || 'gemini-1.5-flash',
  LEAD_PROVIDER: process.env.LEAD_PROVIDER || 'mock',
  PAGESPEED_PROVIDER: process.env.PAGESPEED_PROVIDER || 'mock',
  SOCIAL_PROVIDER: process.env.SOCIAL_PROVIDER || 'mock',
  AI_PROVIDER: process.env.AI_PROVIDER || 'mock',
};

// Validação básica do PORT
if (isNaN(config.PORT)) {
  throw new Error('❌ Variável de ambiente PORT inválida: deve ser um número.');
}

// Validação dos Providers
const validLeadProviders = ['mock', 'apify', 'outscraper'];
if (!validLeadProviders.includes(config.LEAD_PROVIDER)) {
  throw new Error(`❌ LEAD_PROVIDER inválido: deve ser um dos seguintes: ${validLeadProviders.join(', ')}`);
}

const validPagespeedProviders = ['mock', 'google'];
if (!validPagespeedProviders.includes(config.PAGESPEED_PROVIDER)) {
  throw new Error(`❌ PAGESPEED_PROVIDER inválido: deve ser um dos seguintes: ${validPagespeedProviders.join(', ')}`);
}

const validSocialProviders = ['mock', 'basic'];
if (!validSocialProviders.includes(config.SOCIAL_PROVIDER)) {
  throw new Error(`❌ SOCIAL_PROVIDER inválido: deve ser um dos seguintes: ${validSocialProviders.join(', ')}`);
}

const validAiProviders = ['mock', 'gemini', 'openai'];
if (!validAiProviders.includes(config.AI_PROVIDER)) {
  throw new Error(`❌ AI_PROVIDER inválido: deve ser um dos seguintes: ${validAiProviders.join(', ')}`);
}

// Se o modo real estiver ativo, avisa sobre chaves ausentes
if (config.USE_REAL_API) {
  const missingKeys = [];
  if (!config.APIFY_API_KEY || config.APIFY_API_KEY === 'your_apify_key_here') {
    missingKeys.push('APIFY_API_KEY');
  }
  if (!config.PAGESPEED_API_KEY || config.PAGESPEED_API_KEY === 'your_pagespeed_key_here') {
    missingKeys.push('PAGESPEED_API_KEY');
  }
  if (!config.GEMINI_API_KEY || config.GEMINI_API_KEY === 'your_gemini_key_here') {
    missingKeys.push('GEMINI_API_KEY');
  }
  if (!config.OPENAI_API_KEY || config.OPENAI_API_KEY === 'your_openai_key_here') {
    missingKeys.push('OPENAI_API_KEY');
  }

  if (missingKeys.length > 0) {
    console.warn(`⚠️ ALERTA: USE_REAL_API está definido como true, mas as seguintes chaves de API estão ausentes ou com valores padrão no .env: ${missingKeys.join(', ')}. A integração real pode falhar.`);
  }
}

module.exports = config;
