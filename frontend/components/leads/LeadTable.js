'use client';

export default function LeadTable({ leads = [], onGetData, onAddToCrm, addingLeadId }) {
  if (!leads.length) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="text-lg">Nenhum lead encontrado</p>
        <p className="text-sm mt-1">Aguarde a coleta dos leads ou inicie uma campanha</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700/50">
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Nome</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Endereço</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Google</th>
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => {
            return (
              <tr
                key={lead.id}
                className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors duration-150"
              >
                <td className="py-3.5 px-4 text-sm font-medium text-gray-100">{lead.name}</td>
                <td className="py-3.5 px-4 text-sm text-gray-300">{lead.address || lead.city || '—'}</td>
                <td className="py-3.5 px-4">
                  <div className="flex items-center gap-1.5">
                    <span className="text-yellow-500">⭐</span>
                    <span className="text-sm font-medium text-gray-100">{lead.google_rating ?? '—'}</span>
                  </div>
                </td>
                <td className="py-3.5 px-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      onClick={() => onGetData?.(lead.id)}
                      className="text-sm font-medium text-cyan-400 hover:text-cyan-300 transition-colors"
                    >
                      Obter dados
                    </button>
                    <button
                      onClick={() => onAddToCrm?.(lead.id)}
                      disabled={lead.in_crm || addingLeadId === lead.id}
                      className="text-sm font-medium text-emerald-400 hover:text-emerald-300 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors"
                    >
                      {lead.in_crm
                        ? 'Já está no CRM'
                        : addingLeadId === lead.id
                          ? 'Adicionando...'
                          : 'Adicionar ao CRM'}
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
