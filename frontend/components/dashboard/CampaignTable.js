'use client';

import { useRouter } from 'next/navigation';
import Badge from '@/components/ui/Badge';
import { STATUS_CONFIG } from '@/lib/constants';

export default function CampaignTable({ campaigns = [] }) {
  const router = useRouter();

  if (!campaigns.length) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="text-lg">Nenhuma campanha encontrada</p>
        <p className="text-sm mt-1">Crie uma nova campanha para começar</p>
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
    const map = { processing: 'info', completed: 'success', failed: 'danger' };
    return map[status] || 'default';
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700/50">
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Nicho</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Localização</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Leads</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Data</th>
          </tr>
        </thead>
        <tbody>
          {campaigns.map((campaign) => {
            const statusConf = STATUS_CONFIG[campaign.status] || {};
            return (
              <tr
                key={campaign.id}
                onClick={() => router.push(`/campaigns/${campaign.id}`)}
                className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors duration-150 group"
              >
                <td className="py-3.5 px-4 text-sm font-medium text-gray-100 group-hover:text-cyan-400 transition-colors">{campaign.niche}</td>
                <td className="py-3.5 px-4 text-sm text-gray-300">{campaign.location}</td>
                <td className="py-3.5 px-4">
                  <Badge variant={getStatusVariant(campaign.status)}>
                    {statusConf.icon} {statusConf.label || campaign.status}
                  </Badge>
                </td>
                <td className="py-3.5 px-4 text-sm font-semibold text-gray-100">{campaign.total_leads ?? '—'}</td>
                <td className="py-3.5 px-4 text-sm text-gray-400">{formatDate(campaign.created_at)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
