'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Badge from '@/components/ui/Badge';
import { STATUS_CONFIG } from '@/lib/constants';
import { fetchApi } from '@/lib/api';
import {
  Play, Pause, RotateCw, ExternalLink, Flame, Globe, ArrowRight
} from 'lucide-react';

export default function CampaignTable({ campaigns = [], onRefresh }) {
  const router = useRouter();
  const [loadingAction, setLoadingAction] = useState({});

  if (!campaigns.length) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="text-lg">Nenhuma campanha encontrada</p>
        <p className="text-sm mt-1">Crie uma nova campanha para começar a captar leads</p>
      </div>
    );
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getStatusVariant = (status) => {
    const map = { processing: 'info', completed: 'success', failed: 'danger', cancelled: 'warning' };
    return map[status] || 'default';
  };

  const handleActivate = async (campaignId, e) => {
    e.stopPropagation();
    try {
      setLoadingAction((prev) => ({ ...prev, [campaignId]: 'activating' }));
      await fetchApi(`/campaigns/${campaignId}/activate`, { method: 'POST' });
      onRefresh?.();
    } catch (err) {
      console.error('Erro ao ativar campanha:', err);
      alert('Erro ao ativar campanha: ' + (err.message || 'Falha no servidor'));
    } finally {
      setLoadingAction((prev) => ({ ...prev, [campaignId]: null }));
    }
  };

  const handleCancel = async (campaignId, e) => {
    e.stopPropagation();
    if (!window.confirm('Deseja pausar esta campanha?')) return;
    try {
      setLoadingAction((prev) => ({ ...prev, [campaignId]: 'cancelling' }));
      await fetchApi(`/campaigns/${campaignId}/cancel`, { method: 'POST' });
      onRefresh?.();
    } catch (err) {
      console.error('Erro ao pausar campanha:', err);
      alert('Erro ao pausar campanha: ' + (err.message || 'Falha no servidor'));
    } finally {
      setLoadingAction((prev) => ({ ...prev, [campaignId]: null }));
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-gray-700/50 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
            <th className="py-3 px-4">Nicho</th>
            <th className="py-3 px-4">Localização</th>
            <th className="py-3 px-4">Status</th>
            <th className="py-3 px-4 text-center">Total Leads</th>
            <th className="py-3 px-4 text-center">Prioridade A</th>
            <th className="py-3 px-4 text-center">Sem Site</th>
            <th className="py-3 px-4">Data</th>
            <th className="py-3 px-4 text-right">Ação</th>
          </tr>
        </thead>
        <tbody>
          {campaigns.slice(0, 8).map((campaign) => {
            const statusConf = STATUS_CONFIG[campaign.status] || {};
            const isProcessing = campaign.status === 'processing';
            const actLoading = loadingAction[campaign.id];

            return (
              <tr
                key={campaign.id}
                onClick={() => router.push(`/campaigns/${campaign.id}`)}
                className="border-b border-gray-800/80 hover:bg-gray-800/50 cursor-pointer transition-colors duration-150 group text-xs"
              >
                <td className="py-3.5 px-4 font-semibold text-gray-100 group-hover:text-cyan-400 transition-colors">
                  {campaign.niche}
                </td>
                <td className="py-3.5 px-4 text-gray-300">{campaign.location}</td>
                <td className="py-3.5 px-4">
                  <Badge variant={getStatusVariant(campaign.status)}>
                    {isProcessing ? (
                      <span className="flex items-center gap-1">
                        <RotateCw size={11} className="animate-spin text-cyan-400" />
                        <span>Processando</span>
                      </span>
                    ) : (
                      <span>{statusConf.icon} {statusConf.label || campaign.status}</span>
                    )}
                  </Badge>
                </td>
                <td className="py-3.5 px-4 text-center font-bold text-gray-100">
                  {campaign.total_leads ?? 0}
                </td>
                <td className="py-3.5 px-4 text-center">
                  <span className="inline-flex items-center gap-1 font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20 text-[11px]">
                    <Flame size={10} /> {campaign.priority_a ?? 0}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-center">
                  <span className="inline-flex items-center gap-1 font-bold text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded-full border border-purple-500/20 text-[11px]">
                    <Globe size={10} /> {campaign.without_website ?? 0}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-gray-400">{formatDate(campaign.created_at)}</td>
                <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center justify-end gap-1.5">
                    {isProcessing ? (
                      <button
                        onClick={(e) => handleCancel(campaign.id, e)}
                        disabled={actLoading === 'cancelling'}
                        className="p-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-xs transition-colors"
                        title="Pausar automação"
                      >
                        <Pause size={13} />
                      </button>
                    ) : (
                      <button
                        onClick={(e) => handleActivate(campaign.id, e)}
                        disabled={actLoading === 'activating'}
                        className="px-2.5 py-1 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 hover:text-white border border-cyan-500/30 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1"
                        title="Ativar/Reexecutar busca e triagem"
                      >
                        {actLoading === 'activating' ? (
                          <RotateCw size={12} className="animate-spin text-cyan-400" />
                        ) : (
                          <Play size={11} className="fill-cyan-400 text-cyan-400" />
                        )}
                        <span>Ativar</span>
                      </button>
                    )}

                    <button
                      onClick={() => router.push(`/campaigns/${campaign.id}`)}
                      className="p-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white border border-gray-700 rounded-lg text-xs transition-colors"
                      title="Abrir campanha"
                    >
                      <ExternalLink size={13} />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}