const http = require('http');
const https = require('https');
const { URL } = require('url');

/**
 * Faz uma requisição GET simples para extrair a meta tag og:image
 * de um site de forma leve, sem precisar rodar um navegador headless completo.
 * 
 * @param {string} websiteUrl A URL do site do cliente
 * @returns {Promise<string|null>} A URL da imagem ou null
 */
function fetchOgImage(websiteUrl) {
  return new Promise((resolve) => {
    if (!websiteUrl || !websiteUrl.startsWith('http')) {
      return resolve(null);
    }

    try {
      const parsedUrl = new URL(websiteUrl);
      const protocol = parsedUrl.protocol === 'https:' ? https : http;

      const req = protocol.get(websiteUrl, { timeout: 10000 }, (res) => {
        // Seguir redirecionamentos básicos
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          const redirectUrl = new URL(res.headers.location, parsedUrl.origin).href;
          return resolve(fetchOgImage(redirectUrl));
        }

        if (res.statusCode !== 200) {
          return resolve(null);
        }

        let html = '';
        res.on('data', (chunk) => {
          html += chunk.toString();
          // Para otimizar, encerramos a requisição cedo se já encontrarmos a tag ou lermos os primeiros 100kb
          // Geralmente as meta tags estão no <head>
          if (html.length > 100000) {
            req.abort();
          }
        });

        res.on('end', () => {
          // Expressão regular para encontrar <meta property="og:image" content="...">
          const ogImageRegex = /<meta\s+(?:[^>]*?\s+)?(?:property|name)=["']og:image["']\s+content=["'](.*?)["']/i;
          const match = html.match(ogImageRegex);
          
          if (match && match[1]) {
            let imageUrl = match[1];
            // Se a URL for relativa, converter para absoluta
            if (imageUrl.startsWith('/')) {
              imageUrl = new URL(imageUrl, parsedUrl.origin).href;
            }
            resolve(imageUrl);
          } else {
            resolve(null);
          }
        });
      });

      req.on('error', () => resolve(null));
      req.on('timeout', () => {
        req.abort();
        resolve(null);
      });

    } catch (e) {
      resolve(null);
    }
  });
}

module.exports = { fetchOgImage };
