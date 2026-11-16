'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import NewCampaignModal from '@/components/campaigns/NewCampaignModal';
import { STATUS_CONFIG } from '@/lib/constants';
import {
  Rocket, Play, RotateCw, Pause, Trash2, Download, ExternalLink,
  Plus, Search, Filter, Sparkles, CheckCircle2, AlertCircle, Clock,
  Globe, MapPin, Users, Flame, LayoutGrid, List, RefreshCw
} from 'lucide-react';

export default function CampaignsPage() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [viewMode, setViewMode] = useState('cards'); // 'cards' | 'table'
  const [actionLoading, setActionLoading] = useState({});
  const [showModal, setShowModal] = useState(false);
  const [feedback, setFeedback] = useState(null);

  // Carrega campanhas com suas estatísticas agregadas
  const loadCampaigns = useCallback(async (silent = false) => {
    try {
      if (!silent) setIsRefreshing(true);
      const res = await fetchApi('/campaigns');
      const list = res.data || res.campaigns || (Array.isArray(res) ? res : []);
      setCampaigns(list);
    } catch (err) {
      console.error('Erro ao carregar campanhas:', err);
    } finally {
      if (!silent) {
        setIsRefreshing(false);
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    loadCampaigns();
  }, [loadCampaigns]);

  // Polling automático inteligente enquanto houver campanhas em processamento
  const hasProcessing = useMemo(() => {
    return campaigns.some((c) => c.status === 'processing');
  }, [campaigns]);

  useEffect(() => {
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      loadCampaigns(true);
    }, 4000);

    return () => clearInterval(interval);
  }, [hasProcessing, loadCampaigns]);

  // Limpa feedback após 5 segundos
  useEffect(() => {
    if (!feedback) return;
    const timer = setTimeout(() => setFeedback(null), 5000);
    return () => clearTimeout(timer);
  }, [feedback]);

  // Métricas Globais consolidadas
  const summary = useMemo(() => {
    const total = campaigns.length;
    const processing = campaigns.filter((c) => c.status === 'processing').length;
    const completed = campaigns.filter((c) => c.status === 'completed').length;
    const totalLeads = campaigns.reduce((acc, c) => acc + (c.total_leads || 0), 0);
    const totalPriorityA = campaigns.reduce((acc, c) => acc + (c.priority_a || 0), 0);
    const totalWithoutWeb = campaigns.reduce((acc, c) => acc + (c.without_website || 0), 0);

    return {
      total,
      processing,
      completed,
      totalLeads,
      totalPriorityA,
      totalWithoutWeb,
    };
  }, [campaigns]);

  // Filtragem e busca
  const filteredCampaigns = useMemo(() => {
    return campaigns.filter((c) => {
      const matchesSearch =
        !searchQuery.trim() ||
        c.niche?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.location?.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesStatus =
        statusFilter === 'all' ||
        (statusFilter === 'processing' && c.status === 'processing') ||
        (statusFilter === 'completed' && c.status === 'completed') ||
        (statusFilter === 'cancelled' && (c.status === 'cancelled' || c.status === 'paused')) ||
        (statusFilter === 'failed' && c.status === 'failed');

      return matchesSearch && matchesStatus;
    });
  }, [campaigns, searchQuery, statusFilter]);

  // Ação: Ativar / Reativar Campanha
  const handleActivateCampaign = async (campaignId, e) => {
    if (e) e.stopPropagation();
    try {
      setActionLoading((prev) => ({ ...prev, [campaignId]: 'activating' }));
      const res = await fetchApi(`/campaigns/${campaignId}/activate`, { method: 'POST' });

      // Atualiza status localmente de imediato
      setCampaigns((prev) =>
        prev.map((c) => (c.id === campaignId ? { ...c, status: 'processing', error_message: null } : c))
      );

      setFeedback({
        type: 'success',
        message: '⚡ Campanha ativada com sucesso! A automação está buscando e qualificando leads no Google.',
      });

      // Recarrega dados completos
      await loadCampaigns(true);
    } catch (err) {
      console.error('Erro ao ativar campanha:', err);
      setFeedback({
        type: 'error',
        message: err.message || 'Não foi possível ativar a campanha.',
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [campaignId]: null }));
    }
  };

  // Ação: Pausar / Cancelar Campanha
  const handleCancelCampaign = async (campaignId, e) => {
    if (e) e.stopPropagation();
    if (!window.confirm('Deseja pausar esta campanha? Os leads já encontrados continuarão salvos.')) return;

    try {
      setActionLoading((prev) => ({ ...prev, [campaignId]: 'cancelling' }));
      await fetchApi(`/campaigns/${campaignId}/cancel`, { method: 'POST' });

      setCampaigns((prev) =>
        prev.map((c) => (c.id === campaignId ? { ...c, status: 'cancelled' } : c))
      );

      setFeedback({
        type: 'success',
        message: 'Campanha pausada com sucesso. Você pode reativá-la quando quiser.',
      });

      await loadCampaigns(true);
    } catch (err) {
      console.error('Erro ao pausar campanha:', err);
      setFeedback({
        type: 'error',
        message: err.message || 'Não foi possível pausar a campanha.',
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [campaignId]: null }));
    }
  };

  // Ação: Excluir Campanha
  const handleDeleteCampaign = async (campaignId, niche, e) => {
    if (e) e.stopPropagation();
    if (!window.confirm(`Tem certeza que deseja excluir a campanha "${niche}"? Todos os leads associados serão removidos.`)) {
      return;
    }

    try {
      setActionLoading((prev) => ({ ...prev, [campaignId]: 'deleting' }));
      await fetchApi(`/campaigns/${campaignId}`, { method: 'DELETE' });

      setCampaigns((prev) => prev.filter((c) => c.id !== campaignId));

      setFeedback({
        type: 'success',
        message: `Campanha "${niche}" excluída com sucesso.`,
      });
    } catch (err) {
      console.error('Erro ao excluir campanha:', err);
      setFeedback({
        type: 'error',
        message: err.message || 'Não foi possível excluir a campanha.',
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [campaignId]: null }));
    }
  };

  // Ação: Exportar Leads (CSV)
  const handleExportCSV = async (campaignId, niche, e) => {
    if (e) e.stopPropagation();
    try {
      setActionLoading((prev) => ({ ...prev, [campaignId]: 'exporting' }));
      const csvData = await fetchApi(`/campaigns/${campaignId}/leads/export`);
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `leads_${niche || 'campanha'}_${campaignId}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erro ao exportar CSV:', err);
      alert('Não foi possível exportar os leads.');
    } finally {
      setActionLoading((prev) => ({ ...prev, [campaignId]: null }));
    }
  };

  const handleCampaignSuccess = (result) => {
    setShowModal(false);
    loadCampaigns();
    setFeedback({
      type: 'success',
      message: '🚀 Nova campanha criada e disparada! A triagem digital já está rodando em segundo plano.',
    });
    const id = result?.data?.id || result?.id;
    if (id) {
      router.push(`/campaigns/${id}`);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status) => {
    const map = {
      processing: {
        variant: 'info',
        label: 'Em Execução',
        icon: <RotateCw size={12} className="animate-spin text-cyan-400" />,
        badgeClass: 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 animate-pulse',
      },
      completed: {
        variant: 'success',
        label: 'Concluída',
        icon: <CheckCircle2 size={12} className="text-emerald-400" />,
        badgeClass: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
      },
      cancelled: {
        variant: 'warning',
        label: 'Pausada',
        icon: <Clock size={12} className="text-amber-400" />,
        badgeClass: 'bg-amber-500/10 text-amber-400 border border-amber-500/30',
      },
      failed: {
        variant: 'danger',
        label: 'Falha',
        icon: <AlertCircle size={12} className="text-rose-400" />,
        badgeClass: 'bg-rose-500/10 text-rose-400 border border-rose-500/30',
      },
    };

    const cfg = map[status] || {
      variant: 'default',
      label: status || 'Desconhecido',
      icon: null,
      badgeClass: 'bg-gray-800 text-gray-400 border border-gray-700',
    };

    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${cfg.badgeClass}`}>
        {cfg.icon}
        {cfg.label}
      </span>
    );
  };

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Toast Feedback */}
      {feedback && (
        <div
          className={`fixed top-6 right-6 z-50 max-w-md p-4 rounded-2xl shadow-2xl backdrop-blur-xl border transition-all duration-300 flex items-start gap-3 ${
            feedback.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/40 text-emerald-200'
              : 'bg-rose-950/90 border-rose-500/40 text-rose-200'
          }`}
        >
          {feedback.type === 'success' ? (
            <Sparkles size={20} className="text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle size={20} className="text-rose-400 shrink-0 mt-0.5" />
          )}
          <div className="flex-1 text-sm font-medium">{feedback.message}</div>
          <button
            onClick={() => setFeedback(null)}
            className="text-gray-400 hover:text-white text-xs font-bold px-1"
          >
            ✕
          </button>
        </div>
      )}

      {/* Header Principal */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative">
          <div className="absolute -left-4 top-1 w-1 h-12 bg-gradient-to-b from-cyan-400 via-blue-500 to-purple-500 rounded-full" />
          <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-100 to-cyan-400 tracking-tight">
            Campanhas de Prospecção
          </h1>
          <p className="text-sm text-gray-400 mt-1 flex items-center gap-2">
            <span>Central de inteligência de mercado e ativação contínua de leads.</span>
            {hasProcessing && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                Automação ativa
              </span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadCampaigns()}
            disabled={isRefreshing}
            className="p-3 bg-gray-900/80 hover:bg-gray-800 border border-gray-700/60 rounded-xl text-gray-300 hover:text-white transition-all shadow-sm"
            title="Atualizar campanhas"
          >
            <RefreshCw size={18} className={isRefreshing ? 'animate-spin text-cyan-400' : ''} />
          </button>

          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white rounded-xl font-bold text-sm shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] transition-all duration-300 hover:-translate-y-0.5"
          >
            <Rocket size={18} />
            <span>⚡ Ativar Nova Campanha</span>
          </button>
        </div>
      </div>

      {/* Grid de Métricas Consolidadas das Campanhas */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Campanhas */}
        <div className="bg-gray-900/70 border border-gray-800 rounded-2xl p-4 shadow-sm hover:border-gray-700 transition-colors">
          <div className="flex items-center justify-between text-gray-400 mb-2">
            <span className="text-xs uppercase font-bold tracking-wider">Campanhas</span>
            <Rocket size={16} className="text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white">{summary.total}</div>
          <div className="text-[11px] text-gray-500 mt-1">
            {summary.completed} concluídas
          </div>
        </div>

        {/* Em Execução */}
        <div className="bg-cyan-950/20 border border-cyan-800/40 rounded-2xl p-4 shadow-sm hover:border-cyan-700/60 transition-colors">
          <div className="flex items-center justify-between text-cyan-400 mb-2">
            <span className="text-xs uppercase font-bold tracking-wider">Em Execução</span>
            <RotateCw size={16} className={`text-cyan-400 ${summary.processing > 0 ? 'animate-spin' : ''}`} />
          </div>
          <div className="text-2xl font-black text-cyan-200">{summary.processing}</div>
          <div className="text-[11px] text-cyan-400/80 mt-1">
            {summary.processing > 0 ? 'Varredura ativa agora' : 'Nenhuma ativa no momento'}
          </div>
        </div>

        {/* Total Leads */}
        <div className="bg-gray-900/70 border border-gray-800 rounded-2xl p-4 shadow-sm hover:border-gray-700 transition-colors">
          <div className="flex items-center justify-between text-gray-400 mb-2">
            <span className="text-xs uppercase font-bold tracking-wider">Total de Leads</span>
            <Users size={16} className="text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white">{summary.totalLeads}</div>
          <div className="text-[11px] text-gray-500 mt-1">Captados no Google Places</div>
        </div>

        {/* Prioridade A (Hot) */}
        <div className="bg-amber-950/20 border border-amber-800/40 rounded-2xl p-4 shadow-sm hover:border-amber-700/60 transition-colors">
          <div className="flex items-center justify-between text-amber-400 mb-2">
            <span className="text-xs uppercase font-bold tracking-wider">Prioridade A (Hot)</span>
            <Flame size={16} className="text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-300">{summary.totalPriorityA}</div>
          <div className="text-[11px] text-amber-400/80 mt-1">Alta urgência comercial</div>
        </div>

        {/* Sem Site (Oportunidade LP) */}
        <div className="col-span-2 lg:col-span-1 bg-purple-950/20 border border-purple-800/40 rounded-2xl p-4 shadow-sm hover:border-purple-700/60 transition-colors">
          <div className="flex items-center justify-between text-purple-400 mb-2">
            <span className="text-xs uppercase font-bold tracking-wider">Sem Website</span>
            <Globe size={16} className="text-purple-400" />
          </div>
          <div className="text-2xl font-black text-purple-300">{summary.totalWithoutWeb}</div>
          <div className="text-[11px] text-purple-400/80 mt-1">Alvo direto para Landing Page</div>
        </div>
      </div>

      {/* Barra de Filtros, Busca e Alternância de Visualização */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-gray-900/60 border border-gray-800/80 p-3.5 rounded-2xl backdrop-blur-md">
        {/* Input de Busca */}
        <div className="relative w-full md:w-80">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Buscar por nicho ou cidade..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-950/80 border border-gray-800 rounded-xl text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/40 transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 hover:text-white"
            >
              ✕
            </button>
          )}
        </div>

        {/* Filtros de Status */}
        <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto">
          {[
            { id: 'all', label: 'Todas', count: summary.total },
            { id: 'processing', label: 'Em Execução', count: summary.processing },
            { id: 'completed', label: 'Concluídas', count: summary.completed },
            { id: 'cancelled', label: 'Pausadas', count: campaigns.filter((c) => c.status === 'cancelled' || c.status === 'paused').length },
            { id: 'failed', label: 'Falhas', count: campaigns.filter((c) => c.status === 'failed').length },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setStatusFilter(f.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === f.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'bg-gray-800/60 hover:bg-gray-800 text-gray-400 hover:text-gray-200 border border-transparent'
              }`}
            >
              {f.label} <span className="opacity-60 text-[10px] ml-0.5">({f.count})</span>
            </button>
          ))}
        </div>

        {/* Toggle Cards / Tabela */}
        <div className="flex items-center gap-1 bg-gray-950/80 p-1 rounded-xl border border-gray-800/80 shrink-0">
          <button
            onClick={() => setViewMode('cards')}
            className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all ${
              viewMode === 'cards'
                ? 'bg-gray-800 text-cyan-400 shadow-sm'
                : 'text-gray-500 hover:text-gray-300'
            }`}
            title="Visualização em Cards"
          >
            <LayoutGrid size={16} />
            <span className="hidden sm:inline">Cards</span>
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all ${
              viewMode === 'table'
                ? 'bg-gray-800 text-cyan-400 shadow-sm'
                : 'text-gray-500 hover:text-gray-300'
            }`}
            title="Visualização em Tabela"
          >
            <List size={16} />
            <span className="hidden sm:inline">Tabela</span>
          </button>
        </div>
      </div>

      {/* Conteúdo Principal: Cards ou Tabela */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              className="bg-gray-900/40 border border-gray-800 rounded-2xl p-6 h-64 animate-pulse-soft"
            />
          ))}
        </div>
      ) : filteredCampaigns.length === 0 ? (
        <div className="bg-gray-900/40 border border-gray-800/80 rounded-2xl p-12 text-center">
          <Rocket size={40} className="mx-auto text-gray-600 mb-3" />
          <h3 className="text-lg font-bold text-gray-200">Nenhuma campanha encontrada</h3>
          <p className="text-sm text-gray-400 mt-1 max-w-md mx-auto">
            {searchQuery || statusFilter !== 'all'
              ? 'Nenhuma campanha corresponde aos filtros aplicados. Tente limpar a busca ou mudar o filtro de status.'
              : 'Você ainda não possui campanhas criadas. Clique em "Ativar Nova Campanha" para iniciar a prospecção automática.'}
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-5 inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-bold shadow-lg"
          >
            <Plus size={16} />
            <span>Criar Primeira Campanha</span>
          </button>
        </div>
      ) : viewMode === 'cards' ? (
        /* VISUALIZAÇÃO EM CARDS */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCampaigns.map((camp) => {
            const isProcessing = camp.status === 'processing';
            const totalLeads = camp.total_leads || 0;
            const pA = camp.priority_a || 0;
            const pB = camp.priority_b || 0;
            const pC = camp.priority_c || 0;
            const withoutWeb = camp.without_website || 0;
            const avgDms = camp.avg_dms || 0;
            const avgCos = camp.avg_cos || 0;
            const actLoading = actionLoading[camp.id];

            return (
              <div
                key={camp.id}
                onClick={() => router.push(`/campaigns/${camp.id}`)}
                className={`bg-gray-900/50 hover:bg-gray-900/80 border rounded-2xl p-5 cursor-pointer transition-all duration-300 hover:shadow-xl hover:-translate-y-1 relative group flex flex-col justify-between ${
                  isProcessing
                    ? 'border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.15)] bg-gradient-to-b from-cyan-950/10 to-transparent'
                    : 'border-gray-800 hover:border-gray-700'
                }`}
              >
                {/* Top Card: Nicho, Localização & Status */}
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex-1 min-w-0">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 block mb-0.5">
                        Campanha de Prospecção
                      </span>
                      <h3 className="text-lg font-bold text-gray-100 group-hover:text-cyan-300 transition-colors truncate">
                        {camp.niche}
                      </h3>
                      <p className="text-xs text-gray-400 flex items-center gap-1 mt-1 truncate">
                        <MapPin size={13} className="text-gray-500 shrink-0" />
                        <span>{camp.location}</span>
                      </p>
                    </div>
                    <div className="shrink-0">{getStatusBadge(camp.status)}</div>
                  </div>

                  {/* Barra de Progresso Animada se estiver processando */}
                  {isProcessing && (
                    <div className="my-3 space-y-1.5 bg-cyan-950/30 p-2.5 rounded-xl border border-cyan-500/20">
                      <div className="flex items-center justify-between text-[11px] text-cyan-300 font-semibold">
                        <span className="flex items-center gap-1.5">
                          <RotateCw size={12} className="animate-spin text-cyan-400" />
                          Buscando e qualificando leads...
                        </span>
                        <span>{totalLeads} coletados</span>
                      </div>
                      <div className="w-full bg-gray-900 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-gradient-to-r from-cyan-500 to-purple-500 h-full rounded-full animate-pulse w-full" />
                      </div>
                    </div>
                  )}

                  {/* Bloco de Métricas Chave */}
                  <div className="grid grid-cols-2 gap-2 my-4">
                    {/* Total Leads */}
                    <div className="bg-gray-950/60 p-2.5 rounded-xl border border-gray-800/80">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-gray-500">
                        Total Leads
                      </div>
                      <div className="text-lg font-black text-gray-100 mt-0.5 flex items-baseline gap-1">
                        {totalLeads}
                        <span className="text-[10px] font-normal text-gray-500">captados</span>
                      </div>
                    </div>

                    {/* Prioridade A */}
                    <div className="bg-amber-950/20 p-2.5 rounded-xl border border-amber-800/30">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-amber-400/90 flex items-center gap-1">
                        <Flame size={11} className="text-amber-400" /> Hot (A)
                      </div>
                      <div className="text-lg font-black text-amber-300 mt-0.5 flex items-baseline gap-1">
                        {pA}
                        <span className="text-[10px] font-normal text-amber-400/70">
                          {totalLeads > 0 ? `${Math.round((pA / totalLeads) * 100)}%` : '0%'}
                        </span>
                      </div>
                    </div>

                    {/* Sem Website */}
                    <div className="bg-purple-950/20 p-2.5 rounded-xl border border-purple-800/30">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-purple-400/90 flex items-center gap-1">
                        <Globe size={11} className="text-purple-400" /> Sem Site
                      </div>
                      <div className="text-lg font-black text-purple-300 mt-0.5 flex items-baseline gap-1">
                        {withoutWeb}
                        <span className="text-[10px] font-normal text-purple-400/70">alvos LP</span>
                      </div>
                    </div>

                    {/* Scores DMS / COS */}
                    <div className="bg-gray-950/60 p-2.5 rounded-xl border border-gray-800/80">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-gray-500">
                        Oportunidade (COS)
                      </div>
                      <div className="text-lg font-black text-emerald-400 mt-0.5 flex items-baseline gap-1">
                        {avgCos}
                        <span className="text-[10px] font-normal text-gray-500">/100</span>
                      </div>
                    </div>
                  </div>

                  {/* Barra de Distribuição de Prioridade (A, B, C) */}
                  {totalLeads > 0 && (
                    <div className="mb-4">
                      <div className="flex justify-between text-[10px] text-gray-500 mb-1">
                        <span>Qualificação de Leads:</span>
                        <span>A: {pA} | B: {pB} | C: {pC}</span>
                      </div>
                      <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden flex border border-gray-800">
                        <div
                          style={{ width: `${(pA / totalLeads) * 100}%` }}
                          className="bg-amber-400 h-full"
                          title={`Prioridade A: ${pA} (${Math.round((pA / totalLeads) * 100)}%)`}
                        />
                        <div
                          style={{ width: `${(pB / totalLeads) * 100}%` }}
                          className="bg-blue-400 h-full"
                          title={`Prioridade B: ${pB} (${Math.round((pB / totalLeads) * 100)}%)`}
                        />
                        <div
                          style={{ width: `${(pC / totalLeads) * 100}%` }}
                          className="bg-gray-600 h-full"
                          title={`Prioridade C: ${pC} (${Math.round((pC / totalLeads) * 100)}%)`}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Rodapé do Card: Data & Ações Rápidas */}
                <div className="pt-3 border-t border-gray-800/80 space-y-3">
                  <div className="flex items-center justify-between text-[11px] text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock size={12} />
                      {formatDate(camp.created_at)}
                    </span>
                    {camp.diagnostics_count > 0 && (
                      <span className="text-cyan-400/90 font-semibold">
                        {camp.diagnostics_count} diagnósticos IA
                      </span>
                    )}
                  </div>

                  {/* Botões de Ação na Base */}
                  <div className="flex items-center justify-between gap-2">
                    {/* Botão de Ativação / Pausa */}
                    {isProcessing ? (
                      <button
                        onClick={(e) => handleCancelCampaign(camp.id, e)}
                        disabled={actLoading === 'cancelling'}
                        className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-xl text-xs font-bold transition-all"
                        title="Pausar execução da campanha"
                      >
                        <Pause size={14} />
                        <span>{actLoading === 'cancelling' ? 'Pausando...' : 'Pausar'}</span>
                      </button>
                    ) : (
                      <button
                        onClick={(e) => handleActivateCampaign(camp.id, e)}
                        disabled={actLoading === 'activating'}
                        className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 hover:border-cyan-500/60 rounded-xl text-xs font-bold transition-all"
                        title="Ativar/Reexecutar busca e triagem de leads"
                      >
                        {actLoading === 'activating' ? (
                          <RotateCw size={14} className="animate-spin text-cyan-400" />
                        ) : (
                          <Play size={14} className="text-cyan-400 fill-cyan-400" />
                        )}
                        <span>{actLoading === 'activating' ? 'Ativando...' : '⚡ Ativar Radar'}</span>
                      </button>
                    )}

                    {/* Botão Ver Leads */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/campaigns/${camp.id}`);
                      }}
                      className="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 rounded-xl text-xs font-bold transition-all flex items-center gap-1"
                      title="Ver leads da campanha"
                    >
                      <span>Leads</span>
                      <ExternalLink size={12} className="text-gray-400" />
                    </button>

                    {/* Botão Exportar CSV */}
                    <button
                      onClick={(e) => handleExportCSV(camp.id, camp.niche, e)}
                      disabled={actLoading === 'exporting'}
                      className="p-2 bg-gray-800/80 hover:bg-gray-700 text-gray-400 hover:text-white border border-gray-700/80 rounded-xl text-xs transition-all"
                      title="Exportar Leads (CSV)"
                    >
                      <Download size={14} />
                    </button>

                    {/* Botão Excluir */}
                    <button
                      onClick={(e) => handleDeleteCampaign(camp.id, camp.niche, e)}
                      disabled={actLoading === 'deleting'}
                      className="p-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 hover:border-rose-500/40 rounded-xl text-xs transition-all"
                      title="Excluir Campanha"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* VISUALIZAÇÃO EM TABELA DETALHADA */
        <div className="bg-gray-900/60 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-800 bg-gray-950/60 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Nicho / Segmento</th>
                  <th className="py-3.5 px-4">Localização</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-center">Total Leads</th>
                  <th className="py-3.5 px-4 text-center">Prioridade A</th>
                  <th className="py-3.5 px-4 text-center">Sem Site</th>
                  <th className="py-3.5 px-4 text-center">Média COS</th>
                  <th className="py-3.5 px-4">Data</th>
                  <th className="py-3.5 px-4 text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 text-xs">
                {filteredCampaigns.map((camp) => {
                  const isProcessing = camp.status === 'processing';
                  const actLoading = actionLoading[camp.id];

                  return (
                    <tr
                      key={camp.id}
                      onClick={() => router.push(`/campaigns/${camp.id}`)}
                      className="hover:bg-gray-800/40 cursor-pointer transition-colors group"
                    >
                      <td className="py-3.5 px-4 font-bold text-gray-200 group-hover:text-cyan-400 transition-colors">
                        {camp.niche}
                      </td>
                      <td className="py-3.5 px-4 text-gray-400">{camp.location}</td>
                      <td className="py-3.5 px-4">{getStatusBadge(camp.status)}</td>
                      <td className="py-3.5 px-4 text-center font-extrabold text-white">
                        {camp.total_leads ?? 0}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="inline-flex items-center gap-1 font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                          <Flame size={11} /> {camp.priority_a ?? 0}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="inline-flex items-center gap-1 font-bold text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded-full border border-purple-500/20">
                          <Globe size={11} /> {camp.without_website ?? 0}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center font-bold text-emerald-400">
                        {camp.avg_cos ? `${camp.avg_cos}/100` : '—'}
                      </td>
                      <td className="py-3.5 px-4 text-gray-400 text-[11px]">
                        {formatDate(camp.created_at)}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                          {isProcessing ? (
                            <button
                              onClick={(e) => handleCancelCampaign(camp.id, e)}
                              disabled={actLoading === 'cancelling'}
                              className="p-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-xs"
                              title="Pausar"
                            >
                              <Pause size={14} />
                            </button>
                          ) : (
                            <button
                              onClick={(e) => handleActivateCampaign(camp.id, e)}
                              disabled={actLoading === 'activating'}
                              className="p-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-lg text-xs"
                              title="Ativar / Reexecutar"
                            >
                              {actLoading === 'activating' ? (
                                <RotateCw size={14} className="animate-spin text-cyan-400" />
                              ) : (
                                <Play size={14} className="text-cyan-400 fill-cyan-400" />
                              )}
                            </button>
                          )}

                          <button
                            onClick={() => router.push(`/campaigns/${camp.id}`)}
                            className="p-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 rounded-lg text-xs"
                            title="Abrir campanha"
                          >
                            <ExternalLink size={14} />
                          </button>

                          <button
                            onClick={(e) => handleExportCSV(camp.id, camp.niche, e)}
                            className="p-1.5 bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white border border-gray-700 rounded-lg text-xs"
                            title="Exportar CSV"
                          >
                            <Download size={14} />
                          </button>

                          <button
                            onClick={(e) => handleDeleteCampaign(camp.id, camp.niche, e)}
                            className="p-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 rounded-lg text-xs"
                            title="Excluir"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal de Criação / Ativação de Campanha */}
      <NewCampaignModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={handleCampaignSuccess}
      />
    </div>
  );
}
