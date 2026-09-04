'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import LeadTable from '@/components/leads/LeadTable';
import LeadFilters from '@/components/leads/LeadFilters';
import { STATUS_CONFIG, PRIORITY_CONFIG } from '@/lib/constants';

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const campaignId = params.id;

  const [campaign, setCampaign] = useState(null);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchValue, setSearchValue] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [exporting, setExporting] = useState(false);

  const loadCampaign = useCallback(async () => {
    try {
      const data = await fetchApi(`/campaigns/${campaignId}`);
      const campaignData = data.data || data;
      setCampaign(campaignData);
      return campaignData;
    } catch (err) {
      console.error('Erro ao carregar campanha:', err);
      return null;
    }
  }, [campaignId]);

  const loadLeads = useCallback(async () => {
    try {
      const queryParams = new URLSearchParams();
      if (searchValue) queryParams.set('search', searchValue);
      if (priorityFilter) queryParams.set('priority', priorityFilter);
      const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
      const data = await fetchApi(`/campaigns/${campaignId}/leads${query}`);
      const leadsList = data.data || data.leads || (Array.isArray(data) ? data : []);
      setLeads(leadsList);
    } catch (err) {
      console.error('Erro ao carregar leads:', err);
    }
  }, [campaignId, searchValue, priorityFilter]);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      const campaignData = await loadCampaign();
      await loadLeads();
      setLoading(false);

      // Polling if processing
      if (campaignData?.status === 'processing') {
        const interval = setInterval(async () => {
          const updated = await loadCampaign();
          if (updated?.status !== 'processing') {
            clearInterval(interval);
            await loadLeads();
          }
        }, 3000);
        return () => clearInterval(interval);
      }
    };
    init();
  }, [loadCampaign, loadLeads]);

  useEffect(() => {
    if (!loading) {
      loadLeads();
    }
  }, [searchValue, priorityFilter, loadLeads, loading]);

  const handleExportCSV = async () => {
    try {
      setExporting(true);
      const csvData = await fetchApi(`/campaigns/${campaignId}/leads/export`);
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `leads_${campaign?.niche || 'campanha'}_${campaignId}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erro ao exportar:', err);
    } finally {
      setExporting(false);
    }
  };

  const handleViewDiagnostic = (leadId) => {
    router.push(`/leads/${leadId}`);
  };

  const priorityCounts = leads.reduce(
    (acc, lead) => {
      if (lead.priority) acc[lead.priority] = (acc[lead.priority] || 0) + 1;
      return acc;
    },
    {}
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-800/60 rounded-xl w-64 animate-pulse-soft border border-gray-700/30" />
        <div className="h-4 bg-gray-800/40 rounded-lg w-96 animate-pulse-soft border border-gray-700/30" />
        <div className="bg-gray-900/60 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 h-96 animate-pulse-soft" />
      </div>
    );
  }

  const statusConf = STATUS_CONFIG[campaign?.status] || {};
  const getStatusVariant = (status) => {
    const map = { processing: 'info', completed: 'success', failed: 'danger' };
    return map[status] || 'default';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back button */}
      <button
        onClick={() => router.push('/')}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-cyan-400 font-medium transition-colors"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Voltar ao Dashboard
      </button>

      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-100">
              {campaign?.niche} — {campaign?.location}
            </h1>
            <Badge variant={getStatusVariant(campaign?.status)} size="md">
              {statusConf.icon} {statusConf.label || campaign?.status}
            </Badge>
          </div>
          <p className="text-sm text-gray-400 mt-1">
            {leads.length} leads encontrados
          </p>
        </div>

        <Button
          variant="secondary"
          onClick={handleExportCSV}
          loading={exporting}
          disabled={!leads.length}
        >
          📥 Exportar CSV
        </Button>
      </div>

      {/* Processing message */}
      {campaign?.status === 'processing' && (
        <Card className="border-cyan-500/30 bg-cyan-500/10">
          <div className="flex items-center gap-3">
            <div className="animate-spin w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full" />
            <div>
              <p className="text-sm font-semibold text-cyan-300">Campanha em processamento...</p>
              <p className="text-xs text-cyan-200/70 mt-0.5">Os leads estão sendo coletados e analisados. Atualizando automaticamente.</p>
            </div>
          </div>
        </Card>
      )}

      {/* Error message */}
      {campaign?.status === 'failed' && (
        <Card className="border-rose-500/30 bg-rose-500/10">
          <div className="flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div>
              <p className="text-sm font-semibold text-rose-400">Falha ao processar campanha</p>
              <p className="text-xs text-rose-300/80 mt-1">
                Não foi possível obter os resultados desta campanha. Detalhes do problema:
              </p>
              <p className="text-xs font-mono bg-rose-950/40 border border-rose-500/20 rounded p-2.5 text-rose-300 mt-2 whitespace-pre-wrap">
                {campaign?.error_message || 'Erro desconhecido na execução das APIs de consulta.'}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Priority counters */}
      <div className="flex flex-wrap gap-3">
        {Object.entries(PRIORITY_CONFIG).map(([key, config]) => (
          <div key={key} className={`flex items-center gap-2 px-4 py-2 rounded-xl backdrop-blur-md shadow-sm font-semibold ${config.bgClass}`}>
            <span className={`w-2.5 h-2.5 rounded-full ${config.dotClass}`} />
            <span className="text-sm">{config.label}: {priorityCounts[key] || 0}</span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <LeadFilters
        searchValue={searchValue}
        onSearchChange={setSearchValue}
        priorityFilter={priorityFilter}
        onFilterChange={setPriorityFilter}
      />

      {/* Leads table */}
      <Card padding="p-0">
        <LeadTable leads={leads} onViewDiagnostic={handleViewDiagnostic} />
      </Card>
    </div>
  );
}
