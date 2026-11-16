'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import StatCard from '@/components/ui/StatCard';
import PriorityChart from '@/components/dashboard/PriorityChart';
import CampaignTable from '@/components/dashboard/CampaignTable';
import NewCampaignModal from '@/components/campaigns/NewCampaignModal';
import { Users, BarChart3, ClipboardCheck, Rocket } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState({ totalLeads: 0, avgDms: 0, activeCampaigns: 0, totalDiagnostics: 0 });
  const [priorityData, setPriorityData] = useState([]);
  const [barData, setBarData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      
      // 1. Busca campanhas para a tabela e o gráfico de barras
      const campaignsData = await fetchApi('/campaigns');
      const campaignsList = campaignsData.data || campaignsData.campaigns || (Array.isArray(campaignsData) ? campaignsData : []);
      setCampaigns(campaignsList);

      // 2. Busca estatísticas globais consolidadas do dashboard
      const dashboardRes = await fetchApi('/dashboard/stats');
      const dashboardData = dashboardRes.data || {};

      setStats({
        totalLeads: dashboardData.totalLeads || 0,
        avgDms: dashboardData.avgDms || 0,
        activeCampaigns: dashboardData.activeCampaigns || 0,
        totalDiagnostics: dashboardData.totalDiagnostics || 0,
      });

      if (dashboardData.priorityDistribution) {
        setPriorityData(dashboardData.priorityDistribution);
      }

      // 3. Monta dados para o gráfico de barras de leads por campanha
      const barChartData = campaignsList
        .filter((c) => c.status === 'completed')
        .slice(0, 5) // Top 5
        .map((c) => ({
          name: `${c.niche}`.substring(0, 15),
          leads: c.total_leads || 0,
        }));
      setBarData(barChartData);

    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Polling automático suave enquanto houver campanhas em execução
  const hasProcessing = campaigns.some((c) => c.status === 'processing');
  useEffect(() => {
    if (!hasProcessing) return;
    const interval = setInterval(() => {
      loadData();
    }, 4000);
    return () => clearInterval(interval);
  }, [hasProcessing, loadData]);

  const handleCampaignSuccess = (result) => {
    setShowModal(false);
    loadData();
    const id = result?.data?.id || result?.id;
    if (id) {
      router.push(`/campaigns/${id}`);
    }
  };

  // Loading skeleton
  if (loading) {
    return (
      <div className="space-y-8">
        <div>
          <div className="h-8 bg-gray-800/60 rounded-xl w-48 animate-pulse-soft border border-gray-700/30" />
          <div className="h-4 bg-gray-800/40 rounded-lg w-64 mt-2 animate-pulse-soft border border-gray-700/30" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-gray-900/60 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 animate-pulse-soft">
              <div className="h-4 bg-gray-800/80 rounded w-24 mb-3" />
              <div className="h-8 bg-gray-800/60 rounded w-16" />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <div key={i} className="bg-gray-900/60 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 h-80 animate-pulse-soft" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Header Premium */}
      <div className="relative">
        <div className="absolute -left-4 top-1 w-1 h-12 bg-gradient-to-b from-cyan-400 to-purple-500 rounded-full" />
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-100 to-cyan-500 tracking-tight">
          Painel de Controle
        </h1>
        <p className="text-sm text-gray-400 mt-2 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Sistema operacional online
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Total de Leads"
          value={stats.totalLeads}
          icon={<Users size={24} strokeWidth={1.5} />}
          subtitle="Leads coletados no total"
        />
        <StatCard
          title="Média DMS"
          value={stats.avgDms}
          icon={<BarChart3 size={24} strokeWidth={1.5} />}
          subtitle="Índice de Maturidade"
        />
        <StatCard
          title="Diagnósticos IA"
          value={stats.totalDiagnostics}
          icon={<ClipboardCheck size={24} strokeWidth={1.5} />}
          subtitle="Relatórios gerados"
        />
        <StatCard
          title="Campanhas Ativas"
          value={stats.activeCampaigns}
          icon={<Rocket size={24} strokeWidth={1.5} />}
          subtitle="Processamento em andamento"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Distribuição por Prioridade</h3>
          {priorityData.length > 0 ? (
            <PriorityChart data={priorityData} />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 text-sm">
              Sem dados disponíveis
            </div>
          )}
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Leads por Campanha (Top 5)</h3>
          {barData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={barData} margin={{ top: 20, right: 20, left: -20, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={1}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: '#9CA3AF' }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  tickLine={false}
                  dy={10}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#6B7280' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                  contentStyle={{
                    backgroundColor: 'rgba(17, 24, 39, 0.8)',
                    backdropFilter: 'blur(12px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '16px',
                    boxShadow: '0 10px 30px -5px rgba(0,0,0,0.5)',
                    fontSize: '13px',
                    color: '#F3F4F6'
                  }}
                  itemStyle={{ color: '#06B6D4', fontWeight: 'bold' }}
                  formatter={(value) => [`${value} leads`, 'Captados']}
                />
                <Bar dataKey="leads" fill="url(#colorLeads)" radius={[6, 6, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 text-sm">
              Sem dados disponíveis
            </div>
          )}
        </Card>
      </div>

      {/* Campaign Section */}
      <Card>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-gray-100">Campanhas de Prospecção</h3>
              {hasProcessing && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                  Automação Ativa
                </span>
              )}
            </div>
            <p className="text-xs text-gray-400 mt-0.5">Monitore o radar de leads e ative novas automações sob medida</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => router.push('/campaigns')}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold text-cyan-400 hover:text-cyan-300 bg-cyan-950/40 hover:bg-cyan-900/60 border border-cyan-800/50 transition-all flex items-center gap-1"
            >
              <span>Gerenciar Campanhas ({campaigns.length})</span>
              <span>→</span>
            </button>
            <button
              onClick={() => setShowModal(true)}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-lg text-xs font-bold shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all"
            >
              <Rocket size={14} />
              <span>⚡ Ativar Campanha</span>
            </button>
          </div>
        </div>
        <CampaignTable campaigns={campaigns} onRefresh={loadData} />
      </Card>

      {/* FAB */}
      <button
        onClick={() => setShowModal(true)}
        className="fixed bottom-24 md:bottom-8 right-4 md:right-8 w-14 h-14 md:w-16 md:h-16 bg-gradient-to-tr from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white rounded-full shadow-[0_0_30px_rgba(6,182,212,0.5)] hover:shadow-[0_0_40px_rgba(139,92,246,0.6)] hover:-translate-y-1 transition-all duration-300 flex items-center justify-center z-40 border border-white/20 group"
        title="Nova Campanha"
      >
        <Rocket className="text-white group-hover:scale-110 transition-transform duration-300" size={28} strokeWidth={1.5} />
      </button>

      {/* New Campaign Modal */}
      <NewCampaignModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={handleCampaignSuccess}
      />
    </div>
  );
}
