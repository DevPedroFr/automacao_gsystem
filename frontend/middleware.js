import { NextResponse } from 'next/server';

const AUTH_COOKIE_NAME = 'apd_session';

function hasSessionToken(request) {
  const token = request.cookies.get(AUTH_COOKIE_NAME)?.value;
  return typeof token === 'string' && token.split('.').length === 3;
}

export function middleware(request) {
  const { pathname } = request.nextUrl;

  // 1. Rotas públicas liberadas sem autenticação (para clientes visualizarem sites gerados)
  if (
    pathname.startsWith('/login') ||
    pathname.startsWith('/api/auth') ||
    pathname.includes('/lp-preview') || // Permite que leads visualizem a LP gerada
    pathname.startsWith('/site/') ||    // Páginas públicas de clientes
    pathname.startsWith('/p/') ||       // Páginas públicas de clientes
    pathname.startsWith('/_next') ||
    pathname.startsWith('/favicon.ico') ||
    pathname.match(/\.(png|jpg|jpeg|svg|webp|ico|css|js|html)$/)
  ) {
    // Se já estiver logado e tentar acessar /login, manda pro dashboard
    if (pathname === '/login') {
      if (hasSessionToken(request)) {
        return NextResponse.redirect(new URL('/', request.url));
      }
    }
    return NextResponse.next();
  }

  // 2. Verificar se o usuário possui cookie de sessão válido
  if (!hasSessionToken(request)) {
    // Se for chamada de API interna, responde 401
    if (pathname.startsWith('/api')) {
      return NextResponse.json(
        { error: 'unauthorized', message: 'Acesso restrito. Faça login para continuar.' },
        { status: 401 }
      );
    }

    // Se for navegação de página, redireciona para a tela de login
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
