'use client';

import React from 'react';
import { Activity, Globe, MapPin, AlertTriangle } from 'lucide-react';

const GoogleLogo = ({ size = 18, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
);

const InstagramLogo = ({ size = 18, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <defs>
      <linearGradient id="ig-grad" x1="2" y1="22" x2="22" y2="2" gradientUnits="userSpaceOnUse">
        <stop stopColor="#FEE411"/>
        <stop offset="0.1" stopColor="#FDF030"/>
        <stop offset="0.5" stopColor="#FD5949"/>
        <stop offset="0.75" stopColor="#D6249F"/>
        <stop offset="1" stopColor="#285AEB"/>
      </linearGradient>
    </defs>
    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 10-2.881.001 1.44 1.44 0 002.881-.001z" fill="url(#ig-grad)"/>
  </svg>
);

const LinkedinLogo = ({ size = 18, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" fill="#0A66C2"/>
  </svg>
);

const formatBoldText = (text) => {
  if (typeof text !== 'string') return text;
  const parts = text.split(/\*\*([^*]+)\*\*/g);
  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return <strong key={index} className="font-bold text-gray-900">{part}</strong>;
    }
    return part;
  });
};

export default function PrintReport({ lead, diagnostic }) {
  if (!lead) return null;

  // Render Stars function
  const renderStars = (rating) => {
    const full = Math.floor(rating || 0);
    const half = (rating || 0) % 1 >= 0.5;
    const stars = [];
    for (let i = 0; i < 5; i++) {
      if (i < full) {
        stars.push(<span key={i} className="text-yellow-400 text-lg">★</span>);
      } else if (i === full && half) {
        stars.push(<span key={i} className="text-yellow-400 text-lg">★</span>);
      } else {
        stars.push(<span key={i} className="text-gray-300 text-lg">★</span>);
      }
    }
    return stars;
  };

  // Parse AI Diagnostic
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

  const aiData = diagnostic && diagnostic.diagnostic_status !== 'ai_validation_failed' 
    ? parseDiagnosticData(diagnostic.observed_facts, diagnostic.inferences)
    : null;

  return (
    <div className="print-only bg-white text-gray-900 font-sans p-2">
      {/* 1. Cabeçalho */}
      <div className="border-b-2 border-[#0F2744] pb-4 mb-6">
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-2xl font-extrabold text-[#0F2744]">CONSULTINGS APD</h1>
            <p className="text-xs text-cyan-700 font-bold uppercase tracking-wider">Maturidade Digital & Oportunidade Comercial</p>
          </div>
          <div className="text-right text-xs text-gray-500">
            <p className="font-medium">Data de Emissão: {new Date().toLocaleDateString('pt-BR')}</p>
            <p>Código do Lead: {lead.id.substring(0, 8).toUpperCase()}</p>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-3 font-medium border-t border-gray-100 pt-2">
          Documento Estratégico de Entrega de Ativo Digital preparado para: <strong className="text-[#0F2744] text-base">{lead.name}</strong>
        </p>
      </div>

      {/* 2. Resumo de Scores Principais (DMS e COS) */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="border border-cyan-200 bg-cyan-50/40 p-4 rounded-xl flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold text-cyan-800 uppercase tracking-wider flex items-center gap-1.5">
              <Activity size={14} /> Maturidade Digital (DMS)
            </h3>
            <p className="text-[10px] text-gray-600 mt-1 max-w-[85%]">Avaliação técnica do seu antigo ecossistema (Site, SEO, GBP e Redes).</p>
          </div>
          <div className="text-right">
            <span className="text-4xl font-extrabold text-cyan-600">{lead.dms ?? 0}</span>
            <span className="text-xs font-semibold text-gray-400">/100</span>
          </div>
        </div>

        <div className="border border-emerald-200 bg-emerald-50/40 p-4 rounded-xl flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1.5">
              <Globe size={14} /> Oportunidade (COS)
            </h3>
            <p className="text-[10px] text-gray-600 mt-1 max-w-[85%]">Mede a lacuna de vendas e potencial financeiro da sua região.</p>
          </div>
          <div className="text-right">
            <span className="text-4xl font-extrabold text-emerald-600">{lead.cos ?? 0}</span>
            <span className="text-xs font-semibold text-gray-400">/100</span>
          </div>
        </div>
      </div>

      {/* 3. Dashboard dos 4 Pilares */}
      <h2 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-3">Painel de Auditoria (Antes da Entrega)</h2>
      <div className="grid grid-cols-4 gap-3 mb-6">
        {/* Google */}
        <div className="border border-blue-200 p-3 rounded-xl flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold text-blue-700 uppercase mb-2 flex items-center justify-between">
              <span>Google Maps</span>
              <GoogleLogo size={14}/>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-extrabold text-gray-900">{lead.google_rating ?? '—'}</span>
              <span className="text-[10px] text-gray-500">/ 5.0</span>
            </div>
            <div className="flex mt-0.5">{renderStars(lead.google_rating)}</div>
            <div className="text-[10px] text-gray-600 mt-1">{lead.google_reviews_count ?? 0} avaliações</div>
          </div>
          <div className="mt-3 pt-2 border-t border-gray-100 text-[9px] text-gray-500">
            <div>Telefone: <span className={lead.phone ? "text-emerald-600 font-bold" : "text-gray-400"}>{lead.phone ? '✓ Presente' : '✗ Ausente'}</span></div>
            <div>Endereço: <span className={lead.address ? "text-emerald-600 font-bold" : "text-gray-400"}>{lead.address ? '✓ Presente' : '✗ Ausente'}</span></div>
          </div>
        </div>

        {/* Website */}
        <div className="border border-cyan-200 p-3 rounded-xl flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold text-cyan-700 uppercase mb-2 flex items-center justify-between">
              <span>Website & SEO</span>
              <Globe size={14}/>
            </div>
            {lead.has_website ? (
              <>
                <div className="flex items-baseline gap-1">
                  <span className="text-xl font-extrabold text-gray-900">{lead.pagespeed_score ?? '—'}</span>
                  <span className="text-[10px] text-gray-500">/100</span>
                </div>
                <div className="text-[10px] text-gray-600 mt-1">PageSpeed Score</div>
              </>
            ) : (
              <div className="text-rose-600 font-bold text-[10px] flex items-center gap-1"><AlertTriangle size={12}/> Sem Website</div>
            )}
          </div>
          <div className="mt-3 pt-2 border-t border-gray-100 text-[9px] text-gray-500">
            {lead.has_website ? (
              <>
                <div>LCP: <span className="font-bold">{lead.lcp_ms != null ? `${(lead.lcp_ms / 1000).toFixed(1)}s` : '—'}</span></div>
                <div>SEO: <span className="font-bold">{lead.seo_score != null ? lead.seo_score : '—'}</span></div>
              </>
            ) : (
              <div className="italic">Ausência grave de presença online própria.</div>
            )}
          </div>
        </div>

        {/* Instagram */}
        <div className="border border-pink-200 p-3 rounded-xl flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold text-pink-700 uppercase mb-2 flex items-center justify-between">
              <span>Instagram</span>
              <InstagramLogo size={14}/>
            </div>
            <div className={`text-[10px] font-bold mb-1 ${lead.has_instagram ? 'text-emerald-600' : 'text-gray-500'}`}>
              {lead.has_instagram ? '✓ Perfil Ativo' : '✗ Sem Perfil'}
            </div>
            {lead.has_instagram && (
              <div className="text-[10px] text-gray-600">Último post: {lead.social_last_post_days != null ? `${lead.social_last_post_days} dias` : '—'}</div>
            )}
          </div>
          <div className="mt-3 pt-2 border-t border-gray-100 text-[9px] font-bold text-center">
            {lead.has_instagram 
              ? (lead.social_last_post_days < 30 ? <span className="text-emerald-600">🔥 Presença Ativa</span> : <span className="text-amber-600">⏳ Falta Frequência</span>) 
              : <span className="text-gray-500">⚠️ Grande Gap Social</span>}
          </div>
        </div>

        {/* LinkedIn */}
        <div className="border border-indigo-200 p-3 rounded-xl flex flex-col justify-between">
          <div>
            <div className="text-[10px] font-bold text-indigo-700 uppercase mb-2 flex items-center justify-between">
              <span>LinkedIn</span>
              <LinkedinLogo size={14}/>
            </div>
            <div className={`text-[10px] font-bold mb-1 ${lead.has_linkedin ? 'text-emerald-600' : 'text-gray-400'}`}>
              {lead.has_linkedin ? '✓ Perfil Corporativo' : '✗ Sem Perfil'}
            </div>
            <div className="text-[9px] text-gray-500 mt-1">
              {lead.has_linkedin ? 'Conexão B2B ativa.' : 'Foco atual no varejo/B2C.'}
            </div>
          </div>
          <div className="mt-3 pt-2 border-t border-gray-100 text-[9px] font-bold text-gray-500 text-center">
            {lead.has_linkedin ? '💼 Conexão B2B' : '🌐 Foco Offline/B2C'}
          </div>
        </div>
      </div>

      {/* 4. Análise da Inteligência Artificial */}
      {aiData && (
        <div className="mb-8 break-inside-avoid">
          <h3 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-3">
            Análise Avançada e Impacto nos Negócios
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['website', 'google', 'social'].map((key) => {
              const cat = aiData[key];
              if (!cat || (cat.facts.length === 0 && cat.inferences.length === 0)) return null;
              
              const borderColors = { website: 'border-cyan-200', google: 'border-blue-200', social: 'border-pink-200' };
              const bgColors = { website: 'bg-cyan-50/50', google: 'bg-blue-50/50', social: 'bg-pink-50/50' };
              const textColors = { website: 'text-cyan-800', google: 'text-blue-800', social: 'text-pink-800' };

              return (
                <div key={key} className={`border ${borderColors[key]} rounded-lg overflow-hidden flex flex-col`}>
                  <div className={`${bgColors[key]} ${textColors[key]} px-3 py-2 text-[10px] font-bold uppercase border-b ${borderColors[key]}`}>
                    {cat.icon} {cat.title}
                  </div>
                  <div className="p-3 text-[10px] flex-1">
                    {cat.facts.length > 0 && (
                      <div className="mb-3">
                        <span className="font-extrabold uppercase text-gray-400 block mb-1 text-[9px]">📋 Fatos Identificados</span>
                        <ul className="text-gray-700 space-y-1">
                          {cat.facts.map((fact, idx) => (
                            <li key={idx}>• {formatBoldText(fact.replace(/^[-*•\s\d\.)]+\s*/, ''))}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {cat.inferences.length > 0 && (
                      <div className={`pt-2 ${cat.facts.length > 0 ? 'border-t border-gray-100' : ''}`}>
                        <span className="font-extrabold uppercase text-gray-400 block mb-1 text-[9px]">💡 Análise de Impacto</span>
                        <div className="space-y-1">
                          {cat.inferences.map((inf, idx) => (
                            <p key={idx} className="text-gray-600 bg-gray-50 p-2 rounded border border-gray-100">
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

      {/* 5. A Solução Entregue */}
      <div className="mb-8 break-inside-avoid">
        <h2 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-3">
          O Ativo Digital Entregue Hoje
        </h2>
        <div className="bg-[#0F2744] rounded-xl p-5 text-white shadow-sm border border-gray-800 relative overflow-hidden">
          <div className="relative z-10">
            <p className="text-[11px] text-gray-300 mb-4 font-medium">
              Para resolver os gargalos diagnosticados acima e capturar a grande oportunidade comercial da sua região, desenvolvemos e entregamos sua nova máquina de conversão:
            </p>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white/5 p-3 rounded border border-white/10">
                <span className="text-cyan-400 font-bold text-[11px] block mb-1">⚡ Ultra Rápido</span>
                <p className="text-[9px] text-gray-400 leading-relaxed">Tempo de carregamento otimizado. Retém a atenção do usuário sem travamentos no celular.</p>
              </div>
              <div className="bg-white/5 p-3 rounded border border-white/10">
                <span className="text-emerald-400 font-bold text-[11px] block mb-1">🎯 Foco em Conversão</span>
                <p className="text-[9px] text-gray-400 leading-relaxed">Design focado em captar contatos, com botões de WhatsApp flutuantes e acesso facilitado.</p>
              </div>
              <div className="bg-white/5 p-3 rounded border border-white/10">
                <span className="text-blue-400 font-bold text-[11px] block mb-1">🔍 SEO Ready</span>
                <p className="text-[9px] text-gray-400 leading-relaxed">Código 100% legível pelo Google, preparando o terreno para aumentar as buscas orgânicas pelo seu serviço.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 6. Próximos Passos (Upsell) */}
      <div className="break-inside-avoid">
        <h2 className="text-xs font-bold text-gray-800 uppercase tracking-wider border-b border-gray-200 pb-1 mb-3">
          Próximos Passos Estratégicos (Plano de Escala)
        </h2>
        <p className="text-[11px] text-gray-600 mb-4">
          Com a base tecnológica perfeitamente construída, o próximo objetivo é injetar tráfego qualificado para multiplicar seus contatos. Recomendamos as seguintes ações para o próximo trimestre:
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex gap-3 items-start border border-gray-200 p-3 rounded-lg bg-gray-50">
            <div className="bg-blue-100 text-blue-700 p-2 rounded shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
            </div>
            <div>
              <h4 className="text-[10px] font-bold text-gray-900">Google Ads (Campanhas de Busca)</h4>
              <p className="text-[9px] text-gray-600 mt-1">Lançar campanhas de pesquisa ativadas quando o cliente busca pelos seus serviços na cidade, enviando tráfego direto para o novo site.</p>
            </div>
          </div>
          <div className="flex gap-3 items-start border border-gray-200 p-3 rounded-lg bg-gray-50">
            <div className="bg-pink-100 text-pink-700 p-2 rounded shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path></svg>
            </div>
            <div>
              <h4 className="text-[10px] font-bold text-gray-900">Estratégia de Redes Sociais</h4>
              <p className="text-[9px] text-gray-600 mt-1">Alinhar o conteúdo do Instagram à comunicação do novo site, criando um funil contínuo de conversão.</p>
            </div>
          </div>
        </div>
      </div>


      {/* 7. Metodologia e Fontes */}
      <div className="mt-8 pt-4 border-t border-gray-200 break-inside-avoid">
        <h2 className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-2">
          Transparência e Fontes de Dados
        </h2>
        <p className="text-[9px] text-gray-500 leading-relaxed text-justify">
          <strong>Nota de Credibilidade:</strong> Todas as métricas técnicas (PageSpeed, LCP, SEO) apresentadas neste documento não são estimativas. Elas foram extraídas de forma autônoma através dos servidores da <strong>API Oficial do Google Lighthouse / PageSpeed Insights</strong>. Os dados de reputação (Avaliações e Notas) refletem o estado público indexado via <strong>Google Business Profile (Maps)</strong> na data de emissão. A inteligência de correlação de impacto financeiro (Fatos e Inferências) foi processada por modelos de inteligência artificial de ponta (Gemini API) com base nas métricas brutas.
        </p>
      </div>

    </div>
  );
}
