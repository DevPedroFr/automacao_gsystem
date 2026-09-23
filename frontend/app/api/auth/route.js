import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const VALID_USER = process.env.ADMIN_USER || 'Consultings@GP';
const VALID_PASSWORD = process.env.ADMIN_PASSWORD || 'Gp@2026';
const AUTH_COOKIE_NAME = 'apd_session';
const AUTH_TOKEN = 'authenticated_gp_2026_secure_token';

export async function POST(request) {
  try {
    const { username, password } = await request.json();

    if (username === VALID_USER && password === VALID_PASSWORD) {
      const cookieStore = cookies();
      cookieStore.set({
        name: AUTH_COOKIE_NAME,
        value: AUTH_TOKEN,
        httpOnly: true,
        path: '/',
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 30, // 30 dias
      });

      return NextResponse.json({ success: true, message: 'Autenticado com sucesso' });
    }

    return NextResponse.json(
      { success: false, message: 'Usuário ou senha incorretos' },
      { status: 401 }
    );
  } catch (error) {
    return NextResponse.json(
      { success: false, message: 'Erro ao processar autenticação' },
      { status: 500 }
    );
  }
}

export async function DELETE() {
  const cookieStore = cookies();
  cookieStore.delete(AUTH_COOKIE_NAME);
  return NextResponse.json({ success: true, message: 'Sessão encerrada com sucesso' });
}
