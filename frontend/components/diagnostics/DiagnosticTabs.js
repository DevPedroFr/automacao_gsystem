'use client';

import { useState } from 'react';

const tabs = [
  { key: 'panel', label: 'Painel de Diagnóstico', icon: '📊' },
  { key: 'recommendations', label: 'Recomendações de Venda', icon: '🎯' },
  { key: 'stitch', label: 'Prompt Google Stitch ⚡', icon: '🛠️' },
];

export default function DiagnosticTabs({ diagnostic = {} }) {
  const [activeTab, setActiveTab] = useState('panel');
  const [copiedTab, setCopiedTab] = useState(null);

  /**
   * Converte marcações simples de **negrito** do Markdown para tags HTML strong
   */
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

  /**
   * Agrupa e estrutura os fatos e as inferências por pilares da presença digital
   */
  const parseDiagnosticData = (factsText, inferencesText) => {
    const categories = {
      google: { title: 'Google Empresa & Local', icon: '📍', facts: [], inferences: [] },
      website: { title: 'Website, Performance & SEO', icon: '🌐', facts: [], inferences: [] },
      social: { title: 'Redes Sociais & Engajamento', icon: '📱', facts: [], inferences: [] },
      general: { title: 'Outras Observações', icon: '🔍', facts: [], inferences: [] }
    };

    const getCategory = (text) => {
      const t = text.toLowerCase();
      if (t.includes('google') || t.includes('rating') || t.includes('avaliaç') || t.includes('gbp') || t.includes('maps') || t.includes('reviews') || t.includes('comentário') || t.includes('telefone') || t.includes('endereço')) {
        return 'google';
      }
      if (t.includes('site') || t.includes('website') || t.includes('pagespeed') || t.includes('lcp') || t.includes('inp') || t.includes('cls') || t.includes('velocidade') || t.includes('performance') || t.includes('seo') || t.includes('vitals') || t.includes('landing page')) {
        return 'website';
      }
      if (t.includes('instagram') || t.includes('facebook') || t.includes('linkedin') || t.includes('social') || t.includes('redes') || t.includes('post') || t.includes('publicaç') || t.includes('inbox')) {
        return 'social';
      }
      return 'general';
    };

    if (typeof factsText === 'string') {
      factsText.split('\n').map(line => line.trim()).filter(Boolean).forEach(line => {
        const cat = getCategory(line);
        categories[cat].facts.push(line);
      });
    }

    if (typeof inferencesText === 'string') {
      inferencesText.split('\n').map(line => line.trim()).filter(Boolean).forEach(line => {
        const cat = getCategory(line);
        categories[cat].inferences.push(line);
      });
    }

    return categories;
  };

  const categories = parseDiagnosticData(diagnostic.observed_facts, diagnostic.inferences);

  const contentMap = {
    panel: `Fatos Observados:\n${diagnostic.observed_facts || ''}\n\nInferências da IA:\n${diagnostic.inferences || ''}`,
    recommendations: diagnostic.recommendations || 'Nenhum dado disponível.',
    stitch: diagnostic.stitch_prompt || 'Nenhum prompt gerado.',
  };

  const handleCopy = async (key) => {
    try {
      const textToCopy = contentMap[key];
      await navigator.clipboard.writeText(textToCopy);
      setCopiedTab(key);
      setTimeout(() => setCopiedTab(null), 2000);
    } catch (err) {
      console.error('Erro ao copiar texto:', err);
    }
  };

  /**
   * Componente interno que renderiza o dashboard visual de 3 pilares
   */
  const renderDashboardPanel = (categoriesData) => {
    const activeCats = Object.entries(categoriesData).filter(([_, cat]) => cat.facts.length > 0 || cat.inferences.length > 0);

    if (activeCats.length === 0) {
      return <p className="text-gray-400 italic text-center py-6">Nenhum dado de diagnóstico disponível.</p>;
    }

    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 print:grid-cols-3 print:gap-4">
        {activeCats.map(([key, cat]) => {
          let borderClass = 'border-blue-200';
          let bgHeader = 'bg-blue-50 text-blue-800';
          let iconBg = 'bg-blue-100 text-blue-600';
          let markerColor = 'text-blue-500';

          if (key === 'website') {
            borderClass = 'border-cyan-200';
            bgHeader = 'bg-cyan-50 text-cyan-800';
            iconBg = 'bg-cyan-100 text-cyan-600';
            markerColor = 'text-cyan-500';
          } else if (key === 'social') {
            borderClass = 'border-pink-200';
            bgHeader = 'bg-pink-50 text-pink-800';
            iconBg = 'bg-pink-100 text-pink-600';
            markerColor = 'text-pink-500';
          } else if (key === 'general') {
            borderClass = 'border-slate-200';
            bgHeader = 'bg-slate-50 text-slate-800';
            iconBg = 'bg-slate-100 text-slate-600';
            markerColor = 'text-slate-500';
          }

          return (
            <div key={key} className={`bg-white rounded-2xl border ${borderClass} shadow-sm overflow-hidden flex flex-col justify-between print:break-inside-avoid print:shadow-none print:border-gray-200`}>
              {/* Header */}
              <div className={`px-4 py-3.5 ${bgHeader} flex items-center gap-2.5 border-b border-gray-100 print:bg-gray-50 print:text-gray-900`}>
                <span className={`p-1.5 rounded-lg ${iconBg} text-base leading-none print:bg-gray-100 print:text-gray-700`}>{cat.icon}</span>
                <h3 className="font-bold text-xs uppercase tracking-wide">{cat.title}</h3>
              </div>

              {/* Content */}
              <div className="p-4 flex-1 flex flex-col justify-between space-y-5">
                {/* O que auditamos */}
                <div className="space-y-2">
                  <span className="text-[9px] font-extrabold uppercase tracking-wider text-slate-400 block mb-1">📋 Fatos Identificados</span>
                  {cat.facts.length > 0 ? (
                    <ul className="space-y-2">
                      {cat.facts.map((fact, idx) => {
                        const cleanText = fact.replace(/^[-*•\s\d\.)]+\s*/, '');
                        return (
                          <li key={idx} className="flex items-start gap-1.5 text-xs text-gray-700 leading-relaxed">
                            <span className={`text-[10px] mt-0.5 select-none ${markerColor}`}>•</span>
                            <span>{formatBoldText(cleanText)}</span>
                          </li>
                        );
                      })}
                    </ul>
                  ) : (
                    <p className="text-[11px] text-gray-400 italic">Sem observações específicas.</p>
                  )}
                </div>

                {/* Impacto no Negócio */}
                <div className="pt-3.5 border-t border-gray-100">
                  <span className="text-[9px] font-extrabold uppercase tracking-wider text-slate-400 block mb-1.5">💡 Análise de Impacto</span>
                  {cat.inferences.length > 0 ? (
                    <div className="space-y-2">
                      {cat.inferences.map((inf, idx) => {
                        const cleanText = inf.replace(/^[-*•\s\d\.)]+\s*/, '');
                        return (
                          <p key={idx} className="text-xs text-gray-600 leading-relaxed font-medium bg-slate-50/50 p-2.5 rounded-xl border border-slate-100/50 print:bg-white print:border-gray-100">
                            {formatBoldText(cleanText)}
                          </p>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-[11px] text-gray-400 italic">Sem diagnóstico específico disponível.</p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  /**
   * Renderiza o conteúdo do diagnóstico de forma estruturada com ícones e cards para recomendações e prompt
   */
  const renderFormattedContent = (text, key) => {
    if (!text || text === 'Nenhum dado disponível.' || text === 'Nenhum prompt gerado.') {
      return <p className="text-gray-400 italic text-center py-6">Nenhum dado disponível.</p>;
    }

    const lines = text
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (key === 'recommendations') {
      return (
        <div className="space-y-3">
          {lines.map((line, idx) => {
            const cleanText = line.replace(/^[-*•\s\d\.)]+\s*/, '');
            return (
              <div key={idx} className="flex items-start gap-3 p-3.5 bg-emerald-50/40 border border-emerald-100 rounded-xl hover:bg-emerald-50/80 transition-colors duration-150">
                <span className="text-emerald-600 text-base leading-none mt-0.5">🎯</span>
                <p className="text-sm text-gray-700 leading-relaxed">{formatBoldText(cleanText)}</p>
              </div>
            );
          })}
        </div>
      );
    }

    if (key === 'stitch') {
      const handleGenerateSite = async () => {
        const payload = `Antigravity, por favor atue como meu backend automatizado e crie o site Next.js para este lead, com deploy na Vercel. 
Utilize o seguinte prompt perfeito no Google Stitch MCP para gerar o design e HTML:

---
${text}
---`;
        try {
          await navigator.clipboard.writeText(payload);
          alert('Comando mágico copiado! Cole no chat para o Antigravity iniciar a criação e o deploy do site automaticamente.');
        } catch(err) {
          console.error(err);
        }
      };

      return (
        <div className="space-y-5">
          <div className="p-5 bg-gradient-to-r from-slate-900 to-blue-950 rounded-2xl shadow-lg border border-blue-900 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-left">
              <h4 className="text-white font-bold text-base mb-1.5 flex items-center gap-2">
                <span className="text-xl">🚀</span> Criar Site com IA (Stitch + Antigravity)
              </h4>
              <p className="text-blue-200 text-xs sm:text-sm leading-relaxed max-w-xl">
                Clique no botão ao lado para gerar o <strong>Comando Mágico</strong>. Depois, basta colar o comando no nosso chat para o Antigravity construir e publicar o site inteiro (Frontend + Deploy na Vercel) automaticamente em minutos.
              </p>
            </div>
            <button 
              onClick={handleGenerateSite}
              className="w-full md:w-auto flex-shrink-0 bg-gradient-to-r from-yellow-500 to-yellow-400 hover:from-yellow-400 hover:to-yellow-300 text-blue-950 px-6 py-3 rounded-xl font-bold text-sm transition-all shadow-[0_0_15px_rgba(234,179,8,0.3)] hover:shadow-[0_0_25px_rgba(234,179,8,0.5)] hover:-translate-y-0.5 whitespace-nowrap"
            >
              Gerar Comando Mágico
            </button>
          </div>

          <div className="space-y-2 bg-[#0F2744]/5 border border-[#0F2744]/15 rounded-xl p-4 relative mt-2">
            <div className="text-[10px] uppercase font-bold tracking-wider text-cyan-600 mb-2">Prompt Copiável para o Google Stitch AI (Manual)</div>
            <pre className="text-xs font-mono text-gray-800 whitespace-pre-wrap leading-relaxed select-all">
              {text}
            </pre>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="space-y-6">
      {/* Tab headers (oculto na impressão) */}
      <div className="flex border-b border-gray-200 no-print overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => {
              setActiveTab(tab.key);
              setCopiedTab(null);
            }}
            className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold transition-all duration-200 border-b-2 -mb-px whitespace-nowrap ${
              activeTab === tab.key
                ? 'border-cyan-500 text-cyan-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab content (com botão de cópia na tela) */}
      <div className="relative border border-gray-200 rounded-2xl p-6 bg-white shadow-sm hover:shadow-md transition-shadow duration-200 no-print" key={activeTab}>
        {/* Copy button */}
        <div className="absolute top-4 right-4 z-10">
          <button
            onClick={() => handleCopy(activeTab)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-200 shadow-sm ${
              copiedTab === activeTab
                ? 'bg-green-50 border-green-200 text-green-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            }`}
          >
            {copiedTab === activeTab ? (
              <>
                <span>✓</span>
                <span>Copiado!</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                <span>Copiar {activeTab === 'stitch' ? 'Prompt' : (activeTab === 'panel' ? 'Diagnóstico' : 'Texto')}</span>
              </>
            )}
          </button>
        </div>
        
        {/* Tab body content */}
        <div className="pt-8">
          {activeTab === 'panel' 
            ? renderDashboardPanel(categories) 
            : renderFormattedContent(contentMap[activeTab], activeTab)}
        </div>
      </div>

      {/* Visualização de Impressão Completa para PDF (Imprime APENAS o Painel de Diagnóstico de 3 colunas) */}
      <div className="print-only space-y-4">
        <h3 className="text-sm font-bold text-gray-900 border-b-2 border-gray-200 pb-2 mb-4 uppercase tracking-wider">
          📋 Relatório de Diagnóstico de Presença Digital
        </h3>
        {renderDashboardPanel(categories)}
      </div>
    </div>
  );
}
