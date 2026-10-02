'use client';

import { useState } from 'react';
import { fetchApi, getApiUrl } from '@/lib/api';
import { 
  LayoutDashboard, Target, Wand2, Copy, Check, Download, 
  Globe, ExternalLink, Smartphone, Monitor, RefreshCw, Sparkles, Palette, Users 
} from 'lucide-react';

const tabs = [
  { key: 'panel', label: 'Painel de Diagnóstico', icon: <LayoutDashboard size={16} /> },
  { key: 'recommendations', label: 'Recomendações de Venda', icon: <Target size={16} /> },
  { key: 'stitch', label: 'Landing Page Sob Medida 🚀', icon: <Sparkles size={16} /> },
];

const ARCHETYPES = [
  { id: 'auto', name: 'Automático', tag: 'Inteligente p/ Nicho', icon: '✨' },
  { id: 'cro_high_impact', name: 'Moderno Alto Impacto', tag: 'Dark CRO & Ação', icon: '⚡' },
  { id: 'showcase_catalog', name: 'Vitrine & Cotação', tag: 'Varejo & Catálogo', icon: '📦' },
  { id: 'split_dynamic', name: 'Split Hero Dinâmico', tag: '2 Colunas & Expresso', icon: '🚀' },
  { id: 'authority_proof', name: 'Máxima Autoridade', tag: 'Prova Social & Confiança', icon: '🏆' },
  { id: 'clean_editorial', name: 'Editorial Clean', tag: 'Minimalista & Elegante', icon: '📰' },
];

export default function DiagnosticTabs({ diagnostic = {} }) {
  const [activeTab, setActiveTab] = useState('panel');
  const [copiedTab, setCopiedTab] = useState(null);
  const [isGeneratingSite, setIsGeneratingSite] = useState(false);
  const [siteData, setSiteData] = useState(diagnostic);
  const [selectedArchetype, setSelectedArchetype] = useState('auto');
  const [viewMode, setViewMode] = useState('desktop');
  const [generationError, setGenerationError] = useState(null);
  const [showPromptCode, setShowPromptCode] = useState(false);
  const [isDownloadingImages, setIsDownloadingImages] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  /**
   * Baixa a pasta ZIP com todas as imagens reais extraídas do lead
   * para que o desenvolvedor anexe no prompt fora da automação (Google Stitch, Lovable, Cursor, etc).
   */
  const handleDownloadImages = async () => {
    const currentLeadId = siteData?.lead_id || diagnostic?.lead_id;
    if (!currentLeadId) return;
    try {
      setIsDownloadingImages(true);
      const downloadUrl = getApiUrl(`/leads/${currentLeadId}/download-images`);
      const res = await fetch(downloadUrl);
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail?.message || errJson.message || 'Erro ao gerar o arquivo ZIP com as imagens.');
      }

      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;

      const disposition = res.headers.get('content-disposition');
      let filename = `imagens_lead_${currentLeadId}.zip`;
      if (disposition && disposition.includes('filename=')) {
        const matches = disposition.match(/filename="?([^"]+)"?/);
        if (matches && matches[1]) {
          filename = matches[1];
        }
      }
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);

      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 3000);
    } catch (err) {
      console.error('Erro no download das imagens:', err);
      alert('Não foi possível baixar as imagens: ' + (err.message || 'Erro de conexão com o servidor.'));
    } finally {
      setIsDownloadingImages(false);
    }
  };

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
   * Agrupa e estrutura os fatos e as inferências por pilares da presença digital.
   * Suporta tags explícitas [PILAR] e faz fallback inteligente por palavras-chave.
   */
  const parseDiagnosticData = (factsText, inferencesText) => {
    const categories = {
      google: { title: 'Google Empresa & Local', icon: '📍', facts: [], inferences: [] },
      website: { title: 'Website, Performance & SEO', icon: '🌐', facts: [], inferences: [] },
      social: { title: 'Redes Sociais & Engajamento', icon: '📱', facts: [], inferences: [] },
      general: { title: 'Outras Observações', icon: '🔍', facts: [], inferences: [] }
    };

    const getPilarFromLine = (line) => {
      const tagMatch = line.match(/^\[([A-Z]+)\]\s*/);
      if (tagMatch) {
        const tag = tagMatch[1].toLowerCase();
        if (tag === 'google') return { pilar: 'google', text: line.replace(/^\[[A-Z]+\]\s*/, '') };
        if (tag === 'website') return { pilar: 'website', text: line.replace(/^\[[A-Z]+\]\s*/, '') };
        if (tag === 'social') return { pilar: 'social', text: line.replace(/^\[[A-Z]+\]\s*/, '') };
        if (tag === 'general') return { pilar: 'general', text: line.replace(/^\[[A-Z]+\]\s*/, '') };
      }
      const t = line.toLowerCase();
      if (t.includes('google') || t.includes('rating') || t.includes('avaliaç') || t.includes('gbp') || t.includes('maps') || t.includes('reviews') || t.includes('telefone') || t.includes('endereço')) {
        return { pilar: 'google', text: line };
      }
      if (t.includes('site') || t.includes('website') || t.includes('pagespeed') || t.includes('lcp') || t.includes('inp') || t.includes('ssl') || t.includes('velocidade') || t.includes('performance') || t.includes('seo')) {
        return { pilar: 'website', text: line };
      }
      if (t.includes('instagram') || t.includes('facebook') || t.includes('linkedin') || t.includes('social') || t.includes('redes') || t.includes('post') || t.includes('seguidores')) {
        return { pilar: 'social', text: line };
      }
      return { pilar: 'general', text: line };
    };

    if (typeof factsText === 'string') {
      factsText.split('\n').map(line => line.trim()).filter(Boolean).forEach(line => {
        const { pilar, text } = getPilarFromLine(line);
        categories[pilar].facts.push(text);
      });
    }

    if (typeof inferencesText === 'string') {
      inferencesText.split('\n').map(line => line.trim()).filter(Boolean).forEach(line => {
        const { pilar, text } = getPilarFromLine(line);
        categories[pilar].inferences.push(text);
      });
    }

    return categories;
  };

  const categories = parseDiagnosticData(diagnostic.observed_facts, diagnostic.inferences);

  const salesCopyText = [
    diagnostic.sales_approach ? `🎯 Ângulo de Abordagem:\n${diagnostic.sales_approach}` : '',
    diagnostic.pain_points ? `\n😣 Pontos de Dor:\n${diagnostic.pain_points}` : '',
    diagnostic.talking_points ? `\n💬 Argumentos de Venda:\n${diagnostic.talking_points}` : '',
    diagnostic.value_proposition ? `\n💎 Proposta de Valor:\n${diagnostic.value_proposition}` : '',
    diagnostic.recommendations ? `\n🔧 Recomendações Técnicas:\n${diagnostic.recommendations}` : '',
  ].filter(Boolean).join('\n') || 'Nenhum dado disponível.';

  const contentMap = {
    panel: `Fatos Observados:\n${diagnostic.observed_facts || ''}\n\nInferências da IA:\n${diagnostic.inferences || ''}`,
    recommendations: salesCopyText,
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
   * Renderiza a aba de Recomendações de Venda com seções comerciais estruturadas.
   */
  const renderSalesRecommendations = () => {
    const approach = diagnostic.sales_approach;
    const painPointsRaw = diagnostic.pain_points;
    const talkingPointsRaw = diagnostic.talking_points;
    const valueProposition = diagnostic.value_proposition;
    const recommendations = diagnostic.recommendations;

    const parseList = (text) => {
      if (!text) return [];
      return text.split('\n').map(l => l.replace(/^[-*•]\s*/, '').trim()).filter(Boolean);
    };

    const painPoints = parseList(painPointsRaw);
    const talkingPoints = parseList(talkingPointsRaw);
    const hasCommercialData = approach || painPoints.length > 0 || talkingPoints.length > 0 || valueProposition;

    return (
      <div className="space-y-6">
        {/* Proposta de Valor */}
        {valueProposition && (
          <div className="p-5 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-2xl">
            <div className="flex items-start gap-3">
              <span className="text-2xl">💎</span>
              <div>
                <h4 className="text-xs font-extrabold uppercase tracking-wider text-cyan-400 mb-1">Proposta de Valor Central</h4>
                <p className="text-sm text-gray-100 font-medium leading-relaxed">{valueProposition}</p>
              </div>
            </div>
          </div>
        )}

        {/* Ângulo de Abordagem */}
        {approach && (
          <div className="p-5 bg-emerald-500/10 border border-emerald-500/25 rounded-2xl">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🎯</span>
              <div>
                <h4 className="text-xs font-extrabold uppercase tracking-wider text-emerald-400 mb-1">Ângulo de Abordagem</h4>
                <p className="text-sm text-gray-200 leading-relaxed">{approach}</p>
              </div>
            </div>
          </div>
        )}

        {/* Pontos de Dor & Argumentos lado a lado */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {painPoints.length > 0 && (
            <div className="p-5 bg-rose-500/10 border border-rose-500/25 rounded-2xl">
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-rose-400 mb-3 flex items-center gap-2">
                <span>😣</span> Pontos de Dor do Cliente
              </h4>
              <ul className="space-y-2">
                {painPoints.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-300 leading-relaxed">
                    <span className="text-rose-400 mt-0.5 text-xs">▸</span>
                    <span>{formatBoldText(point)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {talkingPoints.length > 0 && (
            <div className="p-5 bg-amber-500/10 border border-amber-500/25 rounded-2xl">
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-amber-400 mb-3 flex items-center gap-2">
                <span>💬</span> Argumentos-Chave de Venda
              </h4>
              <ul className="space-y-2">
                {talkingPoints.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-300 leading-relaxed">
                    <span className="text-amber-400 mt-0.5 text-xs">▸</span>
                    <span>{formatBoldText(point)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Recomendações Técnicas */}
        {recommendations && (
          <div>
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
              <span>🔧</span> Recomendações Técnicas Prioritárias
            </h4>
            <div className="space-y-2">
              {recommendations.split('\n').filter(Boolean).map((rec, idx) => {
                const isHigh = rec.includes('[HIGH]');
                const isMedium = rec.includes('[MEDIUM]');
                const cleanRec = rec.replace(/^\[(?:HIGH|MEDIUM|LOW)\]\s*/, '');
                return (
                  <div key={idx} className={`flex items-start gap-3 p-3.5 rounded-xl border text-sm ${
                    isHigh ? 'bg-rose-500/10 border-rose-500/25 text-gray-200' :
                    isMedium ? 'bg-amber-500/10 border-amber-500/25 text-gray-200' :
                    'bg-gray-800/40 border-gray-700/40 text-gray-300'
                  }`}>
                    <span className="mt-0.5">
                      {isHigh ? '🔴' : isMedium ? '🟡' : '🟢'}
                    </span>
                    <span className="leading-relaxed">{formatBoldText(cleanRec)}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {!hasCommercialData && !recommendations && (
          <div className="text-center py-10 text-gray-500 italic">
            <p>Gere ou regenere o diagnóstico para carregar as recomendações comerciais detalhadas.</p>
          </div>
        )}
      </div>
    );
  };

  /**
   * Renderiza o conteúdo do prompt Stitch
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
      const currentLeadId = siteData.lead_id || diagnostic.lead_id;
      const previewUrl = getApiUrl(`/leads/${currentLeadId}/lp-preview`);
      const hasGeneratedSite = siteData.has_generated_site || diagnostic.has_generated_site;
      const brandColors = siteData.brand_colors || diagnostic.brand_colors;
      const ownersInfo = siteData.owners_info || diagnostic.owners_info;
      const promptText = siteData.stitch_prompt || diagnostic.stitch_prompt || text;

      const handleGenerateLandingPage = async () => {
        if (!currentLeadId) return;
        setIsGeneratingSite(true);
        setGenerationError(null);
        try {
          const jsonResp = await fetchApi(`/leads/${currentLeadId}/generate-lp`, {
            method: 'POST',
            body: JSON.stringify({ archetype_id: selectedArchetype }),
          });
          setSiteData(jsonResp.data);
          if (diagnostic) {
            diagnostic.has_generated_site = true;
            diagnostic.preview_url = jsonResp.data.preview_url;
            diagnostic.brand_colors = jsonResp.data.brand_colors;
            diagnostic.owners_info = jsonResp.data.owners_info;
            diagnostic.stitch_prompt = jsonResp.data.stitch_prompt;
          }
        } catch (err) {
          const msg = err.message === 'Failed to fetch'
            ? 'Falha de comunicação com o Backend (Failed to fetch). Certifique-se de realizar o Deploy do serviço Backend no Easypanel.'
            : (err.message || 'Falha ao conectar com o servidor para gerar a Landing Page');
          setGenerationError(msg);
        } finally {
          setIsGeneratingSite(false);
        }
      };

      const handleCopyShareLink = async () => {
        try {
          const fullUrl = previewUrl.startsWith('http')
            ? previewUrl
            : `${window.location.origin}${previewUrl}`;
          await navigator.clipboard.writeText(fullUrl);
          alert('Link público da Landing Page copiado com sucesso!');
        } catch (err) {
          console.error(err);
        }
      };

      return (
        <div className="space-y-6">
          {/* Header Action Banner */}
          <div className="p-6 bg-gradient-to-br from-gray-900 via-indigo-950/70 to-slate-900 rounded-2xl shadow-xl border border-indigo-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
            <div className="relative z-10 max-w-2xl">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="text-cyan-400" size={22} />
                <h4 className="text-white font-extrabold text-lg">
                  Landing Page Sob Medida com IA
                </h4>
                <span className="bg-cyan-500/20 text-cyan-400 text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider border border-cyan-500/30">
                  {hasGeneratedSite ? 'Pronta' : 'Meta-Prompt CRO'}
                </span>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">
                {hasGeneratedSite 
                  ? 'A Landing Page deste lead foi gerada sob medida com Tailwind CSS, integrando as dores do diagnóstico, cores da marca e liderança identificada.'
                  : 'Clique no botão ao lado para enriquecer a identidade visual, identificar sócios e gerar automaticamente a Landing Page de alta conversão sem templates genéricos.'}
              </p>

              {/* Badges de Ativos Enriquecidos */}
              {(brandColors || (ownersInfo && ownersInfo.length > 0)) && (
                <div className="mt-4 pt-3 border-t border-gray-700/50 flex flex-wrap items-center gap-4 text-xs">
                  {brandColors && (
                    <div className="flex items-center gap-2 bg-gray-900/60 px-3 py-1 rounded-lg border border-gray-700/60">
                      <Palette size={14} className="text-cyan-400" />
                      <span className="text-gray-400">Paleta da Marca:</span>
                      <div className="flex items-center gap-1.5">
                        <span className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm" style={{ backgroundColor: brandColors.background }} title={`Fundo: ${brandColors.background}`} />
                        <span className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm" style={{ backgroundColor: brandColors.primary }} title={`Primária: ${brandColors.primary}`} />
                        <span className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm" style={{ backgroundColor: brandColors.secondary }} title={`Secundária: ${brandColors.secondary}`} />
                      </div>
                    </div>
                  )}

                  {ownersInfo && ownersInfo.length > 0 && (
                    <div className="flex items-center gap-2 bg-gray-900/60 px-3 py-1 rounded-lg border border-gray-700/60">
                      <Users size={14} className="text-indigo-400" />
                      <span className="text-gray-400">Liderança:</span>
                      <span className="text-white font-medium">
                        {ownersInfo.map(o => o.name).join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              )}
              {/* Seletor de Modelos de Inspiração (Arquétipos) */}
              <div className="mt-4 pt-3 border-t border-gray-700/50">
                <div className="flex items-center gap-2 mb-2">
                  <Wand2 size={13} className="text-cyan-400" />
                  <span className="text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Modelo de Inspiração Visual / Arquitetura:
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                  {ARCHETYPES.map((arch) => {
                    const isSelected = selectedArchetype === arch.id;
                    return (
                      <button
                        key={arch.id}
                        type="button"
                        onClick={() => setSelectedArchetype(arch.id)}
                        className={`p-2 rounded-xl border text-left transition-all flex flex-col justify-between ${
                          isSelected
                            ? 'bg-cyan-500/20 border-cyan-400 text-white shadow-[0_0_12px_rgba(6,182,212,0.3)] ring-1 ring-cyan-400'
                            : 'bg-gray-900/60 border-gray-700/70 text-gray-400 hover:border-gray-500 hover:text-gray-200'
                        }`}
                      >
                        <div className="flex items-center gap-1.5 text-xs font-bold truncate">
                          <span>{arch.icon}</span>
                          <span className="truncate">{arch.name}</span>
                        </div>
                        <span className="text-[10px] text-gray-400 truncate block mt-0.5">{arch.tag}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {generationError && (
                <div className="mt-3 text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 p-2.5 rounded-lg">
                  ⚠️ {generationError}
                </div>
              )}
            </div>

            <div className="relative z-10 flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
              <button 
                onClick={handleGenerateLandingPage}
                disabled={isGeneratingSite}
                className="w-full md:w-auto flex-shrink-0 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-7 py-3 rounded-xl font-bold text-sm transition-all shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isGeneratingSite ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Construindo Landing Page...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>{hasGeneratedSite ? 'Regenerar Página' : 'Gerar LP Sob Medida'}</span>
                  </>
                )}
              </button>

              {hasGeneratedSite && (
                <a
                  href={previewUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full md:w-auto flex-shrink-0 bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-cyan-500/30 px-5 py-3 rounded-xl font-semibold text-sm transition-all flex items-center justify-center gap-2"
                >
                  <ExternalLink size={16} />
                  <span>Abrir Tela Cheia</span>
                </a>
              )}
            </div>
          </div>

          {/* Interactive Preview Container */}
          {hasGeneratedSite && (
            <div className="space-y-3">
              {/* Preview Toolbar */}
              <div className="flex flex-wrap items-center justify-between gap-3 px-2">
                <div className="flex items-center gap-2 bg-gray-900/80 border border-gray-700/60 p-1 rounded-xl">
                  <button
                    onClick={() => setViewMode('desktop')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      viewMode === 'desktop' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    <Monitor size={14} /> Desktop
                  </button>
                  <button
                    onClick={() => setViewMode('mobile')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      viewMode === 'mobile' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    <Smartphone size={14} /> Mobile (375px)
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={handleDownloadImages}
                    disabled={isDownloadingImages}
                    className={`flex items-center gap-1.5 px-3 py-1.5 border rounded-lg text-xs font-semibold transition-all ${
                      downloadSuccess 
                        ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-400' 
                        : 'bg-indigo-950/70 hover:bg-indigo-900 border-indigo-700/60 text-indigo-300 hover:text-white'
                    }`}
                    title="Baixar pasta ZIP com todas as imagens públicas reais da empresa para usar no prompt externamente"
                  >
                    {isDownloadingImages ? (
                      <>
                        <RefreshCw size={13} className="animate-spin text-cyan-400" />
                        <span>Baixando ZIP...</span>
                      </>
                    ) : downloadSuccess ? (
                      <>
                        <Check size={13} className="text-emerald-400" />
                        <span>Imagens Baixadas!</span>
                      </>
                    ) : (
                      <>
                        <Download size={13} className="text-cyan-400" />
                        <span>Baixar Imagens (ZIP)</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleCopyShareLink}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white rounded-lg transition-all"
                  >
                    <Copy size={13} /> Copiar Link para o Cliente
                  </button>
                  <button
                    onClick={() => setShowPromptCode(!showPromptCode)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800/60 hover:bg-gray-700 border border-gray-700 text-xs font-semibold text-gray-400 hover:text-white rounded-lg transition-all"
                  >
                    <Wand2 size={13} /> {showPromptCode ? 'Ocultar Prompt' : 'Ver Prompt Usado'}
                  </button>
                </div>
              </div>

              {/* Iframe Frame */}
              <div className="bg-gray-950/80 border border-gray-700/60 rounded-2xl p-4 flex justify-center shadow-2xl overflow-hidden">
                <div 
                  className={`transition-all duration-300 rounded-xl overflow-hidden shadow-2xl border border-gray-800 ${
                    viewMode === 'mobile' ? 'w-[375px] h-[680px]' : 'w-full h-[650px]'
                  }`}
                >
                  <iframe 
                    src={previewUrl} 
                    title="Landing Page Preview" 
                    className="w-full h-full border-0 bg-gray-950" 
                  />
                </div>
              </div>
            </div>
          )}

          {/* Collapsible Prompt Specification */}
          {(showPromptCode || !hasGeneratedSite) && (
            <div className="space-y-3 bg-gray-900/50 border border-gray-700/50 rounded-xl p-5 relative shadow-inner">
              <div className="text-[10px] uppercase font-bold tracking-wider text-cyan-400 mb-2 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Wand2 size={14} className="text-cyan-400" />
                  <span>Meta-Prompt de Elite Estruturado (CRO & Nicho)</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleDownloadImages}
                    disabled={isDownloadingImages}
                    className="text-cyan-300 hover:text-white bg-cyan-950/70 hover:bg-cyan-900/90 border border-cyan-700/50 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
                    title="Baixar arquivo ZIP com todas as fotos extraídas da empresa para anexar a este prompt no Stitch / Lovable / Cursor"
                  >
                    {isDownloadingImages ? (
                      <RefreshCw size={13} className="animate-spin text-cyan-400" />
                    ) : (
                      <Download size={13} className="text-cyan-400" />
                    )}
                    <span>Baixar Imagens (ZIP)</span>
                  </button>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(promptText);
                      alert('Prompt copiado com sucesso! Agora você pode colar na ferramenta externa de sua escolha.');
                    }}
                    className="text-gray-200 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
                  >
                    <Copy size={13} /> Copiar Prompt
                  </button>
                </div>
              </div>
              <div className="p-2.5 bg-indigo-950/30 border border-indigo-500/20 rounded-lg text-xs text-indigo-300 flex items-center gap-2">
                <span className="font-semibold text-cyan-400">💡 Dica para uso externo:</span>
                <span>Copie o prompt e baixe o ZIP de imagens acima para anexar diretamente no Google Stitch, Lovable, Cursor, Bolt ou v0.</span>
              </div>
              <pre className="text-xs font-mono text-gray-300 whitespace-pre-wrap leading-relaxed select-all max-h-72 overflow-y-auto pr-2 bg-gray-950/60 p-3 rounded-lg border border-gray-800">
                {promptText}
              </pre>
            </div>
          )}
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
        {/* Action buttons (Download Images & Copy) */}
        <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
          {activeTab === 'stitch' && (
            <button
              onClick={handleDownloadImages}
              disabled={isDownloadingImages}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-300 shadow-sm ${
                downloadSuccess
                  ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400'
                  : 'bg-indigo-950/70 border-indigo-700/60 text-indigo-300 hover:bg-indigo-900/90 hover:text-white hover:border-indigo-500'
              }`}
              title="Baixar pasta ZIP com todas as imagens reais extraídas para usar no prompt externamente"
            >
              {isDownloadingImages ? (
                <>
                  <RefreshCw size={13} className="animate-spin text-cyan-400" />
                  <span>Baixando ZIP...</span>
                </>
              ) : downloadSuccess ? (
                <>
                  <Check size={13} className="text-emerald-400" />
                  <span>ZIP Baixado!</span>
                </>
              ) : (
                <>
                  <Download size={13} className="text-cyan-400" />
                  <span>Baixar Imagens (ZIP)</span>
                </>
              )}
            </button>
          )}
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
            ? (
              <div className="space-y-8">
                {/* Dashboard de Pilares existente */}
                {renderDashboardPanel(categories)}

                {/* ===== GAFES CRÍTICAS ENCONTRADAS ===== */}
                {diagnostic.critical_blunders && diagnostic.critical_blunders.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2.5 mb-4">
                      <span className="text-xl">🚨</span>
                      <h3 className="text-sm font-extrabold uppercase tracking-wider text-rose-400">
                        Gafes Críticas Encontradas ({diagnostic.critical_blunders.length})
                      </h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {diagnostic.critical_blunders.map((blunder, idx) => {
                        const severityStyles = {
                          CRITICAL: 'border-rose-500/40 bg-rose-500/10',
                          HIGH: 'border-amber-500/40 bg-amber-500/10',
                          MEDIUM: 'border-yellow-500/30 bg-yellow-500/5',
                        };
                        const severityBadge = {
                          CRITICAL: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
                          HIGH: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
                          MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
                        };
                        return (
                          <div key={idx} className={`p-4 rounded-xl border ${severityStyles[blunder.severity] || severityStyles.MEDIUM} transition-all hover:scale-[1.01]`}>
                            <div className="flex items-start gap-3">
                              <span className="material-symbols-outlined text-xl text-gray-300 mt-0.5" style={{fontVariationSettings: "'FILL' 0, 'wght' 400"}}>{blunder.icon}</span>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                                  <h4 className="text-xs font-bold text-gray-100">{blunder.title}</h4>
                                  <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded border ${severityBadge[blunder.severity] || severityBadge.MEDIUM}`}>
                                    {blunder.severity}
                                  </span>
                                </div>
                                <p className="text-[11px] text-gray-300 leading-relaxed mb-2">{blunder.detected_reason}</p>
                                <div className="text-[10px] text-gray-500 flex items-start gap-1">
                                  <span className="shrink-0">📉</span>
                                  <span>{blunder.financial_impact}</span>
                                </div>
                                <div className="text-[10px] text-emerald-400/80 flex items-start gap-1 mt-1">
                                  <span className="shrink-0">✅</span>
                                  <span className="font-medium">Solução LP: {blunder.lp_solution}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* ===== VAZAMENTO FINANCEIRO ESTIMADO ===== */}
                {diagnostic.revenue_leak && (
                  <div className="p-5 rounded-2xl bg-gradient-to-r from-rose-500/10 via-amber-500/5 to-transparent border border-rose-500/25">
                    <div className="flex items-center gap-2.5 mb-4">
                      <span className="text-xl">💸</span>
                      <h3 className="text-sm font-extrabold uppercase tracking-wider text-rose-400">
                        Vazamento Financeiro Estimado
                      </h3>
                      <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border ${
                        diagnostic.revenue_leak.loss_severity === 'CRÍTICO' 
                          ? 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                          : diagnostic.revenue_leak.loss_severity === 'ALTO'
                            ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                            : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                      }`}>
                        {diagnostic.revenue_leak.loss_severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-200 leading-relaxed mb-4 font-medium">
                      {diagnostic.revenue_leak.summary}
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div className="p-3 rounded-xl bg-gray-900/60 border border-gray-700/50 text-center">
                        <p className="text-lg font-extrabold text-cyan-400">
                          {diagnostic.revenue_leak.monthly_searches?.low}-{diagnostic.revenue_leak.monthly_searches?.high}
                        </p>
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Buscas/mês</p>
                      </div>
                      <div className="p-3 rounded-xl bg-gray-900/60 border border-gray-700/50 text-center">
                        <p className="text-lg font-extrabold text-amber-400">
                          {diagnostic.revenue_leak.lost_leads_per_month?.low}-{diagnostic.revenue_leak.lost_leads_per_month?.high}
                        </p>
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Leads perdidos/mês</p>
                      </div>
                      <div className="p-3 rounded-xl bg-gray-900/60 border border-gray-700/50 text-center">
                        <p className="text-lg font-extrabold text-rose-400">
                          R$ {(diagnostic.revenue_leak.estimated_revenue_lost?.low || 0).toLocaleString('pt-BR')}
                        </p>
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Perda mínima/mês</p>
                      </div>
                      <div className="p-3 rounded-xl bg-gray-900/60 border border-gray-700/50 text-center">
                        <p className="text-lg font-extrabold text-rose-400">
                          R$ {(diagnostic.revenue_leak.estimated_revenue_lost?.high || 0).toLocaleString('pt-BR')}
                        </p>
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Perda máxima/mês</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* ===== MATRIZ DE TRANSFORMAÇÃO DA LP ===== */}
                {diagnostic.transformation_matrix && diagnostic.transformation_matrix.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2.5 mb-4">
                      <span className="text-xl">🔄</span>
                      <h3 className="text-sm font-extrabold uppercase tracking-wider text-emerald-400">
                        O Que a Landing Page Resolve
                      </h3>
                    </div>
                    <div className="space-y-3">
                      {diagnostic.transformation_matrix.map((item, idx) => (
                        <div key={idx} className="p-4 rounded-xl bg-gray-900/60 border border-gray-700/40 hover:border-emerald-500/30 transition-all">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-rose-400 text-xs font-bold">❌ Problema:</span>
                            <span className="text-xs text-gray-200 font-semibold">{item.problem}</span>
                          </div>
                          <p className="text-[11px] text-gray-400 mb-2 pl-5">{item.detected_detail}</p>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-emerald-400 text-xs font-bold">✅ Solução LP:</span>
                            <span className="text-[11px] text-gray-300">{item.lp_solution}</span>
                          </div>
                          <div className="flex items-center gap-2 pl-5 mt-1">
                            <span className="text-cyan-400 text-[10px] font-bold">📈 Ganho:</span>
                            <span className="text-[10px] text-gray-400">{item.expected_gain}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ===== INSIGHT ESTRATÉGICO DO NICHO ===== */}
                {diagnostic.niche_insights && (
                  <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/25">
                    <div className="flex items-start gap-3">
                      <span className="text-lg">🧠</span>
                      <div>
                        <h4 className="text-xs font-extrabold uppercase tracking-wider text-purple-400 mb-1.5">Insight Estratégico do Setor</h4>
                        <p className="text-xs text-gray-300 leading-relaxed">{formatBoldText(diagnostic.niche_insights)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
            : activeTab === 'recommendations'
              ? renderSalesRecommendations()
              : renderFormattedContent(contentMap[activeTab], activeTab)}
        </div>
      </div>
    </div>
  );
}
