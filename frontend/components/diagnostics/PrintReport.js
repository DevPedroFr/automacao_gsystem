'use client';

import React from 'react';
import { 
  Activity, Globe, MapPin, AlertTriangle, TrendingDown, 
  ShieldAlert, Sparkles, CheckCircle2, ArrowRight, DollarSign, 
  Search, Users, Zap, ExternalLink, Award, Clock, Phone, 
  AlertCircle, BarChart3, Check 
} from 'lucide-react';

const GoogleLogo = ({ size = 16, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
);

const InstagramLogo = ({ size = 16, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <defs>
      <linearGradient id="ig-grad-print" x1="2" y1="22" x2="22" y2="2" gradientUnits="userSpaceOnUse">
        <stop stopColor="#FEE411"/>
        <stop offset="0.1" stopColor="#FDF030"/>
        <stop offset="0.5" stopColor="#FD5949"/>
        <stop offset="0.75" stopColor="#D6249F"/>
        <stop offset="1" stopColor="#285AEB"/>
      </linearGradient>
    </defs>
    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 10-2.881.001 1.44 1.44 0 002.881-.001z" fill="url(#ig-grad-print)"/>
  </svg>
);

const LinkedinLogo = ({ size = 16, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" fill="#0A66C2"/>
  </svg>
);

const safeParseJson = (data) => {
  if (!data) return null;
  if (typeof data === 'object') return data;
  try {
    return JSON.parse(data);
  } catch {
    return null;
  }
};

const formatBoldText = (text) => {
  if (typeof text !== 'string') return text;
  const parts = text.split(/\*\*([^*]+)\*\*/g);
  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return <strong key={index} className="font-extrabold text-gray-900">{part}</strong>;
    }
    return part;
  });
};

export default function PrintReport({ lead, diagnostic }) {
  if (!lead) return null;

  const diag = diagnostic || {};

  // Dados enriquecidos
  const criticalBlunders = safeParseJson(diag.critical_blunders) || [];
  const revenueLeak = safeParseJson(diag.revenue_leak);
  const transformationMatrix = safeParseJson(diag.transformation_matrix) || [];
  const brandColors = safeParseJson(diag.brand_colors);
  const ownersInfo = safeParseJson(diag.owners_info) || [];
  const nicheInsights = diag.niche_insights;
  const valueProposition = diag.value_proposition;
  const salesApproach = diag.sales_approach;
  const recommendationsText = diag.recommendations;
  const hasGeneratedSite = Boolean(diag.has_generated_site || diag.preview_url);

  // Render Stars function
  const renderStars = (rating) => {
    const full = Math.floor(rating || 0);
    const half = (rating || 0) % 1 >= 0.5;
    const stars = [];
    for (let i = 0; i < 5; i++) {
      if (i < full) {
        stars.push(<span key={i} className="text-amber-500 text-sm">★</span>);
      } else if (i === full && half) {
        stars.push(<span key={i} className="text-amber-500 text-sm">★</span>);
      } else {
        stars.push(<span key={i} className="text-gray-300 text-sm">★</span>);
      }
    }
    return stars;
  };

  // Parse Fatos e Inferências tradicionais
  const parseDiagnosticData = (factsText, inferencesText) => {
    const categories = {
      google: { title: 'Google Empresa & Local', icon: '📍', facts: [], inferences: [] },
      website: { title: 'Website, Performance & SEO', icon: '🌐', facts: [], inferences: [] },
      social: { title: 'Redes Sociais & Engajamento', icon: '📱', facts: [], inferences: [] },
      general: { title: 'Outras Observações', icon: '🔍', facts: [], inferences: [] }
    };

    const getCategory = (text) => {
      const t = text.toLowerCase();
      if (t.includes('google') || t.includes('rating') || t.includes('avaliaç') || t.includes('gbp') || t.includes('maps') || t.includes('reviews') || t.includes('telefone') || t.includes('endereço')) {
        return 'google';
      }
      if (t.includes('site') || t.includes('website') || t.includes('pagespeed') || t.includes('lcp') || t.includes('inp') || t.includes('cls') || t.includes('velocidade') || t.includes('performance') || t.includes('seo') || t.includes('landing page')) {
        return 'website';
      }
      if (t.includes('instagram') || t.includes('facebook') || t.includes('linkedin') || t.includes('social') || t.includes('redes') || t.includes('post') || t.includes('inbox')) {
        return 'social';
      }
      return 'general';
    };

    if (typeof factsText === 'string') {
      factsText.split('\n').map(line => line.trim()).filter(Boolean).forEach(line => {
        categories[getCategory(line)].facts.push(line);
      });
    }

    if (typeof inferencesText === 'string') {
      inferencesText.split('\n').map(line => line.trim()).filter(Boolean).forEach(line => {
        categories[getCategory(line)].inferences.push(line);
      });
    }

    return categories;
  };

  const aiData = diag.diagnostic_status !== 'ai_validation_failed'
    ? parseDiagnosticData(diag.observed_facts, diag.inferences)
    : null;

  const emissionDate = diag.generated_at 
    ? new Date(diag.generated_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
    : new Date().toLocaleDateString('pt-BR');

  const leadAddress = lead.formatted_address || lead.address || lead.city || 'Localidade não especificada';
  const leadPhone = lead.national_phone_number || lead.phone;
  const leadWebsite = lead.website_uri || lead.website;
  const leadRating = lead.google_rating ?? lead.rating;
  const leadReviews = lead.google_reviews_count ?? lead.user_rating_count ?? 0;

  return (
    <div className="print-only bg-white text-slate-900 font-sans p-6 print:p-8">
      <style dangerouslySetInnerHTML={{ __html: `
        @page {
          size: A4 portrait;
          margin: 0 !important;
        }
        @media print {
          @page {
            size: A4 portrait;
            margin: 0 !important;
          }
          html, body {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #ffffff !important;
          }
          /* Suprime qualquer link ou URL impresso pelo navegador */
          a[href]:after,
          a[href]:before {
            content: none !important;
          }
          /* Oculta cabeçalhos e rodapés do navegador e elementos de sistema */
          header, footer, nav, aside, .no-print {
            display: none !important;
          }
          body {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          .break-inside-avoid {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
          }
          .page-break-before {
            page-break-before: always !important;
            break-before: always !important;
          }
        }
      `}} />

      {/* ========================================================================= */}
      {/* 1. CABEÇALHO INSTITUCIONAL PREMIUM */}
      {/* ========================================================================= */}
      <div className="border-b-2 border-[#0F2744] pb-3 mb-4 break-inside-avoid">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-[#0F2744] tracking-tight">Automação de Leads</h1>
              <span className="bg-[#0F2744] text-white text-[9px] font-extrabold px-2 py-0.5 rounded tracking-wider uppercase">
                Auditoria Oficial
              </span>
            </div>
            <p className="text-xs text-cyan-800 font-bold uppercase tracking-wider mt-0.5">
              Diagnóstico Consultivo 360° & Maturidade Comercial
            </p>
          </div>
          <div className="text-right text-[10px] text-gray-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg">
            <p className="font-semibold text-gray-800">Emissão: {emissionDate}</p>
            <p className="font-mono text-gray-500">Código: #{lead.id ? lead.id.substring(0, 8).toUpperCase() : 'LEAD'}</p>
          </div>
        </div>

        {/* Faixa do Lead */}
        <div className="mt-3 pt-2.5 border-t border-slate-200 flex flex-wrap justify-between items-center gap-2">
          <div>
            <span className="text-[9px] font-extrabold text-slate-500 uppercase tracking-wider block">Empresa Auditada</span>
            <div className="flex items-baseline gap-2">
              <strong className="text-[#0F2744] text-lg font-black">{lead.name}</strong>
              {(lead.category || lead.city) && (
                <span className="text-xs text-slate-600 font-medium">
                  • {lead.category || 'Comércio Local'} {lead.city ? `(${lead.city})` : ''}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-emerald-50 text-emerald-800 border border-emerald-300 text-[10px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1">
              <CheckCircle2 size={12} className="text-emerald-600" /> Auditoria Validada
            </span>
            {hasGeneratedSite && (
              <span className="bg-cyan-50 text-cyan-800 border border-cyan-300 text-[10px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1">
                <Sparkles size={12} className="text-cyan-600" /> Ativo Digital Disponível
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 2. DESTAQUE FINANCEIRO: VAZAMENTO ESTIMADO DE RECEITA LOCAL */}
      {/* ========================================================================= */}
      {revenueLeak ? (
        <div className="mb-4 rounded-xl border-2 border-rose-300 bg-rose-50/50 p-3.5 break-inside-avoid">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="p-1 rounded-md bg-rose-600 text-white">
                <TrendingDown size={14} />
              </div>
              <h2 className="text-xs font-black uppercase tracking-wider text-rose-950">
                Alerta Comercial: Vazamento Estimado de Receita na Região
              </h2>
            </div>
            <span className="bg-rose-600 text-white text-[9px] font-extrabold px-2 py-0.5 rounded-full uppercase tracking-wider">
              Gravidade: {revenueLeak.loss_severity || 'CRÍTICO'}
            </span>
          </div>

          <p className="text-[11px] text-slate-800 font-medium leading-relaxed mb-3">
            {revenueLeak.summary}
          </p>

          <div className="grid grid-cols-4 gap-2">
            {/* Buscas */}
            <div className="bg-white border border-rose-200 rounded-lg p-2 text-center shadow-xs">
              <div className="flex items-center justify-center gap-1 text-slate-500 mb-0.5">
                <Search size={11} />
                <span className="text-[8px] font-extrabold uppercase tracking-wider">Demanda Local</span>
              </div>
              <p className="text-base font-black text-slate-900 leading-none">
                {revenueLeak.monthly_searches?.low ?? 0}-{revenueLeak.monthly_searches?.high ?? 0}
              </p>
              <p className="text-[8px] text-slate-500 font-medium mt-0.5">buscas/mês no Google</p>
            </div>

            {/* Leads Perdidos */}
            <div className="bg-white border border-rose-200 rounded-lg p-2 text-center shadow-xs">
              <div className="flex items-center justify-center gap-1 text-amber-600 mb-0.5">
                <Users size={11} />
                <span className="text-[8px] font-extrabold uppercase tracking-wider">Leads Perdidos</span>
              </div>
              <p className="text-base font-black text-amber-700 leading-none">
                {revenueLeak.lost_leads_per_month?.low ?? 0}-{revenueLeak.lost_leads_per_month?.high ?? 0}
              </p>
              <p className="text-[8px] text-slate-500 font-medium mt-0.5">orçamentos desviados/mês</p>
            </div>

            {/* Perda Mínima */}
            <div className="bg-white border border-rose-200 rounded-lg p-2 text-center shadow-xs">
              <div className="flex items-center justify-center gap-1 text-rose-600 mb-0.5">
                <DollarSign size={11} />
                <span className="text-[8px] font-extrabold uppercase tracking-wider">Perda Mínima</span>
              </div>
              <p className="text-base font-black text-rose-700 leading-none">
                R$ {(revenueLeak.estimated_revenue_lost?.low || 0).toLocaleString('pt-BR')}
              </p>
              <p className="text-[8px] text-slate-500 font-medium mt-0.5">faturamento perdido/mês</p>
            </div>

            {/* Perda Máxima */}
            <div className="bg-rose-100/70 border border-rose-300 rounded-lg p-2 text-center shadow-xs">
              <div className="flex items-center justify-center gap-1 text-rose-800 mb-0.5">
                <AlertCircle size={11} />
                <span className="text-[8px] font-extrabold uppercase tracking-wider">Perda Máxima</span>
              </div>
              <p className="text-base font-black text-rose-900 leading-none">
                R$ {(revenueLeak.estimated_revenue_lost?.high || 0).toLocaleString('pt-BR')}
              </p>
              <p className="text-[8px] text-rose-700 font-medium mt-0.5">potencial deixado na mesa</p>
            </div>
          </div>
        </div>
      ) : (
        /* Fallback para scores DMS e COS se não houver cálculo de revenue_leak */
        <div className="grid grid-cols-2 gap-3 mb-4 break-inside-avoid">
          <div className="border border-cyan-200 bg-cyan-50/50 p-3 rounded-xl flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-cyan-900 uppercase tracking-wider flex items-center gap-1.5">
                <Activity size={13} /> Maturidade Digital (DMS)
              </h3>
              <p className="text-[9px] text-slate-600 mt-0.5">Avaliação técnica do ecossistema auditado (Site, SEO, GBP).</p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-black text-cyan-700">{lead.dms ?? 0}</span>
              <span className="text-[10px] font-bold text-slate-400">/100</span>
            </div>
          </div>

          <div className="border border-emerald-200 bg-emerald-50/50 p-3 rounded-xl flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
                <Globe size={13} /> Oportunidade Comercial (COS)
              </h3>
              <p className="text-[9px] text-slate-600 mt-0.5">Mede a lacuna de faturamento e potencial de captação local.</p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-black text-emerald-700">{lead.cos ?? 0}</span>
              <span className="text-[10px] font-bold text-slate-400">/100</span>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 3. PAINEL DOS 4 PILARES DA PRESENÇA DIGITAL */}
      {/* ========================================================================= */}
      <div className="mb-4 break-inside-avoid">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-[11px] font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <BarChart3 size={13} className="text-[#0F2744]" /> Auditoria dos 4 Pilares da Presença Digital
          </h2>
          <span className="text-[9px] text-slate-500 font-medium">Dados auditados em tempo real</span>
        </div>

        <div className="grid grid-cols-4 gap-2.5">
          {/* Pilar 1: Google Maps */}
          <div className="border border-blue-200 bg-blue-50/30 p-2.5 rounded-xl flex flex-col justify-between">
            <div>
              <div className="text-[9px] font-bold text-blue-800 uppercase mb-1.5 flex items-center justify-between">
                <span>Google Maps</span>
                <GoogleLogo size={13}/>
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-lg font-black text-slate-900">{leadRating ?? '—'}</span>
                <span className="text-[9px] font-bold text-slate-500">/ 5.0</span>
              </div>
              <div className="flex mt-0.5">{renderStars(leadRating)}</div>
              <div className="text-[9px] text-slate-600 mt-1 font-medium">{leadReviews} avaliações reais</div>
            </div>
            <div className="mt-2 pt-2 border-t border-blue-100 text-[8px] text-slate-600 space-y-0.5">
              <div>Telefone: <span className={leadPhone ? "text-emerald-700 font-bold" : "text-rose-600 font-bold"}>{leadPhone ? '✓ Presente' : '✗ Ausente'}</span></div>
              <div>Endereço: <span className={leadAddress ? "text-emerald-700 font-bold" : "text-rose-600 font-bold"}>{leadAddress ? '✓ Presente' : '✗ Ausente'}</span></div>
            </div>
          </div>

          {/* Pilar 2: Website & Performance */}
          <div className={`p-2.5 rounded-xl flex flex-col justify-between border ${leadWebsite ? 'border-cyan-200 bg-cyan-50/30' : 'border-rose-300 bg-rose-50/40'}`}>
            <div>
              <div className="text-[9px] font-bold uppercase mb-1.5 flex items-center justify-between text-cyan-800">
                <span>Website & SEO</span>
                <Globe size={13}/>
              </div>
              {leadWebsite ? (
                <>
                  <div className="flex items-baseline gap-1">
                    <span className="text-lg font-black text-slate-900">{lead.pagespeed_score ?? '—'}</span>
                    <span className="text-[9px] font-bold text-slate-500">/100</span>
                  </div>
                  <div className="text-[9px] text-slate-600 mt-0.5">Lighthouse Score</div>
                </>
              ) : (
                <div className="text-rose-700 font-bold text-[9px] flex items-center gap-1 mt-1">
                  <AlertTriangle size={12} className="text-rose-600 shrink-0" />
                  <span>Sem Site Próprio</span>
                </div>
              )}
            </div>
            <div className="mt-2 pt-2 border-t border-slate-100 text-[8px] text-slate-600">
              {leadWebsite ? (
                <>
                  <div>LCP: <span className="font-bold">{lead.lcp_ms != null ? `${(lead.lcp_ms / 1000).toFixed(1)}s` : '—'}</span></div>
                  <div>SEO: <span className="font-bold">{lead.seo_score ?? '—'}/100</span></div>
                </>
              ) : (
                <div className="text-rose-800 font-semibold leading-tight">
                  100% dos cliques dependem de canais de terceiros.
                </div>
              )}
            </div>
          </div>

          {/* Pilar 3: Instagram */}
          <div className="border border-pink-200 bg-pink-50/30 p-2.5 rounded-xl flex flex-col justify-between">
            <div>
              <div className="text-[9px] font-bold text-pink-800 uppercase mb-1.5 flex items-center justify-between">
                <span>Instagram</span>
                <InstagramLogo size={13}/>
              </div>
              <div className={`text-[9px] font-bold mb-1 ${lead.has_instagram ? 'text-emerald-700' : 'text-slate-500'}`}>
                {lead.has_instagram ? '✓ Perfil Mapeado' : '✗ Sem Perfil Ativo'}
              </div>
              {lead.has_instagram && (
                <div className="text-[9px] text-slate-600">
                  {lead.social_last_post_days != null ? `Post: há ${lead.social_last_post_days} dias` : 'Atividade recente'}
                </div>
              )}
            </div>
            <div className="mt-2 pt-2 border-t border-pink-100 text-[8px] font-bold text-center">
              {lead.has_instagram 
                ? (lead.social_last_post_days != null && lead.social_last_post_days > 30 
                    ? <span className="text-amber-700">⏳ Falta Frequência</span> 
                    : <span className="text-emerald-700">🔥 Presença Local</span>) 
                : <span className="text-slate-500">⚠️ Gap de Engajamento</span>}
            </div>
          </div>

          {/* Pilar 4: LinkedIn */}
          <div className="border border-indigo-200 bg-indigo-50/30 p-2.5 rounded-xl flex flex-col justify-between">
            <div>
              <div className="text-[9px] font-bold text-indigo-800 uppercase mb-1.5 flex items-center justify-between">
                <span>LinkedIn</span>
                <LinkedinLogo size={13}/>
              </div>
              <div className={`text-[9px] font-bold mb-1 ${lead.has_linkedin ? 'text-emerald-700' : 'text-slate-500'}`}>
                {lead.has_linkedin ? '✓ Perfil Corporativo' : '✗ Não Prioritário'}
              </div>
              <div className="text-[8px] text-slate-500 mt-0.5 leading-tight">
                {lead.has_linkedin ? 'Autoridade B2B ativa.' : 'Foco em captação B2C/Local.'}
              </div>
            </div>
            <div className="mt-2 pt-2 border-t border-indigo-100 text-[8px] font-bold text-center text-slate-600">
              {lead.has_linkedin ? '💼 Presença B2B' : '🌐 Foco Direto ao Cliente'}
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 4. GAFES COMERCIAIS CRÍTICAS IDENTIFICADAS */}
      {/* ========================================================================= */}
      {criticalBlunders.length > 0 && (
        <div className="mb-4 break-inside-avoid">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-[11px] font-black text-rose-900 uppercase tracking-wider flex items-center gap-1.5">
              <ShieldAlert size={13} className="text-rose-600" />
              Gafes Comerciais Críticas que Custam Clientes ({criticalBlunders.length})
            </h2>
            <span className="text-[8px] font-bold text-rose-600 uppercase tracking-wider bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
              Gargalos Diretos no Funil
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {criticalBlunders.slice(0, 4).map((blunder, idx) => {
              const isCrit = blunder.severity === 'CRITICAL';
              return (
                <div 
                  key={idx} 
                  className={`p-2.5 rounded-xl border ${isCrit ? 'border-rose-300 bg-rose-50/40' : 'border-amber-200 bg-amber-50/30'} flex flex-col justify-between`}
                >
                  <div>
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <h4 className="text-[10px] font-black text-slate-900 leading-tight">
                        {blunder.title}
                      </h4>
                      <span className={`text-[8px] font-extrabold uppercase px-1.5 py-0.2 rounded border shrink-0 ${
                        isCrit ? 'bg-rose-600 text-white border-rose-600' : 'bg-amber-500 text-white border-amber-500'
                      }`}>
                        {blunder.severity}
                      </span>
                    </div>

                    <p className="text-[9px] text-slate-700 leading-relaxed mb-1.5 font-medium">
                      {blunder.detected_reason || blunder.description}
                    </p>
                  </div>

                  <div className="pt-1.5 border-t border-slate-200/70 space-y-0.5 text-[8.5px]">
                    <div className="text-rose-800 flex items-start gap-1 font-semibold">
                      <span className="shrink-0 text-rose-600">📉</span>
                      <span>Impacto: {blunder.financial_impact}</span>
                    </div>
                    <div className="text-emerald-800 flex items-start gap-1 font-bold">
                      <span className="shrink-0 text-emerald-600">✅</span>
                      <span>Solução: {blunder.lp_solution}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 5. MATRIZ DE TRANSFORMAÇÃO: COMO A NOVA SOLUÇÃO RESOLVE */}
      {/* ========================================================================= */}
      {transformationMatrix.length > 0 && (
        <div className="mb-4 break-inside-avoid">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-[11px] font-black text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
              <Zap size={13} className="text-emerald-600" />
              Matriz de Transformação: Como a Nova Landing Page Resolve
            </h2>
            <span className="text-[8px] font-bold text-emerald-700 uppercase tracking-wider bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Retorno Rápido sobre Investimento
            </span>
          </div>

          <div className="space-y-1.5">
            {transformationMatrix.slice(0, 3).map((item, idx) => (
              <div key={idx} className="p-2 rounded-xl border border-slate-200 bg-slate-50/70 grid grid-cols-12 gap-2 items-center text-[9px]">
                <div className="col-span-4 border-r border-slate-200 pr-2">
                  <div className="text-rose-700 font-extrabold uppercase text-[8px] flex items-center gap-1 mb-0.5">
                    <span>❌ Problema Atual</span>
                  </div>
                  <p className="font-bold text-slate-800 leading-tight">{item.problem}</p>
                  <p className="text-[8px] text-slate-500 mt-0.5">{item.detected_detail}</p>
                </div>

                <div className="col-span-5 border-r border-slate-200 pr-2">
                  <div className="text-emerald-700 font-extrabold uppercase text-[8px] flex items-center gap-1 mb-0.5">
                    <span>✅ Solução da Landing Page</span>
                  </div>
                  <p className="text-slate-800 font-medium leading-tight">{item.lp_solution}</p>
                </div>

                <div className="col-span-3 text-center bg-white p-1.5 rounded-lg border border-slate-200">
                  <div className="text-cyan-700 font-extrabold uppercase text-[8px] mb-0.5">
                    📈 Ganho Previsto
                  </div>
                  <p className="font-black text-slate-900 leading-tight text-[8.5px]">{item.expected_gain}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 6. INSIGHT DO NICHO & PROPOSTA DE VALOR */}
      {/* ========================================================================= */}
      {(nicheInsights || valueProposition || salesApproach) && (
        <div className="grid grid-cols-2 gap-2.5 mb-4 break-inside-avoid">
          {valueProposition && (
            <div className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200">
              <span className="text-[8.5px] font-black text-cyan-900 uppercase tracking-wider block mb-1 flex items-center gap-1">
                <span>💎</span> Proposta de Valor Central
              </span>
              <p className="text-[9.5px] text-slate-800 font-bold leading-relaxed">
                {formatBoldText(valueProposition)}
              </p>
            </div>
          )}

          {nicheInsights && (
            <div className="p-2.5 rounded-xl bg-purple-50/70 border border-purple-200">
              <span className="text-[8.5px] font-black text-purple-900 uppercase tracking-wider block mb-1 flex items-center gap-1">
                <span>🧠</span> Inteligência de Mercado no Nicho
              </span>
              <p className="text-[9px] text-slate-700 font-medium leading-relaxed">
                {formatBoldText(nicheInsights)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* 7. ANÁLISE QUALITATIVA DA IA (FATOS E INFERÊNCIAS) */}
      {/* ========================================================================= */}
      {aiData && (
        <div className="mb-4 break-inside-avoid">
          <h3 className="text-[10px] font-black text-slate-800 uppercase tracking-wider mb-2">
            Análise Qualitativa de Fatos e Inferências (Gemini AI Audit)
          </h3>
          <div className="grid grid-cols-3 gap-2">
            {['website', 'google', 'social'].map((key) => {
              const cat = aiData[key];
              if (!cat || (cat.facts.length === 0 && cat.inferences.length === 0)) return null;

              const borderColors = { website: 'border-cyan-200', google: 'border-blue-200', social: 'border-pink-200' };
              const bgColors = { website: 'bg-cyan-50/50', google: 'bg-blue-50/50', social: 'bg-pink-50/50' };
              const textColors = { website: 'text-cyan-900', google: 'text-blue-900', social: 'text-pink-900' };

              return (
                <div key={key} className={`border ${borderColors[key]} rounded-lg overflow-hidden flex flex-col bg-white`}>
                  <div className={`${bgColors[key]} ${textColors[key]} px-2.5 py-1 text-[9px] font-black uppercase border-b ${borderColors[key]}`}>
                    {cat.icon} {cat.title}
                  </div>
                  <div className="p-2 text-[8.5px] flex-1 space-y-2">
                    {cat.facts.length > 0 && (
                      <div>
                        <span className="font-extrabold uppercase text-slate-400 block mb-0.5 text-[7.5px]">📋 Fatos Verificados</span>
                        <ul className="text-slate-700 space-y-0.5">
                          {cat.facts.slice(0, 3).map((fact, idx) => (
                            <li key={idx} className="leading-tight">• {formatBoldText(fact.replace(/^[-*•\s\d\.)]+\s*/, ''))}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {cat.inferences.length > 0 && (
                      <div className="pt-1.5 border-t border-slate-100">
                        <span className="font-extrabold uppercase text-slate-400 block mb-0.5 text-[7.5px]">💡 Análise de Impacto</span>
                        <div className="space-y-1">
                          {cat.inferences.slice(0, 2).map((inf, idx) => (
                            <p key={idx} className="text-slate-600 bg-slate-50 p-1 rounded border border-slate-100 leading-tight">
                              {formatBoldText(inf.replace(/^[-*•\s\d\.)]+\s*/, ''))}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 8. O ATIVO DIGITAL ENTREGUE SOB MEDIDA */}
      {/* ========================================================================= */}
      <div className="mb-4 break-inside-avoid">
        <div className="bg-[#0F2744] rounded-xl p-3.5 text-white shadow-sm border border-slate-800">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5 border-b border-white/10 pb-2">
            <div className="flex items-center gap-2">
              <Sparkles size={14} className="text-cyan-400" />
              <h3 className="text-xs font-black uppercase tracking-wider text-white">
                O Novo Ativo Digital Desenvolvido Sob Medida
              </h3>
            </div>
            {hasGeneratedSite && (
              <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[9px] font-extrabold px-2 py-0.5 rounded-full uppercase tracking-wider">
                Pronto para Ativação no Domínio
              </span>
            )}
          </div>

          <p className="text-[10px] text-slate-300 mb-3 font-medium leading-relaxed">
            Para estancar imediatamente as gafes comerciais diagnosticadas e capturar os orçamentos que vazam para concorrentes, 
            estruturamos a máquina de conversão sob medida para <strong>{lead.name}</strong>:
          </p>

          <div className="grid grid-cols-3 gap-2.5">
            <div className="bg-white/5 p-2 rounded-lg border border-white/10">
              <span className="text-cyan-400 font-extrabold text-[9.5px] block mb-0.5">⚡ Velocidade Extrema (PageSpeed 95+)</span>
              <p className="text-[8.5px] text-slate-300 leading-relaxed">Carregamento instantâneo em 3G/4G sem perda de visitantes por lentidão no celular.</p>
            </div>
            <div className="bg-white/5 p-2 rounded-lg border border-white/10">
              <span className="text-emerald-400 font-extrabold text-[9.5px] block mb-0.5">🎯 Botão WhatsApp em 1 Clique</span>
              <p className="text-[8.5px] text-slate-300 leading-relaxed">Botão flutuante com mensagem pré-configurada apontando direto para o WhatsApp da equipe.</p>
            </div>
            <div className="bg-white/5 p-2 rounded-lg border border-white/10">
              <span className="text-amber-400 font-extrabold text-[9.5px] block mb-0.5">🏆 Prova Social & Autoridade Local</span>
              <p className="text-[8.5px] text-slate-300 leading-relaxed">Exibição de destaque da nota {leadRating || '5.0'}★ do Google Maps com catálogo de serviços do nicho.</p>
            </div>
          </div>

          {/* Se houver dados de cores da marca ou sócios identificados */}
          {(brandColors || ownersInfo.length > 0) && (
            <div className="mt-2.5 pt-2 border-t border-white/10 flex flex-wrap items-center justify-between text-[9px] text-slate-300">
              {brandColors && (
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-400 font-bold">Identidade Visual Calibrada:</span>
                  <div className="flex items-center gap-1">
                    {brandColors.primary && (
                      <span className="inline-block w-3 h-3 rounded-full border border-white/30" style={{ backgroundColor: brandColors.primary }} title={`Primária: ${brandColors.primary}`} />
                    )}
                    {brandColors.secondary && (
                      <span className="inline-block w-3 h-3 rounded-full border border-white/30" style={{ backgroundColor: brandColors.secondary }} title={`Secundária: ${brandColors.secondary}`} />
                    )}
                    {brandColors.accent && (
                      <span className="inline-block w-3 h-3 rounded-full border border-white/30" style={{ backgroundColor: brandColors.accent }} title={`Destaque: ${brandColors.accent}`} />
                    )}
                  </div>
                </div>
              )}
              {ownersInfo.length > 0 && (
                <div className="text-[8.5px] text-slate-300">
                  <span className="text-slate-400 font-bold">Liderança Identificada: </span>
                  <span>{ownersInfo.map(o => o.name).join(', ')}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 9. PRÓXIMOS PASSOS ESTRATÉGICOS (PLANO DE ESCALA) */}
      {/* ========================================================================= */}
      <div className="mb-4 break-inside-avoid">
        <h2 className="text-[10px] font-black text-slate-800 uppercase tracking-wider border-b border-slate-200 pb-1 mb-2">
          Próximos Passos Estratégicos (Plano de Escala & Crescimento)
        </h2>
        <div className="grid grid-cols-2 gap-2.5">
          <div className="flex gap-2.5 items-start border border-slate-200 p-2.5 rounded-lg bg-slate-50/60">
            <div className="bg-blue-100 text-blue-800 p-1.5 rounded shrink-0">
              <Globe size={14} />
            </div>
            <div>
              <h4 className="text-[9.5px] font-bold text-slate-900 leading-tight">1. Publicação & Ativação de Domínio</h4>
              <p className="text-[8.5px] text-slate-600 mt-0.5 leading-relaxed">
                Conectar a nova Landing Page ao domínio oficial da empresa e ao link oficial do Perfil da Empresa no Google (Maps).
              </p>
            </div>
          </div>

          <div className="flex gap-2.5 items-start border border-slate-200 p-2.5 rounded-lg bg-slate-50/60">
            <div className="bg-emerald-100 text-emerald-800 p-1.5 rounded shrink-0">
              <Zap size={14} />
            </div>
            <div>
              <h4 className="text-[9.5px] font-bold text-slate-900 leading-tight">2. Campanhas Locais de Alta Intenção</h4>
              <p className="text-[8.5px] text-slate-600 mt-0.5 leading-relaxed">
                Direcionar as buscas ativas de clientes na região via Google Ads direto para a nova página otimizada para WhatsApp.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 10. METODOLOGIA E FONTES DE DADOS OFICIAIS */}
      {/* ========================================================================= */}
      <div className="pt-2 border-t border-slate-200 break-inside-avoid text-slate-500">
        <div className="flex justify-between items-center text-[8px] font-bold uppercase tracking-wider mb-1">
          <span>Metodologia & Transparência Técnica</span>
          <span>Documento Executivo Confidencial</span>
        </div>
        <p className="text-[7.5px] leading-relaxed text-justify">
          <strong>Aviso de Conformidade:</strong> As métricas técnicas de performance e SEO apresentadas neste relatório foram obtidas diretamente através da <strong>API Oficial do Google Lighthouse / PageSpeed Insights</strong>. Os dados de reputação refletem o estado público indexado via <strong>Google Places API (Google Maps)</strong> na data de emissão. A correlação de impacto financeiro e análise de mercado foi processada por modelos de inteligência artificial de ponta (Gemini AI) com base em métricas reais do mercado local.
        </p>
      </div>

      {/* Rodapé Executivo White-label */}
      <div className="mt-4 pt-2 border-t border-slate-200/80 flex justify-between items-center text-[8px] text-slate-400 font-semibold uppercase tracking-wider break-inside-avoid">
        <span>Automação de Leads • Auditoria de Presença Digital & Performance</span>
        <span>Documento emitido para uso exclusivo de {lead.name}</span>
      </div>

    </div>
  );
}
