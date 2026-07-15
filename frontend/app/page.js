'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import StatCard from '@/components/ui/StatCard';
import PriorityChart from '@/components/dashboard/PriorityChart';
import CampaignTable from '@/components/dashboard/CampaignTable';
import NewCampaignModal from '@/components/campaigns/NewCampaignModal';

export default function DashboardPage() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState({ totalLeads: 0, avgDms: 0, activeCampaigns: 0, totalDiagnostics: 0 });
  const [apiUsage, setApiUsage] = useState({
    apify: { used: 0, limit: 50, unit: 'pesquisas' },
    gemini: { used: 0, limit: 1500, unit: 'requisições' },
    pagespeed: { used: 0, limit: 25000, unit: 'auditorias' }
  });
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

      // 2. Busca estatísticas globais consolidadas do dashboard e consumo de APIs
      const dashboardRes = await fetchApi('/dashboard/stats');
      const dashboardData = dashboardRes.data || {};

      setStats({
        totalLeads: dashboardData.totalLeads || 0,
        avgDms: dashboardData.avgDms || 0,
        activeCampaigns: dashboardData.activeCampaigns || 0,
        totalDiagnostics: dashboardData.totalDiagnostics || 0,
      });

      if (dashboardData.apiUsage) {
        setApiUsage(dashboardData.apiUsage);
      }

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
          <div className="h-8 bg-gray-200 rounded w-48 animate-pulse-soft" />
          <div className="h-4 bg-gray-200 rounded w-64 mt-2 animate-pulse-soft" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse-soft">
              <div className="h-4 bg-gray-200 rounded w-24 mb-3" />
              <div className="h-8 bg-gray-200 rounded w-16" />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-80 animate-pulse-soft" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Visão geral da prospecção comercial</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Total de Leads"
          value={stats.totalLeads}
          icon="👥"
          subtitle="Leads coletados"
        />
        <StatCard
          title="Média DMS"
          value={stats.avgDms}
          icon="📊"
          subtitle="Maturidade Digital"
        />
        <StatCard
          title="Diagnósticos Feitos"
          value={stats.totalDiagnostics}
          icon="📋"
          subtitle="Gerados com IA"
        />
        <StatCard
          title="Campanhas Ativas"
          value={stats.activeCampaigns}
          icon="🚀"
          subtitle="Em processamento"
        />
      </div>

      {/* API Usage & Quotas (Limites Gratuitos) */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-1.5">
          <span>⚡</span> Consumo de APIs (Controle do Limite Gratuito)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Apify */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-gray-600">
              <span>Apify (Scraper do Maps)</span>
              <span className="font-mono text-gray-500">{apiUsage.apify.used} / {apiUsage.apify.limit} {apiUsage.apify.unit}</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-cyan-500 h-2 rounded-full transition-all duration-700" 
                style={{ width: `${Math.min(100, (apiUsage.apify.used / apiUsage.apify.limit) * 100)}%` }}
              />
            </div>
            <p className="text-[10px] text-gray-400 font-medium">
              Sobram <span className="text-cyan-600 font-bold">{Math.max(0, apiUsage.apify.limit - apiUsage.apify.used)}</span> {apiUsage.apify.unit} de prospecção este mês.
            </p>
          </div>

          {/* Gemini */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-gray-600">
              <span>Gemini 2.5 Flash (Diagnósticos)</span>
              <span className="font-mono text-gray-500">{apiUsage.gemini.used} / {apiUsage.gemini.limit} {apiUsage.gemini.unit}</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-emerald-500 h-2 rounded-full transition-all duration-700" 
                style={{ width: `${Math.min(100, (apiUsage.gemini.used / apiUsage.gemini.limit) * 100)}%` }}
              />
            </div>
            <p className="text-[10px] text-gray-400 font-medium">
              Sobram <span className="text-emerald-600 font-bold">{Math.max(0, apiUsage.gemini.limit - apiUsage.gemini.used)}</span> {apiUsage.gemini.unit} para geração de relatórios hoje.
            </p>
          </div>

          {/* PageSpeed */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-gray-600">
              <span>Google PageSpeed Insights</span>
              <span className="font-mono text-gray-500">{apiUsage.pagespeed.used} / {apiUsage.pagespeed.limit} {apiUsage.pagespeed.unit}</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-indigo-500 h-2 rounded-full transition-all duration-700" 
                style={{ width: `${Math.min(100, (apiUsage.pagespeed.used / apiUsage.pagespeed.limit) * 100)}%` }}
              />
            </div>
            <p className="text-[10px] text-gray-400 font-medium">
              Sobram <span className="text-indigo-600 font-bold">{Math.max(0, apiUsage.pagespeed.limit - apiUsage.pagespeed.used)}</span> {apiUsage.pagespeed.unit} de auditorias hoje.
            </p>
          </div>
        </div>
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Distribuição por Prioridade</h3>
          {priorityData.length > 0 ? (
            <PriorityChart data={priorityData} />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
              Sem dados disponíveis de leads
            </div>
          )}
        </Card>

        <Card>
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Leads por Campanha (Top 5)</h3>
          {barData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={barData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  axisLine={{ stroke: '#E5E7EB' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
                    fontSize: '13px',
                  }}
                  formatter={(value) => [`${value} leads`, 'Total']}
                />
                <Bar dataKey="leads" fill="#06B6D4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
              Sem dados disponíveis
            </div>
          )}
        </Card>
      </div>

      {/* Campaign Table */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Campanhas Recentes</h3>
        <CampaignTable campaigns={campaigns} />
      </Card>

      {/* FAB */}
      <button
        onClick={() => setShowModal(true)}
        className="fixed bottom-8 right-8 w-14 h-14 bg-cyan-500 hover:bg-cyan-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center text-2xl font-light z-40"
        title="Nova Campanha"
      >
        +
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
