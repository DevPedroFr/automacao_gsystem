'use client';

import Badge from '@/components/ui/Badge';
import ScoreBar from '@/components/ui/ScoreBar';
import { PRIORITY_CONFIG } from '@/lib/constants';

export default function LeadTable({ leads = [], onViewDiagnostic }) {
  if (!leads.length) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="text-lg">Nenhum lead encontrado</p>
        <p className="text-sm mt-1">Ajuste os filtros ou aguarde o processamento</p>
      </div>
    );
  }

  const getPriorityVariant = (priority) => {
    const map = { A: 'success', B: 'warning', C: 'danger' };
    return map[priority] || 'default';
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700/50">
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Nome</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Cidade</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Avaliações</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider min-w-[120px]">DMS</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider min-w-[120px]">COS</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Prioridade</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => {
            const priorityConf = PRIORITY_CONFIG[lead.priority] || {};
            return (
              <tr
                key={lead.id}
                className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors duration-150"
              >
                <td className="py-3.5 px-4 text-sm font-medium text-gray-100">{lead.name}</td>
                <td className="py-3.5 px-4 text-sm text-gray-300">{lead.city || '—'}</td>
                <td className="py-3.5 px-4">
                  <div className="flex items-center gap-1.5">
                    <span className="text-yellow-500">⭐</span>
                    <span className="text-sm font-medium text-gray-100">{lead.google_rating ?? '—'}</span>
                    <span className="text-xs text-gray-500">({lead.google_reviews_count ?? 0})</span>
                  </div>
                </td>
                <td className="py-3.5 px-4">
                  <ScoreBar value={lead.dms ?? 0} showValue />
                </td>
                <td className="py-3.5 px-4">
                  <ScoreBar value={lead.cos ?? 0} showValue />
                </td>
                <td className="py-3.5 px-4">
                  <Badge variant={getPriorityVariant(lead.priority)}>
                    {priorityConf.label || lead.priority}
                  </Badge>
                </td>
                <td className="py-3.5 px-4">
                  <button
                    onClick={() => onViewDiagnostic?.(lead.id)}
                    className="text-sm font-medium text-cyan-400 hover:text-cyan-300 transition-colors"
                  >
                    Ver Diagnóstico
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
