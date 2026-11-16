'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Lock, User, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

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
    <div className="bg-gray-900/80 backdrop-blur-xl border border-gray-800 rounded-3xl p-8 shadow-2xl relative">
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
              autoFocus
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
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-[#0B0F19] text-gray-100 relative overflow-hidden">
      {/* Background Ambient Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-cyan-500/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-[400px] h-[300px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-cyan-400 mb-4 shadow-[0_0_25px_rgba(6,182,212,0.2)]">
            <ShieldCheck size={28} />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-wide">
            Automação <span className="text-cyan-400">de Leads</span>
          </h1>
          <p className="text-xs text-gray-400 mt-1 uppercase tracking-widest font-semibold">
            Área de Acesso Restrito
          </p>
        </div>

        {/* Suspense Wrapper for Next.js 14 */}
        <Suspense fallback={<div className="text-center text-gray-500 py-8">Carregando painel seguro...</div>}>
          <LoginForm />
        </Suspense>
      </div>
    </div>
  );
}
