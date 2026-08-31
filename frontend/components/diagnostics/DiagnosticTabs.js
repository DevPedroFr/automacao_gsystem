'use client';

import { useState } from 'react';
import { LayoutDashboard, Target, Wand2, Copy, Check } from 'lucide-react';

const tabs = [
  { key: 'panel', label: 'Painel de Diagnóstico', icon: <LayoutDashboard size={16} /> },
  { key: 'recommendations', label: 'Recomendações de Venda', icon: <Target size={16} /> },
  { key: 'stitch', label: 'Prompt Google Stitch ⚡', icon: <Wand2 size={16} /> },
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
        return <strong key={index} className="font-bold text-white print:text-gray-900">{part}</strong>;
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
          let borderClass = 'border-blue-500/20';
          let bgHeader = 'bg-blue-500/10 text-blue-400';
          let iconBg = 'bg-blue-500/20 text-blue-300';
          let markerColor = 'text-blue-400';

          if (key === 'website') {
            borderClass = 'border-cyan-500/20';
            bgHeader = 'bg-cyan-500/10 text-cyan-400';
            iconBg = 'bg-cyan-500/20 text-cyan-300';
            markerColor = 'text-cyan-400';
          } else if (key === 'social') {
            borderClass = 'border-pink-500/20';
            bgHeader = 'bg-pink-500/10 text-pink-400';
            iconBg = 'bg-pink-500/20 text-pink-300';
            markerColor = 'text-pink-400';
          } else if (key === 'general') {
            borderClass = 'border-gray-500/20';
            bgHeader = 'bg-gray-500/10 text-gray-300';
            iconBg = 'bg-gray-500/20 text-gray-300';
            markerColor = 'text-gray-400';
          }

          return (
            <div key={key} className={`bg-gray-900/60 backdrop-blur-md rounded-2xl border ${borderClass} shadow-lg overflow-hidden flex flex-col justify-between print:bg-white print:break-inside-avoid print:shadow-none print:border-gray-200 hover:shadow-[0_4px_20px_rgba(6,182,212,0.1)] transition-all duration-300`}>
              {/* Header */}
              <div className={`px-4 py-3.5 ${bgHeader} flex items-center gap-2.5 border-b border-gray-700/50 print:bg-gray-50 print:text-gray-900 print:border-gray-200`}>
                <span className={`p-1.5 rounded-lg ${iconBg} text-base leading-none print:bg-gray-200 print:text-gray-700`}>{cat.icon}</span>
                <h3 className="font-bold text-xs uppercase tracking-wide">{cat.title}</h3>
              </div>

              {/* Content */}
              <div className="p-4 flex-1 flex flex-col justify-between space-y-5">
                {/* O que auditamos */}
                <div className="space-y-2">
                  <span className="text-[9px] font-extrabold uppercase tracking-wider text-gray-500 block mb-1">📋 Fatos Identificados</span>
                  {cat.facts.length > 0 ? (
                    <ul className="space-y-2">
                      {cat.facts.map((fact, idx) => {
                        const cleanText = fact.replace(/^[-*•\s\d\.)]+\s*/, '');
                        return (
                          <li key={idx} className="flex items-start gap-1.5 text-xs text-gray-300 leading-relaxed print:text-gray-700">
                            <span className={`text-[10px] mt-0.5 select-none ${markerColor}`}>•</span>
                            <span>{formatBoldText(cleanText)}</span>
                          </li>
                        );
                      })}
                    </ul>
                  ) : (
                    <p className="text-[11px] text-gray-600 italic">Sem observações específicas.</p>
                  )}
                </div>

                {/* Impacto no Negócio */}
                <div className="pt-3.5 border-t border-gray-700/30 print:border-gray-100">
                  <span className="text-[9px] font-extrabold uppercase tracking-wider text-gray-500 block mb-1.5">💡 Análise de Impacto</span>
                  {cat.inferences.length > 0 ? (
                    <div className="space-y-2">
                      {cat.inferences.map((inf, idx) => {
                        const cleanText = inf.replace(/^[-*•\s\d\.)]+\s*/, '');
                        return (
                          <p key={idx} className="text-xs text-gray-400 leading-relaxed font-medium bg-gray-800/50 p-2.5 rounded-xl border border-gray-700/50 print:bg-white print:border-gray-100 print:text-gray-600">
                            {formatBoldText(cleanText)}
                          </p>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-[11px] text-gray-600 italic">Sem diagnóstico específico disponível.</p>
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
              <div key={idx} className="flex items-start gap-3 p-4 bg-emerald-500/10 border border-emerald-500/25 rounded-xl hover:bg-emerald-500/15 transition-colors duration-150 print:bg-white print:border-gray-200">
                <span className="text-emerald-400 text-base leading-none mt-0.5">🎯</span>
                <p className="text-sm text-gray-200 print:text-gray-800 leading-relaxed">{formatBoldText(cleanText)}</p>
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
          <div className="p-6 bg-gradient-to-br from-gray-900 to-indigo-950/80 rounded-2xl shadow-xl border border-indigo-500/30 flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
            
            <div className="text-left relative z-10">
              <h4 className="text-white font-extrabold text-lg mb-2 flex items-center gap-2">
                <Wand2 className="text-cyan-400" size={24} /> Criar Site com IA <span className="bg-cyan-500/20 text-cyan-400 text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider border border-cyan-500/30">Auto</span>
              </h4>
              <p className="text-gray-300 text-sm leading-relaxed max-w-2xl">
                Clique no botão ao lado para gerar o <strong>Comando Mágico</strong>. Depois, cole no chat para o Antigravity construir e publicar o site inteiro (Frontend + Deploy Vercel) automaticamente.
              </p>
            </div>
            <button 
              onClick={handleGenerateSite}
              className="relative z-10 w-full md:w-auto flex-shrink-0 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white px-8 py-3.5 rounded-xl font-bold text-sm transition-all shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] hover:-translate-y-0.5 whitespace-nowrap flex items-center justify-center gap-2"
            >
              <Wand2 size={16} /> Gerar Comando Mágico
            </button>
          </div>

          <div className="space-y-2 bg-gray-900/50 border border-gray-700/50 rounded-xl p-5 relative mt-4 shadow-inner">
            <div className="text-[10px] uppercase font-bold tracking-wider text-cyan-500 mb-3 flex items-center gap-1">
              Prompt Copiável para o Google Stitch AI
            </div>
            <pre className="text-xs font-mono text-gray-300 whitespace-pre-wrap leading-relaxed select-all">
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
      <div className="flex border-b border-gray-700/50 no-print overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => {
              setActiveTab(tab.key);
              setCopiedTab(null);
            }}
            className={`flex items-center gap-2 px-6 py-4 text-sm font-semibold transition-all duration-300 border-b-2 -mb-px whitespace-nowrap ${
              activeTab === tab.key
                ? 'border-cyan-400 text-cyan-400 bg-cyan-500/5'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500 hover:bg-gray-800/30'
            }`}
          >
            <span className={activeTab === tab.key ? 'animate-pulse' : ''}>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab content (com botão de cópia na tela) */}
      <div className="relative border border-gray-700/50 rounded-b-2xl rounded-tr-2xl p-6 bg-gray-900/40 backdrop-blur-md shadow-xl transition-shadow duration-200 no-print" key={activeTab}>
        {/* Copy button */}
        <div className="absolute top-4 right-4 z-10">
          <button
            onClick={() => handleCopy(activeTab)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-300 shadow-sm ${
              copiedTab === activeTab
                ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400'
                : 'bg-gray-800/50 border-gray-700 text-gray-300 hover:bg-gray-700 hover:text-white hover:border-gray-600'
            }`}
          >
            {copiedTab === activeTab ? (
              <>
                <Check size={14} />
                <span>Copiado!</span>
              </>
            ) : (
              <>
                <Copy size={14} />
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
