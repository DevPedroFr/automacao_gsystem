'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import {
  Activity,
  BriefcaseBusiness,
  LayoutDashboard,
  LogOut,
  ShieldCheck,
  Settings2,
  Target,
  Zap,
} from 'lucide-react';

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/crm', label: 'CRM', icon: BriefcaseBusiness },
  { href: '/campaigns', label: 'Campanhas', icon: Target },
  { href: '/settings', label: 'Configurações', icon: Settings2 },
];

const accessLabels = {
  g_system: 'G-System',
  spy_car: 'Spy Car',
  diretoria: 'Diretoria',
};

function isActiveRoute(pathname, href) {
  return href === '/' ? pathname === '/' : pathname.startsWith(href);
}

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    let active = true;
    fetch('/api/auth')
      .then((response) => response.ok ? response.json() : null)
      .then((result) => {
        if (active) setUser(result?.user || null);
      })
      .catch((err) => console.error('Erro ao carregar nível de acesso:', err));

    return () => {
      active = false;
    };
  }, []);

  if (pathname === '/login') return null;

  const visibleNavItems = navItems.filter(
    (item) => item.href !== '/settings' || user?.access_level === 'diretoria',
  );

  const handleLogout = async () => {
    try {
      await fetch('/api/auth', { method: 'DELETE' });
    } catch (err) {
      console.error('Erro ao sair:', err);
    } finally {
      router.push('/login');
      router.refresh();
    }
  };

  return (
    <>
      <aside className="relative z-20 hidden min-h-screen w-[276px] shrink-0 flex-col border-r border-white/[0.07] bg-[#080f1b]/90 backdrop-blur-2xl md:flex print:hidden">
        <div className="pointer-events-none absolute inset-y-8 right-0 w-px bg-gradient-to-b from-transparent via-cyan-300/20 to-transparent" />

        <div className="px-5 pb-7 pt-7">
          <Link href="/" className="group flex items-center gap-3.5 rounded-2xl focus-visible:outline-offset-4">
            <span className="flex h-11 w-11 items-center justify-center rounded-[14px] border border-cyan-200/20 bg-gradient-to-br from-cyan-300/20 to-blue-500/10 text-cyan-100 shadow-[0_8px_24px_rgba(8,145,178,0.12)] transition-transform group-hover:scale-[1.04]">
              <Zap size={21} fill="currentColor" strokeWidth={1.7} />
            </span>
            <span className="min-w-0">
              <span className="block truncate text-[15px] font-semibold tracking-tight text-white">Automação de Leads</span>
              <span className="mt-1 block font-mono text-[9px] font-semibold uppercase tracking-[0.19em] text-cyan-200/55">
                Intelligence suite
              </span>
            </span>
          </Link>
        </div>

        <div className="mx-5 mb-3 flex items-center justify-between border-t border-white/[0.06] pt-5">
          <span className="font-mono text-[9px] font-semibold uppercase tracking-[0.2em] text-gray-600">
            Workspace
          </span>
          <Activity size={13} className="text-gray-600" />
        </div>

        <nav aria-label="Navegação principal" className="flex-1 space-y-1 px-3">
          {visibleNavItems.map((item, index) => {
            const active = isActiveRoute(pathname, item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? 'page' : undefined}
                className={`group relative flex items-center gap-3 rounded-xl border px-3.5 py-3 text-[13px] font-medium transition-all duration-200 ${
                  active
                    ? 'border-cyan-200/[0.12] bg-gradient-to-r from-cyan-300/[0.11] via-cyan-300/[0.045] to-transparent text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.035)]'
                    : 'border-transparent text-gray-400 hover:border-white/[0.055] hover:bg-white/[0.035] hover:text-gray-100'
                }`}
              >
                {active && <span className="absolute -left-px top-2.5 bottom-2.5 w-0.5 rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(34,211,238,0.65)]" />}
                <span className={`flex h-8 w-8 items-center justify-center rounded-lg transition-colors ${
                  active ? 'bg-cyan-300/[0.1] text-cyan-100' : 'text-gray-500 group-hover:text-gray-200'
                }`}>
                  <Icon size={17} strokeWidth={1.8} />
                </span>
                <span className="flex-1">{item.label}</span>
                <span className={`font-mono text-[9px] ${active ? 'text-cyan-100/45' : 'text-gray-700'}`}>
                  0{index + 1}
                </span>
              </Link>
            );
          })}
        </nav>

        <div className="space-y-3 border-t border-white/[0.06] px-4 pb-5 pt-4">
          <div className="rounded-2xl border border-white/[0.07] bg-gradient-to-br from-white/[0.045] to-white/[0.015] p-3.5">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck size={12} className="text-cyan-200/65" />
                <span className="font-mono text-[9px] font-semibold uppercase tracking-[0.15em] text-gray-400">
                  Ambiente protegido
                </span>
              </div>
              <span className="rounded-md border border-cyan-300/10 bg-cyan-400/[0.045] px-1.5 py-0.5 font-mono text-[8px] text-cyan-100/60">
                AUTH
              </span>
            </div>
            <p className="truncate text-xs font-semibold text-gray-200">{user?.username || 'Painel comercial'}</p>
            <p className="mt-1 text-[10px] text-gray-500">{accessLabels[user?.access_level] || 'Inteligência comercial'}</p>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="group flex w-full items-center gap-3 rounded-xl border border-transparent px-3.5 py-2.5 text-xs font-semibold text-gray-500 transition-colors hover:border-rose-300/10 hover:bg-rose-400/[0.05] hover:text-rose-200"
          >
            <LogOut size={15} className="transition-transform group-hover:-translate-x-0.5" />
            Encerrar sessão
          </button>
          <div className="px-3.5 font-mono text-[9px] uppercase tracking-[0.14em] text-gray-700">
            Commercial intelligence · v1.2
          </div>
        </div>
      </aside>

      <nav
        aria-label="Navegação principal"
        className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around border-t border-white/[0.08] bg-[#080f1b]/95 px-2 pb-[max(0.65rem,env(safe-area-inset-bottom))] pt-2 shadow-[0_-12px_36px_rgba(0,0,0,0.35)] backdrop-blur-2xl md:hidden print:hidden"
      >
        {visibleNavItems.map((item) => {
          const active = isActiveRoute(pathname, item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? 'page' : undefined}
              className={`flex min-w-[68px] flex-col items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-[10px] font-medium transition-colors ${
                active ? 'text-cyan-100' : 'text-gray-500 hover:text-gray-200'
              }`}
            >
              <span className={`flex h-7 w-10 items-center justify-center rounded-lg transition-colors ${
                active ? 'border border-cyan-200/10 bg-cyan-300/[0.1]' : ''
              }`}>
                <Icon size={17} strokeWidth={1.8} />
              </span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </>
  );
}
