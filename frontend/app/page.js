'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  BadgeCheck,
  CircleAlert,
  CircleCheck,
  Activity,
  FolderKanban,
  Handshake,
  LoaderCircle,
  PauseCircle,
  Percent,
  Phone,
  Users,
  Wallet,
} from 'lucide-react';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import StatCard from '@/components/ui/StatCard';

const EMPTY_CRM_STATS = {
  contactedCustomers: 0,
  interestedCustomers: 0,
  closedCustomers: 0,
  paidCustomers: 0,
  conversionRate: 0,
};

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState(EMPTY_CRM_STATS);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatedAt, setUpdatedAt] = useState(null);

  const loadDashboard = useCallback(async () => {
    const [dashboardResult, campaignsResult] = await Promise.allSettled([
      fetchApi('/dashboard/stats'),
      fetchApi('/campaigns'),
    ]);
    const errors = [];

    if (dashboardResult.status === 'fulfilled' && dashboardResult.value.data?.crmStats) {
      setStats(dashboardResult.value.data.crmStats);
    } else {
      const message = dashboardResult.status === 'rejected'
        ? dashboardResult.reason?.message
        : 'A API não retornou os indicadores do CRM.';
      errors.push(message || 'Não foi possível carregar os indicadores do CRM.');
      console.error('Erro ao carregar indicadores do CRM:', dashboardResult.status === 'rejected'
        ? dashboardResult.reason
        : message);
    }

    if (campaignsResult.status === 'fulfilled') {
      const campaignList = campaignsResult.value.data
        || campaignsResult.value.campaigns
        || (Array.isArray(campaignsResult.value) ? campaignsResult.value : null);
      if (Array.isArray(campaignList)) {
        setCampaigns(campaignList);
      } else {
        errors.push('A API retornou uma lista de campanhas inválida.');
      }
    } else {
      errors.push(campaignsResult.reason?.message || 'Não foi possível carregar as campanhas.');
      console.error('Erro ao carregar campanhas:', campaignsResult.reason);
    }

    setError(errors.join(' '));
    if (!errors.length) setUpdatedAt(new Date());
    setLoading(false);
  }, []);

  useEffect(() => {
    loadDashboard();
    const intervalId = setInterval(loadDashboard, 15000);
    window.addEventListener('focus', loadDashboard);

    return () => {
      clearInterval(intervalId);
      window.removeEventListener('focus', loadDashboard);
    };
  }, [loadDashboard]);

  const conversionRate = Number(stats.conversionRate) || 0;
  const formattedConversionRate = `${conversionRate.toLocaleString('pt-BR', {
    maximumFractionDigits: 1,
  })}%`;
  const campaignSummary = campaigns.reduce((summary, campaign) => ({
    total: summary.total + 1,
    processing: summary.processing + (campaign.status === 'processing' ? 1 : 0),
    completed: summary.completed + (campaign.status === 'completed' ? 1 : 0),
    paused: summary.paused + (['cancelled', 'paused'].includes(campaign.status) ? 1 : 0),
    failed: summary.failed + (campaign.status === 'failed' ? 1 : 0),
    leads: summary.leads + (Number(campaign.total_leads) || 0),
  }), { total: 0, processing: 0, completed: 0, paused: 0, failed: 0, leads: 0 });
  const recentCampaigns = campaigns.slice(0, 5);
  const formatDate = (dateString) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('pt-BR');
  };
  const campaignStatus = {
    processing: { label: 'Processando', variant: 'info' },
    completed: { label: 'Concluída', variant: 'success' },
    failed: { label: 'Falhou', variant: 'danger' },
    cancelled: { label: 'Pausada', variant: 'warning' },
    paused: { label: 'Pausada', variant: 'warning' },
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div>
          <div className="h-8 w-56 animate-pulse-soft rounded-xl border border-gray-700/30 bg-gray-800/60" />
          <div className="mt-2 h-4 w-80 animate-pulse-soft rounded-lg border border-gray-700/30 bg-gray-800/40" />
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-5">
          {[1, 2, 3, 4, 5].map((item) => (
            <div key={item} className="h-32 animate-pulse-soft rounded-2xl border border-gray-700/50 bg-gray-900/60" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-2 font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-200/65">
            <Activity size={13} />
            Central de operações
            <span className="ml-1 inline-flex items-center gap-1.5 rounded-full border border-cyan-300/10 bg-cyan-400/[0.045] px-2 py-1 text-[9px] tracking-[0.12em] text-cyan-100/70">
              SYNC · 15S
            </span>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-gray-100 sm:text-4xl">Visão geral</h1>
          <p className="mt-2 max-w-2xl text-sm text-gray-400">
            Acompanhe o CRM e o desempenho das campanhas em um só lugar.
          </p>
        </div>
        <div className="flex items-center gap-4">
          {updatedAt && (
            <span className="hidden rounded-lg border border-white/[0.07] bg-white/[0.025] px-3 py-2 font-mono text-[10px] text-gray-500 sm:inline-flex">
              Atualizado às {updatedAt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
          <button
            type="button"
            onClick={() => router.push('/crm')}
            className="inline-flex items-center gap-2 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-sm font-semibold text-cyan-300 transition-colors hover:bg-cyan-500/20"
          >
            Abrir CRM <ArrowRight size={16} />
          </button>
          <button
            type="button"
            onClick={() => router.push('/campaigns')}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-800/70 px-4 py-2 text-sm font-semibold text-gray-200 transition-colors hover:bg-gray-700"
          >
            Campanhas <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {error && (
        <Card className="border-rose-500/30 bg-rose-500/10">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p role="alert" className="text-sm text-rose-300">{error}</p>
            <button
              type="button"
              onClick={loadDashboard}
              className="text-sm font-semibold text-rose-200 underline underline-offset-2"
            >
              Tentar novamente
            </button>
          </div>
        </Card>
      )}

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-gray-100">Visão do CRM</h2>
          <p className="mt-1 text-xs text-gray-400">Clientes por etapa atual da esteira comercial.</p>
        </div>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5">
        <StatCard
          title="Contatados"
          value={stats.contactedCustomers}
          icon={<Phone size={23} strokeWidth={1.7} />}
          subtitle="Etapa atual: Contatado"
        />
        <StatCard
          title="Interessados"
          value={stats.interestedCustomers}
          icon={<Handshake size={23} strokeWidth={1.7} />}
          subtitle="Etapa atual: Interessado"
        />
        <StatCard
          title="Fechados"
          value={stats.closedCustomers}
          icon={<BadgeCheck size={23} strokeWidth={1.7} />}
          subtitle="Etapa atual: Fechado"
        />
        <StatCard
          title="Pagos"
          value={stats.paidCustomers}
          icon={<Wallet size={23} strokeWidth={1.7} />}
          subtitle="Etapa atual: Pago"
        />
        <StatCard
          title="Taxa de conversão"
          value={formattedConversionRate}
          icon={<Percent size={23} strokeWidth={1.7} />}
          subtitle="Fechados ÷ contatados"
        />
        </div>
      </section>

      <Card>
        <div className="flex items-start gap-3">
          <div className="mt-0.5 rounded-lg border border-cyan-500/20 bg-cyan-500/10 p-2 text-cyan-300">
            <Handshake size={18} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-gray-200">Indicadores ligados à esteira do CRM</h2>
            <p className="mt-1 text-xs leading-relaxed text-gray-400">
              Os números consideram somente leads adicionados ao CRM e acompanham o status atual de cada cliente.
              Ao mover um cliente entre as etapas, os indicadores são atualizados automaticamente.
            </p>
          </div>
        </div>
      </Card>

      <section className="space-y-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-gray-100">Visão das campanhas</h2>
            <p className="mt-1 text-xs text-gray-400">Acompanhe a coleta de leads e o andamento das campanhas.</p>
          </div>
          <button
            type="button"
            onClick={() => router.push('/campaigns')}
            className="text-sm font-semibold text-cyan-400 transition-colors hover:text-cyan-300"
          >
            Gerenciar campanhas <ArrowRight size={14} className="ml-1 inline" />
          </button>
        </div>

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5">
          <StatCard
            title="Campanhas"
            value={campaignSummary.total}
            icon={<FolderKanban size={22} strokeWidth={1.7} />}
            subtitle="Total cadastradas"
          />
          <StatCard
            title="Em andamento"
            value={campaignSummary.processing}
            icon={<LoaderCircle size={22} strokeWidth={1.7} />}
            subtitle="Coleta em processamento"
          />
          <StatCard
            title="Concluídas"
            value={campaignSummary.completed}
            icon={<CircleCheck size={22} strokeWidth={1.7} />}
            subtitle="Coleta finalizada"
          />
          <StatCard
            title="Atenção"
            value={campaignSummary.paused + campaignSummary.failed}
            icon={campaignSummary.failed
              ? <CircleAlert size={22} strokeWidth={1.7} />
              : <PauseCircle size={22} strokeWidth={1.7} />}
            subtitle={`${campaignSummary.paused} pausadas · ${campaignSummary.failed} com falha`}
          />
          <StatCard
            title="Leads"
            value={campaignSummary.leads}
            icon={<Users size={22} strokeWidth={1.7} />}
            subtitle="Encontrados nas campanhas"
          />
        </div>

        <Card padding="p-0">
          <div className="flex items-center justify-between border-b border-gray-700/50 p-4">
            <h3 className="text-sm font-semibold text-gray-200">Campanhas recentes</h3>
            <span className="text-xs text-gray-500">Últimas {recentCampaigns.length}</span>
          </div>
          {recentCampaigns.length ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left">
                <thead>
                  <tr className="border-b border-gray-800 text-[11px] font-semibold uppercase tracking-wide text-gray-500">
                    <th className="px-4 py-3">Nicho</th>
                    <th className="px-4 py-3">Localização</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 text-center">Leads</th>
                    <th className="px-4 py-3">Criada em</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody>
                  {recentCampaigns.map((campaign) => {
                    const status = campaignStatus[campaign.status] || {
                      label: campaign.status || 'Desconhecido',
                      variant: 'default',
                    };
                    return (
                      <tr key={campaign.id} className="border-b border-gray-800/70 text-sm last:border-0">
                        <td className="px-4 py-3 font-medium text-gray-100">{campaign.niche || '—'}</td>
                        <td className="px-4 py-3 text-gray-400">{campaign.location || '—'}</td>
                        <td className="px-4 py-3">
                          <Badge variant={status.variant}>{status.label}</Badge>
                        </td>
                        <td className="px-4 py-3 text-center font-semibold text-gray-200">
                          {Number(campaign.total_leads) || 0}
                        </td>
                        <td className="px-4 py-3 text-gray-500">{formatDate(campaign.created_at)}</td>
                        <td className="px-4 py-3 text-right">
                          <button
                            type="button"
                            onClick={() => router.push(`/campaigns/${campaign.id}`)}
                            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300"
                          >
                            Abrir
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-sm text-gray-400">Nenhuma campanha encontrada.</p>
              <button
                type="button"
                onClick={() => router.push('/campaigns')}
                className="mt-3 text-sm font-semibold text-cyan-400 hover:text-cyan-300"
              >
                Ver campanhas
              </button>
            </div>
          )}
        </Card>
      </section>
    </div>
  );
}
