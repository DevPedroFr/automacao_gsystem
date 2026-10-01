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
import PrintReport from '@/components/diagnostics/PrintReport';
import { PRIORITY_CONFIG } from '@/lib/constants';
import { ChevronLeft, Download, MapPin, Globe, RefreshCw, AlertTriangle, Activity, MessageSquare } from 'lucide-react';

const InstagramIcon = ({ size = 18, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect width="20" height="20" x="2" y="2" rx="5" ry="5"/>
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
    <line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>
  </svg>
);

const LinkedinIcon = ({ size = 18, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
    <rect width="4" height="12" x="2" y="9"/>
    <circle cx="4" cy="4" r="2"/>
  </svg>
);

export default function LeadDetailPage() {
  const params = useParams();
  const router = useRouter();
  const leadId = params.id;

  const [lead, setLead] = useState(null);
  const [diagnostic, setDiagnostic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [leadError, setLeadError] = useState(null);
  const [diagLoading, setDiagLoading] = useState(false);
  const [diagError, setDiagError] = useState('');
  const [showCandidates, setShowCandidates] = useState(false);

  const loadLead = useCallback(async () => {
    try {
      setLeadError(null);
      const data = await fetchApi(`/leads/${leadId}`);
      const leadData = data?.data || data;
      setLead(leadData);
      if (leadData?.diagnostic) {
        setDiagnostic(leadData.diagnostic);
      }
    } catch (err) {
      console.error('Erro ao carregar lead:', err);
      setLeadError(err.message || 'Erro ao carregar dados do lead');
    }
  }, [leadId]);

  const loadDiagnostic = useCallback(async () => {
    try {
      const data = await fetchApi(`/leads/${leadId}/diagnostic`);
      if (data?.data || data) {
        setDiagnostic(data.data || data);
      }
    } catch {
      // 404 significa que o diagnóstico ainda não foi gerado
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

  const handleSelectInstagram = async (handle) => {
    try {
      setDiagLoading(true);
      await fetchApi(`/leads/${leadId}/select-instagram`, {
        method: 'POST',
        body: JSON.stringify({ handle })
      });
      // After selecting, trigger diagnostic generation again
      await handleGenerateDiagnostic();
      await loadLead(); // Reload lead data to hide candidates
    } catch (err) {
      console.error(err);
      setDiagError('Erro ao selecionar perfil: ' + err.message);
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
        <div className="h-8 bg-gray-800/60 rounded-xl w-64 animate-pulse-soft border border-gray-700/30" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-gray-900/60 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 h-32 animate-pulse-soft" />
          ))}
        </div>
      </div>
    );
  }

  if (leadError) {
    return (
      <div className="text-center py-20 space-y-4">
        <div className="w-16 h-16 bg-rose-500/10 border border-rose-500/25 text-rose-400 rounded-full flex items-center justify-center mx-auto text-2xl">
          ⚠️
        </div>
        <h2 className="text-xl font-bold text-gray-100">Não foi possível carregar os dados deste lead</h2>
        <p className="text-sm text-gray-400 max-w-md mx-auto">{leadError}</p>
        <div className="flex justify-center gap-3 pt-2">
          <Button variant="secondary" onClick={() => router.back()}>
            Voltar
          </Button>
          <Button onClick={() => {
            setLoading(true);
            Promise.all([loadLead(), loadDiagnostic()]).finally(() => setLoading(false));
          }}>
            Tentar Novamente 🔄
          </Button>
        </div>
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="text-center py-20">
        <p className="text-lg text-gray-400">Lead não encontrado</p>
        <Button variant="secondary" className="mt-4" onClick={() => router.back()}>
          Voltar
        </Button>
      </div>
    );
  }


  const priorityConf = PRIORITY_CONFIG[lead.priority] || {};

  const handleExportPdf = () => {
    const originalTitle = document.title;
    document.title = lead?.name ? `Diagnóstico - ${lead.name}` : 'Diagnóstico Comercial';
    window.print();
    setTimeout(() => {
      document.title = originalTitle;
    }, 1500);
  };

  return (
    <div className="animate-fade-in">
      {/* O relatório de impressão fica invisível na tela e visível apenas no print */}
      <PrintReport lead={lead} diagnostic={diagnostic} />

      {/* Todo o conteúdo da tela fica oculto na impressão */}
      <div className="space-y-8 no-print">
      {/* Back button */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-cyan-400 transition-colors no-print font-medium"
      >
        <ChevronLeft size={16} />
        Voltar à campanha
      </button>

      {/* Header (oculto/adaptado na impressão via no-print nas ações) */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-gray-100">{lead.name}</h1>
          <Badge variant={getPriorityVariant(lead.priority)} size="md">
            {priorityConf.label || lead.priority}
          </Badge>
        </div>

        {/* Botão de Exportar para PDF (escondido na impressão) */}
        {diagnostic && diagnostic.diagnostic_status !== 'ai_validation_failed' && (
          <Button
            onClick={handleExportPdf}
            variant="secondary"
            className="flex items-center gap-2 no-print bg-gray-800 hover:bg-gray-700 text-gray-200 border-gray-700"
          >
            <Download size={16} /> Exportar Diagnóstico (PDF)
          </Button>
        )}
      </div>

      {/* ÁREA DE CONTATO / VENDAS */}
      <div className="no-print">
        <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider mb-4 flex items-center gap-2">
          💰 Área de Vendas & Contato
        </h2>
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Info do Cliente */}
          <div className="xl:col-span-1 flex flex-col gap-4">
            <Card padding="p-5" className="border-t-4 border-t-blue-500 h-full">
              <div className="flex flex-col h-full gap-6">
                <div>
                  <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Telefone / WhatsApp</p>
                  <div className="flex flex-col gap-2">
                    <span className="text-xl font-medium text-gray-200">
                      {lead.phone || 'Telefone não disponível'}
                    </span>
                    {lead.phone && (
                      <a 
                        href={`https://wa.me/${lead.phone.replace(/\D/g, '')}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="bg-green-600 hover:bg-green-500 text-white text-sm font-bold px-4 py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 mt-2"
                      >
                        <MessageSquare size={16} /> Abrir WhatsApp Web
                      </a>
                    )}
                  </div>
                </div>
                
                <div>
                  <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Endereço</p>
                  <div className="flex items-start gap-2 bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                    <MapPin size={18} className="text-gray-400 mt-0.5 shrink-0" />
                    <span className="text-sm font-medium text-gray-300 leading-relaxed">
                      {lead.address || lead.city || 'Endereço não disponível'}
                    </span>
                  </div>
                </div>

                {lead.instagram_url && (
                  <div>
                    <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Instagram</p>
                    <a 
                      href={lead.instagram_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-400 hover:text-cyan-300 text-sm font-medium flex items-center gap-2 truncate bg-gray-900/50 p-3 rounded-lg border border-gray-800 hover:border-cyan-500/30 transition-colors"
                    >
                      <InstagramIcon size={16} />
                      {lead.instagram_url.replace('https://instagram.com/', '@').replace('https://www.instagram.com/', '@')}
                    </a>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Mensagem de Venda (Só aparece se o diagnóstico estiver pronto) */}
          <div className="xl:col-span-2">
            {diagnostic && diagnostic.diagnostic_status !== 'ai_validation_failed' && (diagnostic.email_draft || diagnostic.whatsapp_draft || diagnostic.instagram_draft) ? (
              <EmailDraft 
                emailText={diagnostic.email_draft || diagnostic.email_text || ''} 
                whatsappText={diagnostic.whatsapp_draft || ''}
                instagramText={diagnostic.instagram_draft || ''}
              />
            ) : (

              <Card padding="p-8" className="h-full flex flex-col items-center justify-center text-center border-dashed border-2 border-gray-700 bg-gray-900/20">
                <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mb-4">
                  <MessageSquare className="text-gray-500" size={24} />
                </div>
                <h3 className="text-gray-300 font-bold mb-2">Gere o Diagnóstico para ver as mensagens</h3>
                <p className="text-sm text-gray-500 max-w-sm mb-6">
                  A inteligência artificial vai criar mensagens de abordagem personalizadas baseadas nas dores técnicas deste cliente.
                </p>
                <Button 
                  onClick={handleGenerateDiagnostic}
                  disabled={diagLoading}
                  className="bg-cyan-600 hover:bg-cyan-500"
                >
                  {diagLoading ? 'Processando IA...' : 'Gerar Diagnóstico Agora'}
                </Button>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Resumo de Scores de Venda Premium */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 no-print">
        {/* DMS */}
        <Card className="border-l-4 border-l-cyan-500 relative group overflow-hidden" padding="p-6">
          <div className="absolute -right-10 -top-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none group-hover:bg-cyan-500/20 transition-colors duration-500" />
          <div className="absolute top-0 right-0 transform translate-x-4 -translate-y-4 text-cyan-500/5 text-8xl font-black select-none pointer-events-none group-hover:scale-110 transition-transform duration-500">DMS</div>
          <div className="flex justify-between items-start mb-2 relative z-10">
            <div>
              <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                <Activity size={14} /> Maturidade Digital (DMS)
              </h3>
              <p className="text-xs text-gray-400 mt-1 max-w-[80%]">Mede a qualidade técnica do site, SEO, GBP e redes sociais.</p>
            </div>
            <div className="text-right">
              <span className={`text-5xl font-extrabold tracking-tighter drop-shadow-md ${getScoreColor(lead.dms ?? 0)}`}>
                {lead.dms ?? 0}
              </span>
              <span className="text-sm font-semibold text-gray-500 ml-0.5">/100</span>
            </div>
          </div>
          <div className="mt-6 relative z-10">
            <ScoreBar value={lead.dms ?? 0} />
          </div>
        </Card>

        {/* COS */}
        <Card className="border-l-4 border-l-emerald-500 relative group overflow-hidden" padding="p-6">
          <div className="absolute -right-10 -top-10 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none group-hover:bg-emerald-500/20 transition-colors duration-500" />
          <div className="absolute top-0 right-0 transform translate-x-4 -translate-y-4 text-emerald-500/5 text-8xl font-black select-none pointer-events-none group-hover:scale-110 transition-transform duration-500">COS</div>
          <div className="flex justify-between items-start mb-2 relative z-10">
            <div>
              <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <Globe size={14} /> Oportunidade (COS)
              </h3>
              <p className="text-xs text-gray-400 mt-1 max-w-[80%]">Mede a lacuna de vendas e potencial de melhoria.</p>
            </div>
            <div className="text-right">
              <span className={`text-5xl font-extrabold tracking-tighter drop-shadow-md ${getScoreColor(lead.cos ?? 0)}`}>
                {lead.cos ?? 0}
              </span>
              <span className="text-sm font-semibold text-gray-500 ml-0.5">/100</span>
            </div>
          </div>
          <div className="mt-6 relative z-10">
            <ScoreBar value={lead.cos ?? 0} />
          </div>
        </Card>
      </div>

      {/* Painel de Presença Digital — Os 4 Pilares (Padrão Dashboard Visual) */}
      <div>
        <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider mb-4 flex items-center gap-2 no-print">
          <Activity size={18} className="text-cyan-400" /> Painel de Presença Digital (4 Pilares)
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 no-print">
          {/* Pilar 1: Google Empresa */}
          <Card padding="p-5" className="flex flex-col justify-between group hover:border-blue-500/40">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">1. Google Empresa</span>
                <span className="bg-blue-500/10 text-blue-400 p-2 rounded-xl border border-blue-500/20 group-hover:scale-110 transition-transform duration-300">
                  <MapPin size={18} />
                </span>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl font-extrabold text-gray-100">{lead.google_rating ?? '—'}</span>
                    <span className="text-xs text-gray-500 font-semibold">/ 5.0</span>
                  </div>
                  <div className="flex mt-1">{renderStars(lead.google_rating)}</div>
                </div>
                <div className="text-xs text-gray-400">
                  <strong className="text-gray-200 font-bold">{lead.google_reviews_count ?? 0}</strong> avaliações no Google Maps
                </div>
              </div>
            </div>
            
            <div className="mt-5 pt-3 border-t border-gray-700/50 space-y-2 text-xs text-gray-400">
              <div className="flex items-center justify-between">
                <span>Telefone:</span>
                <span className={`font-semibold ${lead.phone ? 'text-emerald-400' : 'text-gray-500'}`}>
                  {lead.phone ? '✓ Presente' : '✗ Ausente'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Endereço:</span>
                <span className={`font-semibold ${lead.address ? 'text-emerald-400' : 'text-gray-500'}`}>
                  {lead.address ? '✓ Presente' : '✗ Ausente'}
                </span>
              </div>
            </div>
          </Card>

          {/* Pilar 2: Website & SEO */}
          <Card padding="p-5" className="flex flex-col justify-between group hover:border-cyan-500/40">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">2. Website & SEO</span>
                <span className="bg-cyan-500/10 text-cyan-400 p-2 rounded-xl border border-cyan-500/20 group-hover:scale-110 transition-transform duration-300">
                  <Globe size={18} />
                </span>
              </div>
              
              {lead.has_website ? (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-baseline gap-1">
                      <span className={`text-3xl font-extrabold ${getScoreColor(lead.pagespeed_score ?? 0)}`}>
                        {lead.pagespeed_score ?? '—'}
                      </span>
                      <span className="text-xs text-gray-500 font-semibold">/100</span>
                    </div>
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wide">PageSpeed Score</span>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-1 bg-gray-800/50 rounded border border-gray-700/50">
                      <p className="text-[9px] font-bold text-gray-500">LCP</p>
                      <p className="text-xs font-bold text-gray-300 mt-0.5">
                        {lead.lcp_ms != null ? `${(lead.lcp_ms / 1000).toFixed(1)}s` : '—'}
                      </p>
                    </div>
                    <div className="p-1 bg-gray-800/50 rounded border border-gray-700/50">
                      <p className="text-[9px] font-bold text-gray-500">INP</p>
                      <p className="text-xs font-bold text-gray-300 mt-0.5">
                        {lead.inp_ms != null ? `${lead.inp_ms}ms` : '—'}
                      </p>
                    </div>
                    <div className="p-1 bg-gray-800/50 rounded border border-gray-700/50">
                      <p className="text-[9px] font-bold text-gray-500">SEO</p>
                      <p className="text-xs font-bold text-gray-300 mt-0.5">
                        {lead.seo_score != null ? `${lead.seo_score}` : '—'}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col justify-center py-2 text-center">
                  <div className="flex items-center justify-center gap-1 text-rose-400 font-bold text-xs uppercase tracking-wider">
                    <AlertTriangle size={14} /> Sem Website
                  </div>
                  <p className="text-[11px] text-gray-500 mt-2">Oportunidade ideal para criação de site no Google Stitch.</p>
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-gray-700/50 text-center">
              {lead.website ? (
                <a
                  href={lead.website.startsWith('http') ? lead.website : `https://${lead.website}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-bold text-cyan-400 hover:text-cyan-300 hover:underline inline-flex items-center gap-1"
                >
                  Acessar Website ↗
                </a>
              ) : (
                <span className="text-xs text-gray-500 italic">Nenhum site cadastrado</span>
              )}
            </div>
          </Card>

          {/* Pilar 3: Instagram */}
          <Card padding="p-5" className="flex flex-col justify-between group hover:border-pink-500/40 relative">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">3. Instagram</span>
                <span className="bg-pink-500/10 text-pink-400 p-2 rounded-xl border border-pink-500/20 group-hover:scale-110 transition-transform duration-300">
                  <InstagramIcon size={18} />
                </span>
              </div>
              
              <div className="space-y-3">
                <div>
                  <Badge variant={lead.has_instagram ? 'success' : 'danger'} size="md">
                    {lead.has_instagram ? '✓ Perfil Ativo' : '✗ Sem Perfil'}
                  </Badge>
                </div>
                
                {lead.has_instagram ? (
                  <p className="text-xs text-gray-400 leading-relaxed">
                    Último post detectado a: <strong className="text-gray-200 font-semibold">{lead.social_last_post_days !== null ? `${lead.social_last_post_days} dias` : '—'}</strong>
                  </p>
                ) : (
                  <p className="text-[11px] text-gray-500">
                    Rede social essencial para conversão e validação social do negócio.
                  </p>
                )}
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-gray-700/50 text-center flex flex-col items-center gap-2">
              <span className={`text-xs font-bold ${lead.has_instagram && lead.social_last_post_days < 30 ? 'text-emerald-400' : 'text-amber-400'}`}>
                {lead.has_instagram 
                  ? (lead.social_last_post_days < 30 ? '🔥 Presença Ativa' : '⏳ Falta Frequência') 
                  : '⚠️ Grande Gap Social'}
              </span>
              {lead.instagram_url && (
                <a
                  href={lead.instagram_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-bold text-pink-400 hover:text-pink-300 hover:underline inline-flex items-center gap-1"
                >
                  Acessar Instagram ↗
                </a>
              )}
            </div>

            {/* Sugestões de Candidatos */}
            {!lead.has_instagram && lead.instagram_candidates && (
              <div className="mt-4 pt-3 border-t border-gray-700/50">
                <Button 
                  variant="secondary" 
                  size="sm" 
                  className="w-full text-xs py-2 bg-pink-500/10 text-pink-400 hover:bg-pink-500/20 border-pink-500/20"
                  onClick={() => setShowCandidates(true)}
                >
                  <InstagramIcon size={14} className="mr-2" />
                  Ver possíveis perfis
                </Button>
              </div>
            )}
          </Card>

          {/* Pilar 4: LinkedIn */}
          <Card padding="p-5" className="flex flex-col justify-between group hover:border-indigo-500/40">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">4. LinkedIn</span>
                <span className="bg-indigo-500/10 text-indigo-400 p-2 rounded-xl border border-indigo-500/20 group-hover:scale-110 transition-transform duration-300">
                  <LinkedinIcon size={18} />
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

            <div className="mt-5 pt-3 border-t border-gray-700/50 text-center">
              <span className="text-xs font-bold text-gray-400">
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
                <p className="text-lg font-semibold text-rose-400">Falha ao Gerar Diagnóstico com IA</p>
                <p className="text-sm text-rose-300/80">
                  O provedor de Inteligência Artificial falhou ao analisar os dados do lead. Detalhes do erro:
                </p>
                <p className="text-xs font-mono bg-rose-950/40 border border-rose-500/20 rounded-xl p-3 text-rose-300 text-left whitespace-pre-wrap">
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
                <p className="text-gray-400 mb-4">
                  Nenhum diagnóstico gerado para este lead.
                </p>
                <Button size="lg" onClick={handleGenerateDiagnostic} className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 shadow-[0_0_15px_rgba(6,182,212,0.4)] border-0">
                  <RefreshCw className="inline-block mr-2" size={18} /> Gerar Diagnóstico com IA
                </Button>
              </>
            )}
            {diagError && (
              <p className="text-sm text-rose-400 mt-3">{diagError}</p>
            )}
          </div>
        </Card>
      )}


      {diagLoading && (
        <Card className="text-center py-10">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin w-8 h-8 border-3 border-cyan-500 border-t-transparent rounded-full" />
            <div>
              <p className="text-sm font-semibold text-gray-200">Gerando diagnóstico com IA...</p>
              <p className="text-xs text-gray-400 mt-1">Isso pode levar alguns segundos</p>
            </div>
          </div>
        </Card>
      )}

      {diagnostic && diagnostic.diagnostic_status !== 'ai_validation_failed' && (
        <>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-100">📋 Diagnóstico Detalhado</h2>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleGenerateDiagnostic}
                disabled={diagLoading}
                className="hover:border-cyan-500/50"
              >
                {diagLoading ? 'Processando IA...' : '🔄 Regenerar Diagnóstico'}
              </Button>
            </div>
            <DiagnosticTabs diagnostic={diagnostic} />
          </Card>
        </>
      )}
      </div>

      {/* Modal de Candidatos de Instagram */}
      {showCandidates && lead?.instagram_candidates && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowCandidates(false)} />
          <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl z-10 w-full max-w-md overflow-hidden animate-scale-up">
            <div className="p-5 border-b border-gray-800 flex justify-between items-center">
              <h3 className="font-bold text-gray-100 flex items-center gap-2">
                <InstagramIcon className="text-pink-400" /> Possíveis Perfis
              </h3>
              <button onClick={() => setShowCandidates(false)} className="text-gray-400 hover:text-white p-1">
                ✕
              </button>
            </div>
            <div className="p-5 space-y-2 max-h-[60vh] overflow-y-auto custom-scrollbar">
              {(() => {
                try {
                  const cands = JSON.parse(lead.instagram_candidates);
                  return cands.map(cand => (
                    <button
                      key={cand}
                      onClick={() => {
                        setShowCandidates(false);
                        handleSelectInstagram(cand);
                      }}
                      className="w-full text-left bg-gray-800/50 hover:bg-gray-700 text-gray-200 px-4 py-3 rounded-xl transition-colors border border-gray-700 hover:border-pink-500/50 flex justify-between items-center group"
                    >
                      <span className="font-medium">@{cand}</span>
                      <span className="text-xs font-bold text-pink-500/0 group-hover:text-pink-400 transition-colors">Selecionar →</span>
                    </button>
                  ));
                } catch (e) {
                  return <p className="text-sm text-gray-400">Erro ao carregar candidatos.</p>;
                }
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
