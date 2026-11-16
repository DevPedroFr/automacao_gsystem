'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import LeadTable from '@/components/leads/LeadTable';
import { STATUS_CONFIG } from '@/lib/constants';
import { CircleStop, Play, RotateCw, ChevronLeft } from 'lucide-react';

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const campaignId = params.id;

  const [campaign, setCampaign] = useState(null);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [activating, setActivating] = useState(false);
  const [addingLeadId, setAddingLeadId] = useState(null);

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
      const data = await fetchApi(`/campaigns/${campaignId}/leads?sort_by=name&sort_order=ASC`);
      const leadsList = data.data || data.leads || (Array.isArray(data) ? data : []);
      setLeads(leadsList);
    } catch (err) {
      console.error('Erro ao carregar leads:', err);
    }
  }, [campaignId]);

  useEffect(() => {
    let interval;
    let disposed = false;

    const init = async () => {
      setLoading(true);
      const campaignData = await loadCampaign();
      await loadLeads();
      setLoading(false);

      // Poll campaign and leads while the worker is still processing.
      if (!disposed && campaignData?.status === 'processing') {
        interval = setInterval(async () => {
          const updated = await loadCampaign();
          await loadLeads();
          if (updated?.status !== 'processing') {
            clearInterval(interval);
          }
        }, 3000);
      }
    };
    init();

    return () => {
      disposed = true;
      if (interval) clearInterval(interval);
    };
  }, [loadCampaign, loadLeads]);

  const handleActivateCampaign = async () => {
    try {
      setActivating(true);
      const result = await fetchApi(`/campaigns/${campaignId}/activate`, { method: 'POST' });
      setCampaign(result.data || result);
      await loadLeads();
    } catch (err) {
      console.error('Erro ao ativar campanha:', err);
      window.alert(err.message || 'Não foi possível ativar a campanha.');
    } finally {
      setActivating(false);
    }
  };

  const handleCancelCampaign = async () => {
    if (!window.confirm('Deseja parar esta campanha? Os leads já encontrados serão mantidos.')) return;
    try {
      setCancelling(true);
      const result = await fetchApi(`/campaigns/${campaignId}/cancel`, { method: 'POST' });
      setCampaign(result.data || result);
    } catch (err) {
      console.error('Erro ao parar campanha:', err);
      window.alert(err.message || 'Não foi possível parar a campanha.');
    } finally {
      setCancelling(false);
    }
  };

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

  const handleGetLeadData = (leadId) => {
    router.push(`/leads/${leadId}`);
  };

  const handleAddLeadToCrm = async (leadId) => {
    try {
      setAddingLeadId(leadId);
      await fetchApi(`/leads/${leadId}/crm`, { method: 'POST' });
      setLeads((current) =>
        current.map((lead) => lead.id === leadId ? { ...lead, in_crm: true } : lead)
      );
    } catch (err) {
      console.error('Erro ao adicionar lead ao CRM:', err);
      window.alert(err.message || 'Não foi possível adicionar o lead ao CRM.');
    } finally {
      setAddingLeadId(null);
    }
  };

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
    const map = { processing: 'info', completed: 'success', failed: 'danger', cancelled: 'warning' };
    return map[status] || 'default';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back button */}
      <button
        onClick={() => router.push('/campaigns')}
        className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-cyan-400 font-medium transition-colors"
      >
        <ChevronLeft size={16} />
        Voltar para Campanhas
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

        <div className="flex flex-wrap items-center gap-3">
          {campaign?.status === 'processing' ? (
            <Button variant="danger" onClick={handleCancelCampaign} loading={cancelling}>
              <CircleStop size={16} /> Parar automação
            </Button>
          ) : (
            <button
              onClick={handleActivateCampaign}
              disabled={activating}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white rounded-xl text-xs font-bold shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all"
            >
              {activating ? (
                <RotateCw size={14} className="animate-spin text-white" />
              ) : (
                <Play size={14} className="fill-white text-white" />
              )}
              <span>{activating ? 'Ativando...' : '⚡ Ativar / Reexecutar Radar'}</span>
            </button>
          )}
          <Button variant="secondary" onClick={handleExportCSV} loading={exporting} disabled={!leads.length}>
            📥 Exportar CSV
          </Button>
        </div>
      </div>

      {/* Processing message */}
      {campaign?.status === 'processing' && (
        <Card className="border-cyan-500/30 bg-cyan-500/10">
          <div className="flex items-center gap-3">
            <div className="animate-spin w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full" />
            <div>
              <p className="text-sm font-semibold text-cyan-300">Campanha em processamento...</p>
              <p className="text-xs text-cyan-200/70 mt-0.5">Os dados básicos dos leads estão sendo coletados. Atualizando automaticamente.</p>
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

      {campaign?.status === 'cancelled' && (
        <Card className="border-amber-500/30 bg-amber-500/10">
          <p className="text-sm font-semibold text-amber-300">Campanha parada</p>
          <p className="text-xs text-amber-200/70 mt-1">Os leads encontrados antes da parada foram mantidos.</p>
        </Card>
      )}

      {/* Leads table */}
      <Card padding="p-0">
        <LeadTable
          leads={leads}
          onGetData={handleGetLeadData}
          onAddToCrm={handleAddLeadToCrm}
          addingLeadId={addingLeadId}
        />
      </Card>
    </div>
  );
}
