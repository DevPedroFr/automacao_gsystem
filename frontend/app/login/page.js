'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Lock, User, ArrowRight, ShieldCheck, AlertCircle, Activity, Target, Zap } from 'lucide-react';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectPath = searchParams.get('redirect') || '/';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setLoading(true);

    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), password }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.message || 'Credenciais inválidas');
      }

      router.push(redirectPath);
      router.refresh();
    } catch (err) {
      setErrorMessage(err.message || 'Falha ao autenticar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative rounded-3xl border border-white/[0.09] bg-[#0b1421]/85 p-6 shadow-[0_28px_90px_rgba(0,0,0,0.45),0_0_40px_rgba(34,211,238,0.045)] backdrop-blur-2xl sm:p-8">
      <div className="pointer-events-none absolute inset-x-10 top-0 h-px bg-gradient-to-r from-transparent via-cyan-200/30 to-transparent" />
      <form onSubmit={handleSubmit} className="space-y-5">
        {errorMessage && (
          <div className="flex items-center gap-2.5 p-3.5 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs animate-fade-in">
            <AlertCircle size={16} className="shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
            Usuário
          </label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 text-gray-500 pointer-events-none">
              <User size={16} />
            </span>
            <input
              type="text"
              required
              placeholder="Nome de usuário"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-950/60 border border-gray-800 rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
            Senha de Acesso
          </label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 text-gray-500 pointer-events-none">
              <Lock size={16} />
            </span>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-950/60 border border-gray-800 rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold py-3.5 px-4 rounded-xl text-sm transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_30px_rgba(6,182,212,0.5)] disabled:opacity-50 flex items-center justify-center gap-2 group"
        >
          {loading ? (
            <span>Verificando credenciais...</span>
          ) : (
            <>
              <span>Entrar na Automação</span>
              <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </>
          )}
        </button>
      </form>

      <div className="mt-6 pt-5 border-t border-gray-800/80 text-center text-[11px] text-gray-500">
        Ambiente seguro protegido por credenciais de acesso.
      </div>
    </div>
  );
}

export default function LoginPage() {
  const platformFeatures = [
    { icon: Activity, label: 'Indicadores em tempo real', detail: 'Acompanhamento da operação' },
    { icon: Target, label: 'Pipeline comercial', detail: 'Leads organizados por etapa' },
    { icon: Zap, label: 'Campanhas inteligentes', detail: 'Prospecção automatizada' },
  ];

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#080d16] text-gray-100">
      <div className="pointer-events-none absolute -left-40 top-0 h-[540px] w-[540px] rounded-full bg-cyan-500/[0.07] blur-[150px]" />
      <div className="pointer-events-none absolute -bottom-48 right-0 h-[540px] w-[540px] rounded-full bg-indigo-500/[0.08] blur-[150px]" />

      <div className="relative z-10 mx-auto grid min-h-screen w-full max-w-[1320px] grid-cols-1 items-center gap-10 px-4 py-8 sm:px-8 lg:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.8fr)] lg:gap-16 lg:px-14">
        <section className="hidden lg:block">
          <div className="mb-10 inline-flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-200/20 bg-gradient-to-br from-cyan-300/20 to-blue-500/10 text-cyan-100 shadow-[0_8px_28px_rgba(8,145,178,0.15)]">
              <Zap size={22} fill="currentColor" />
            </span>
            <span>
              <span className="block text-sm font-semibold tracking-tight text-white">Automação de Leads</span>
              <span className="mt-1 block font-mono text-[9px] uppercase tracking-[0.2em] text-cyan-100/55">
                Intelligence suite
              </span>
            </span>
          </div>

          <div className="mb-5 flex items-center gap-2 font-mono text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-100/60">
            <span className="h-px w-7 bg-cyan-200/50" />
            Lead intelligence platform
          </div>
          <h1 className="max-w-2xl text-5xl font-semibold leading-[1.08] tracking-[-0.04em] text-white xl:text-6xl">
            Transforme dados em{' '}
            <span className="bg-gradient-to-r from-cyan-200 via-cyan-300 to-blue-300 bg-clip-text text-transparent">
              movimento comercial.
            </span>
          </h1>
          <p className="mt-6 max-w-lg text-base leading-7 text-gray-400">
            Um espaço de trabalho para encontrar oportunidades, acompanhar campanhas e conduzir cada lead até a conversão.
          </p>

          <div className="mt-10 max-w-lg space-y-3">
            {platformFeatures.map(({ icon: Icon, label, detail }, index) => (
              <div key={label} className="flex items-center gap-4 rounded-2xl border border-white/[0.06] bg-white/[0.025] px-4 py-3.5">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-200/10 bg-cyan-300/[0.06] text-cyan-100/85">
                  <Icon size={18} strokeWidth={1.7} />
                </span>
                <span className="flex-1">
                  <span className="block text-sm font-medium text-gray-200">{label}</span>
                  <span className="mt-0.5 block text-xs text-gray-500">{detail}</span>
                </span>
                <span className="font-mono text-[9px] text-gray-700">0{index + 1}</span>
              </div>
            ))}
          </div>

          <div className="mt-10 flex items-center gap-3 font-mono text-[9px] uppercase tracking-[0.17em] text-gray-600">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400/40" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400/80" />
            </span>
            Ambiente protegido · G-System + Spy Car
          </div>
        </section>

        <div className="relative z-10 mx-auto w-full max-w-md">
          <div className="mb-8 text-center lg:hidden">
            <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-200/20 bg-gradient-to-br from-cyan-300/20 to-blue-600/10 text-cyan-100 shadow-[0_8px_28px_rgba(8,145,178,0.15)]">
              <ShieldCheck size={27} />
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-white">
              Automação <span className="text-cyan-200">de Leads</span>
            </h1>
            <p className="mt-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-gray-500">
              Intelligence suite
            </p>
          </div>

          <div className="mb-4 hidden items-center justify-between px-1 lg:flex">
            <span className="font-mono text-[10px] font-semibold uppercase tracking-[0.17em] text-gray-500">
              Acesso à plataforma
            </span>
            <span className="inline-flex items-center gap-1.5 text-[10px] font-medium text-emerald-200/65">
              <ShieldCheck size={13} />
              Conexão segura
            </span>
          </div>

          <Suspense fallback={<div className="py-8 text-center text-gray-500">Carregando painel seguro...</div>}>
            <LoginForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
