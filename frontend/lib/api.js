const API_PROXY_BASE = '/api/backend';

function apiUrl(endpoint = '') {
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_PROXY_BASE}${path}`;
}

export async function fetchApi(endpoint, options = {}) {
  const { headers: optionHeaders, ...requestOptions } = options;
  const res = await fetch(apiUrl(endpoint), {
    ...requestOptions,
    headers: { 'Content-Type': 'application/json', ...optionHeaders },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.message || error.detail?.message || 'Erro na requisição');
  }
  const ct = res.headers.get('content-type');
  if (ct && ct.includes('text/csv')) {
    return res.text();
  }
  return res.json();
}

export function getApiUrl(endpoint = '') {
  return apiUrl(endpoint);
}

