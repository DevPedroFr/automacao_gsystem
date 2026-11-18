import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const AUTH_COOKIE_NAME = 'apd_session';
const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, '');
const API_BASE = configuredApiUrl
  ? `${configuredApiUrl}${configuredApiUrl.endsWith('/api') ? '' : '/api'}`
  : '';

function authCookieOptions() {
  return {
    httpOnly: true,
    path: '/',
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 12,
  };
}

async function readBackendResponse(response) {
  const body = await response.json().catch(() => ({}));
  const message = body.detail?.message || body.message || 'Falha ao autenticar.';
  return { body, message };
}

export async function POST(request) {
  if (!API_BASE) {
    return NextResponse.json(
      { success: false, message: 'A URL da API não está configurada.' },
      { status: 503 },
    );
  }

  try {
    const credentials = await request.json();
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
      cache: 'no-store',
    });
    const { body, message } = await readBackendResponse(response);
    if (!response.ok) {
      return NextResponse.json({ success: false, message }, { status: response.status });
    }
    if (!body.access_token || !body.user) {
      return NextResponse.json(
        { success: false, message: 'A API retornou uma sessão inválida.' },
        { status: 502 },
      );
    }

    const result = NextResponse.json({ success: true, user: body.user });
    result.cookies.set(AUTH_COOKIE_NAME, body.access_token, authCookieOptions());
    return result;
  } catch (error) {
    console.error('Erro ao conectar ao serviço de autenticação:', error);
    return NextResponse.json(
      { success: false, message: 'Não foi possível conectar ao serviço de autenticação.' },
      { status: 502 },
    );
  }
}

export async function GET() {
  const token = cookies().get(AUTH_COOKIE_NAME)?.value;
  if (!token || !API_BASE) {
    return NextResponse.json({ success: false, message: 'Sessão não encontrada.' }, { status: 401 });
  }

  try {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    });
    const { body, message } = await readBackendResponse(response);
    if (!response.ok) {
      const result = NextResponse.json({ success: false, message }, { status: response.status });
      if (response.status === 401) result.cookies.delete(AUTH_COOKIE_NAME);
      return result;
    }
    return NextResponse.json({ success: true, user: body.data });
  } catch (error) {
    console.error('Erro ao consultar a sessão:', error);
    return NextResponse.json(
      { success: false, message: 'Não foi possível consultar a sessão.' },
      { status: 502 },
    );
  }
}

export async function DELETE() {
  const result = NextResponse.json({ success: true, message: 'Sessão encerrada com sucesso.' });
  result.cookies.delete(AUTH_COOKIE_NAME);
  return result;
}
