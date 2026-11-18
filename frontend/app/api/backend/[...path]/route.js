import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

const AUTH_COOKIE_NAME = 'apd_session';
const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, '');
const API_BASE = configuredApiUrl
  ? `${configuredApiUrl}${configuredApiUrl.endsWith('/api') ? '' : '/api'}`
  : '';
const FORWARDED_RESPONSE_HEADERS = [
  'cache-control',
  'content-disposition',
  'content-type',
  'retry-after',
];

async function forwardRequest(request, { params }) {
  const token = cookies().get(AUTH_COOKIE_NAME)?.value;
  if (!token) {
    return NextResponse.json(
      { detail: { message: 'Autenticação obrigatória.' } },
      { status: 401 },
    );
  }
  if (!API_BASE) {
    return NextResponse.json(
      { detail: { message: 'A URL da API não está configurada.' } },
      { status: 503 },
    );
  }

  const path = (params.path || []).map((segment) => encodeURIComponent(segment)).join('/');
  const query = new URL(request.url).search;
  const method = request.method.toUpperCase();
  const headers = new Headers({
    Authorization: `Bearer ${token}`,
    Accept: request.headers.get('accept') || 'application/json',
  });
  const contentType = request.headers.get('content-type');
  if (contentType) headers.set('Content-Type', contentType);

  let upstream;
  try {
    upstream = await fetch(`${API_BASE}/${path}${query}`, {
      method,
      headers,
      body: ['GET', 'HEAD'].includes(method) ? undefined : await request.arrayBuffer(),
      cache: 'no-store',
    });
  } catch (error) {
    console.error('Erro ao encaminhar requisição para a API:', error);
    return NextResponse.json(
      { detail: { message: 'Não foi possível conectar ao backend.' } },
      { status: 502 },
    );
  }

  const responseHeaders = new Headers();
  for (const headerName of FORWARDED_RESPONSE_HEADERS) {
    const value = upstream.headers.get(headerName);
    if (value) responseHeaders.set(headerName, value);
  }

  const response = new NextResponse(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
  if (upstream.status === 401) response.cookies.delete(AUTH_COOKIE_NAME);
  return response;
}

export const GET = forwardRequest;
export const POST = forwardRequest;
export const PUT = forwardRequest;
export const PATCH = forwardRequest;
export const DELETE = forwardRequest;
