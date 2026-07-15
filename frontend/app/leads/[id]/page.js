'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import ScoreBar from '@/components/ui/ScoreBar';
import DiagnosticTabs from '@/components/diagnostics/DiagnosticTabs';
import EmailDraft from '@/components/diagnostics/EmailDraft';
import { PRIORITY_CONFIG } from '@/lib/constants';

export default function LeadDetailPage() {
  const params = useParams();
  const router = useRouter();
  const leadId = params.id;

  const [lead, setLead] = useState(null);
  const [diagnostic, setDiagnostic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [diagLoading, setDiagLoading] = useState(false);
  const [diagError, setDiagError] = useState('');

  const loadLead = useCallback(async () => {
    try {
      const data = await fetchApi(`/leads/${leadId}`);
      setLead(data.data || data);
    } catch (err) {
      console.error('Erro ao carregar lead:', err);
    }
  }, [leadId]);

  const loadDiagnostic = useCallback(async () => {
    try {
      const data = await fetchApi(`/leads/${leadId}/diagnostic`);
      setDiagnostic(data.data || data);
    } catch {
      // 404 means no diagnostic yet
      setDiagnostic(null);
    }
  }, [leadId]);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([loadLead(), loadDiagnostic()]);
      setLoading(false);
    };
    init();
  }, [loadLead, loadDiagnostic]);

  const handleGenerateDiagnostic = async () => {
    try {
      setDiagLoading(true);
      setDiagError('');
      const result = await fetchApi(`/leads/${leadId}/diagnostic`, {
        method: 'POST',
      });
      setDiagnostic(result.data || result);
    } catch (err) {
      setDiagError(err.message || 'Erro ao gerar diagnóstico');
    } finally {
      setDiagLoading(false);
    }
  };

  const getPriorityVariant = (priority) => {
    const map = { A: 'success', B: 'warning', C: 'danger' };
    return map[priority] || 'default';
  };

  const getScoreColor = (score) => {
    if (score < 40) return 'text-red-500';
    if (score < 70) return 'text-yellow-500';
    return 'text-green-500';
  };

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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-200 rounded w-64 animate-pulse-soft" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-32 animate-pulse-soft" />
          ))}
        </div>
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="text-center py-20">
        <p className="text-lg text-gray-500">Lead não encontrado</p>
        <Button variant="secondary" className="mt-4" onClick={() => router.back()}>
          Voltar
        </Button>
      </div>
    );
  }

  const priorityConf = PRIORITY_CONFIG[lead.priority] || {};

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Cabeçalho de papel timbrado exclusivo para o PDF Impresso */}
      <div className="print-only border-b-2 border-[#0F2744] pb-4 mb-6">
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-2xl font-extrabold text-[#0F2744]">CONSULTINGS APD</h1>
            <p className="text-xs text-cyan-600 font-bold uppercase tracking-wider">Maturidade Digital & Oportunidade Comercial</p>
          </div>
          <div className="text-right text-xs text-gray-500">
            <p className="font-medium">Data de Emissão: {new Date().toLocaleDateString('pt-BR')}</p>
            <p>Código do Lead: {lead.id.substring(0, 8).toUpperCase()}</p>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-3 italic border-t border-gray-100 pt-2">
          Relatório de auditoria técnica da presença digital preparado para: <strong className="text-gray-950">{lead.name}</strong>
        </p>
      </div>

      {/* Back button (oculto na impressão) */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors no-print"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Voltar à campanha
      </button>

      {/* Header (oculto/adaptado na impressão via no-print nas ações) */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-gray-900">{lead.name}</h1>
          <Badge variant={getPriorityVariant(lead.priority)} size="md">
            {priorityConf.label || lead.priority}
          </Badge>
        </div>

        {/* Botão de Exportar para PDF (escondido na impressão) */}
        {diagnostic && diagnostic.diagnostic_status !== 'ai_validation_failed' && (
          <Button
            onClick={() => window.print()}
            variant="secondary"
            className="flex items-center gap-2 no-print"
          >
            📄 Exportar Diagnóstico (PDF)
          </Button>
        )}
      </div>

      {/* Resumo de Scores de Venda */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 no-print">
        {/* DMS */}
        <Card className="bg-gradient-to-br from-white to-slate-50 border-l-4 border-cyan-500 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 transform translate-x-4 -translate-y-4 text-cyan-500/5 text-9xl font-bold select-none pointer-events-none group-hover:scale-110 transition-transform duration-500">DMS</div>
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Maturidade Digital (DMS)</h3>
              <p className="text-xs text-gray-500 mt-1">Mede a qualidade técnica do site, SEO, GBP e redes sociais.</p>
            </div>
            <div className="text-right">
              <span className={`text-4xl font-extrabold tracking-tight ${getScoreColor(lead.dms ?? 0)}`}>
                {lead.dms ?? 0}
              </span>
              <span className="text-sm font-semibold text-gray-400 ml-0.5">/100</span>
            </div>
          </div>
          <div className="mt-4">
            <ScoreBar value={lead.dms ?? 0} />
          </div>
        </Card>

        {/* COS */}
        <Card className="bg-gradient-to-br from-white to-slate-50 border-l-4 border-emerald-500 shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 transform translate-x-4 -translate-y-4 text-emerald-500/5 text-9xl font-bold select-none pointer-events-none group-hover:scale-110 transition-transform duration-500">COS</div>
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Oportunidade Comercial (COS)</h3>
              <p className="text-xs text-gray-500 mt-1">Mede a lacuna de vendas (reputação física excelente vs. presença digital fraca).</p>
            </div>
            <div className="text-right">
              <span className={`text-4xl font-extrabold tracking-tight ${getScoreColor(lead.cos ?? 0)}`}>
                {lead.cos ?? 0}
              </span>
              <span className="text-sm font-semibold text-gray-400 ml-0.5">/100</span>
            </div>
          </div>
          <div className="mt-4">
            <ScoreBar value={lead.cos ?? 0} />
          </div>
        </Card>
      </div>

      {/* Painel de Presença Digital — Os 4 Pilares (Padrão Dashboard Visual) */}
      <div>
        <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2 no-print">
          <span>📊</span> Painel de Presença Digital (4 Pilares)
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Pilar 1: Google Empresa */}
          <Card padding="p-5" className="flex flex-col justify-between border border-gray-200 shadow-sm hover:border-blue-200 transition-colors duration-300">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">1. Google Empresa</span>
                <span className="bg-blue-50 text-blue-600 p-1.5 rounded-lg">
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
                  </svg>
                </span>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl font-extrabold text-gray-900">{lead.google_rating ?? '—'}</span>
                    <span className="text-xs text-gray-400 font-semibold">/ 5.0</span>
                  </div>
                  <div className="flex mt-1">{renderStars(lead.google_rating)}</div>
                </div>
                <div className="text-xs text-gray-500">
                  <strong className="text-gray-900 font-bold">{lead.google_reviews_count ?? 0}</strong> avaliações no Google Maps
                </div>
              </div>
            </div>
            
            <div className="mt-5 pt-3 border-t border-gray-100 space-y-1.5 text-xs text-gray-500">
              <div className="flex items-center justify-between">
                <span>Telefone:</span>
                <span className={`font-semibold ${lead.phone ? 'text-green-600' : 'text-gray-400'}`}>
                  {lead.phone ? '✓ Presente' : '✗ Ausente'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Endereço:</span>
                <span className={`font-semibold ${lead.address ? 'text-green-600' : 'text-gray-400'}`}>
                  {lead.address ? '✓ Presente' : '✗ Ausente'}
                </span>
              </div>
            </div>
          </Card>

          {/* Pilar 2: Website & SEO */}
          <Card padding="p-5" className="flex flex-col justify-between border border-gray-200 shadow-sm hover:border-cyan-200 transition-colors duration-300">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">2. Website & SEO</span>
                <span className="bg-cyan-50 text-cyan-600 p-1.5 rounded-lg">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </span>
              </div>
              
              {lead.has_website ? (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-baseline gap-1">
                      <span className={`text-3xl font-extrabold ${getScoreColor(lead.pagespeed_score ?? 0)}`}>
                        {lead.pagespeed_score ?? '—'}
                      </span>
                      <span className="text-xs text-gray-400 font-semibold">/100</span>
                    </div>
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wide">PageSpeed Score</span>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-1 bg-gray-50 rounded border border-gray-100">
                      <p className="text-[9px] font-bold text-gray-400">LCP</p>
                      <p className="text-xs font-bold text-gray-700 mt-0.5">
                        {lead.lcp_ms != null ? `${(lead.lcp_ms / 1000).toFixed(1)}s` : '—'}
                      </p>
                    </div>
                    <div className="p-1 bg-gray-50 rounded border border-gray-100">
                      <p className="text-[9px] font-bold text-gray-400">INP</p>
                      <p className="text-xs font-bold text-gray-700 mt-0.5">
                        {lead.inp_ms != null ? `${lead.inp_ms}ms` : '—'}
                      </p>
                    </div>
                    <div className="p-1 bg-gray-50 rounded border border-gray-100">
                      <p className="text-[9px] font-bold text-gray-400">SEO</p>
                      <p className="text-xs font-bold text-gray-700 mt-0.5">
                        {lead.seo_score != null ? `${lead.seo_score}` : '—'}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col justify-center py-2 text-center">
                  <span className="text-red-500 font-bold text-xs uppercase tracking-wider">⚠️ Sem Website</span>
                  <p className="text-[11px] text-gray-400 mt-1">Oportunidade ideal para criação de site no Google Stitch.</p>
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100 text-center">
              {lead.website ? (
                <a
                  href={lead.website.startsWith('http') ? lead.website : `https://${lead.website}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-bold text-cyan-600 hover:text-cyan-700 hover:underline inline-flex items-center gap-1"
                >
                  Acessar Website ↗
                </a>
              ) : (
                <span className="text-xs text-gray-400 italic">Nenhum site cadastrado</span>
              )}
            </div>
          </Card>

          {/* Pilar 3: Instagram */}
          <Card padding="p-5" className="flex flex-col justify-between border border-gray-200 shadow-sm hover:border-pink-200 transition-colors duration-300">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">3. Instagram</span>
                <span className="bg-pink-50 text-pink-600 p-1.5 rounded-lg">
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.051.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
                  </svg>
                </span>
              </div>
              
              <div className="space-y-3">
                <div>
                  <Badge variant={lead.has_instagram ? 'success' : 'danger'} size="md">
                    {lead.has_instagram ? '✓ Perfil Ativo' : '✗ Sem Perfil'}
                  </Badge>
                </div>
                
                {lead.has_instagram ? (
                  <p className="text-xs text-gray-500 leading-relaxed">
                    Último post detectado a: <strong className="text-gray-900 font-semibold">{lead.social_last_post_days !== null ? `${lead.social_last_post_days} dias` : '—'}</strong>
                  </p>
                ) : (
                  <p className="text-[11px] text-gray-400">
                    Rede social essencial para conversão e validação social do negócio.
                  </p>
                )}
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-gray-100 text-center flex flex-col items-center gap-2">
              <span className={`text-xs font-bold ${lead.has_instagram && lead.social_last_post_days < 30 ? 'text-green-600' : 'text-amber-500'}`}>
                {lead.has_instagram 
                  ? (lead.social_last_post_days < 30 ? '🔥 Presença Ativa' : '⏳ Falta Frequência') 
                  : '⚠️ Grande Gap Social'}
              </span>
              {lead.instagram_url && (
                <a
                  href={lead.instagram_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-bold text-pink-600 hover:text-pink-700 hover:underline inline-flex items-center gap-1"
                >
                  Acessar Instagram ↗
                </a>
              )}
            </div>
          </Card>

          {/* Pilar 4: LinkedIn */}
          <Card padding="p-5" className="flex flex-col justify-between border border-gray-200 shadow-sm hover:border-indigo-200 transition-colors duration-300">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">4. LinkedIn</span>
                <span className="bg-indigo-50 text-indigo-600 p-1.5 rounded-lg">
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                  </svg>
                </span>
              </div>
              
              <div className="space-y-3">
                <div>
                  <Badge variant={lead.has_linkedin ? 'success' : 'default'} size="md">
                    {lead.has_linkedin ? '✓ Perfil Corporativo' : '— Sem Perfil'}
                  </Badge>
                </div>
                
                <p className="text-[11px] text-gray-400 leading-relaxed">
                  {lead.has_linkedin 
                    ? 'Excelente para prospecção corporativa e conexão com diretores.' 
                    : 'Foco atual no varejo. Espaço para prospecção de parcerias B2B.'}
                </p>
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-gray-100 text-center">
              <span className="text-xs font-bold text-gray-500">
                {lead.has_linkedin ? '💼 Conexão B2B' : '🌐 Foco Offline/B2C'}
              </span>
            </div>
          </Card>
        </div>
      </div>

      {/* Diagnostic section */}
      {(!diagnostic || diagnostic.diagnostic_status === 'ai_validation_failed') && !diagLoading && (
        <Card className="py-10">
          <div className="text-center">
            {diagnostic?.diagnostic_status === 'ai_validation_failed' ? (
              <div className="space-y-4 max-w-xl mx-auto">
                <span className="text-3xl block">❌</span>
                <p className="text-lg font-semibold text-red-800">Falha ao Gerar Diagnóstico com IA</p>
                <p className="text-sm text-red-600">
                  O provedor de Inteligência Artificial falhou ao analisar os dados do lead. Detalhes do erro:
                </p>
                <p className="text-xs font-mono bg-red-100 border border-red-200 rounded p-3 text-red-700 text-left whitespace-pre-wrap">
                  {diagnostic.error_message || 'Erro desconhecido na geração do Gemini.'}
                </p>
                <div className="pt-2">
                  <Button size="lg" onClick={handleGenerateDiagnostic}>
                    Tentar Gerar Novamente 🔄
                  </Button>
                </div>
              </div>
            ) : (
              <>
                <p className="text-gray-500 mb-4">Nenhum diagnóstico gerado para este lead.</p>
                <Button size="lg" onClick={handleGenerateDiagnostic}>
                  Gerar Diagnóstico com IA 🤖
                </Button>
              </>
            )}
            {diagError && (
              <p className="text-sm text-red-600 mt-3">{diagError}</p>
            )}
          </div>
        </Card>
      )}

      {diagLoading && (
        <Card className="text-center py-10">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin w-8 h-8 border-3 border-cyan-500 border-t-transparent rounded-full" />
            <div>
              <p className="text-sm font-medium text-gray-700">Gerando diagnóstico com IA...</p>
              <p className="text-xs text-gray-400 mt-1">Isso pode levar alguns segundos</p>
            </div>
          </div>
        </Card>
      )}

      {diagnostic && diagnostic.diagnostic_status !== 'ai_validation_failed' && (
        <>
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">📋 Diagnóstico</h2>
            <DiagnosticTabs diagnostic={diagnostic} />
          </Card>

          <div className="no-print" id="email-draft-card">
            <EmailDraft 
              emailText={diagnostic.email_draft || diagnostic.email_text || ''} 
              whatsappText={diagnostic.whatsapp_draft || ''}
              instagramText={diagnostic.instagram_draft || ''}
            />
          </div>
        </>
      )}
    </div>
  );
}
