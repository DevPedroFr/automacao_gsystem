const config = require('../config/env');

/**
 * Faz o deploy de um conjunto de arquivos na Vercel usando a Vercel API.
 * @param {string} projectName - O nome do projeto na Vercel (ex: 'lead-consultings-apd').
 * @param {Array<{file: string, data: string}>} files - Lista de arquivos (caminho e conteúdo base64/texto).
 * @returns {Promise<string>} A URL do site publicado.
 */
async function deployToVercel(projectName, files) {
  if (!config.VERCEL_API_TOKEN) {
    throw new Error('VERCEL_API_TOKEN não está configurado no .env.');
  }

  const endpoint = 'https://api.vercel.com/v13/deployments';
  
  const payload = {
    name: projectName.toLowerCase().replace(/[^a-z0-9-]/g, '-').substring(0, 52),
    files: files.map(f => ({
      file: f.file,
      data: f.data
    })),
    projectSettings: {
      framework: null, // HTML estático por padrão (pode ser alterado para 'nextjs' se for o caso)
    },
    target: 'production'
  };

  try {
    console.log(`[Vercel Service] Iniciando deploy do projeto "${payload.name}"...`);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.VERCEL_API_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Erro da Vercel API (Status ${response.status}): ${errorText}`);
    }

    const data = await response.json();
    console.log(`[Vercel Service] Deploy concluído. URL: https://${data.url}`);
    
    return `https://${data.url}`;
  } catch (error) {
    console.error(`❌ [Vercel Service] Falha ao fazer deploy:`, error.message);
    throw error;
  }
}

module.exports = { deployToVercel };
