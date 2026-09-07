const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();

if (!configuredApiUrl) {
  throw new Error('NEXT_PUBLIC_API_URL não está configurada. Defina a URL pública da API antes do build.');
}

const API_BASE = configuredApiUrl.replace(/\/+$/, '');

export async function fetchApi(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.message || 'Erro na requisição');
  }
  const ct = res.headers.get('content-type');
  if (ct && ct.includes('text/csv')) {
    return res.text();
  }
  return res.json();
}
