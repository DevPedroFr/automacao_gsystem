'use client';

export default function LeadTable({
  leads = [],
  onGetData,
  onAddToCrm,
  addingLeadId,
  selectedLeadIds = [],
  onToggleLead,
  onToggleAll,
  onCollectSelected,
  isCollecting = false,
  collectionProgress,
  collectionError,
}) {
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
      <div className="flex flex-col gap-3 border-b border-gray-700/50 p-4 sm:flex-row sm:items-center sm:justify-between">
        <label className="flex items-center gap-2 text-sm text-gray-300">
          <input
            type="checkbox"
            checked={leads.length > 0 && leads.every((lead) => selectedLeadIds.includes(lead.id))}
            onChange={onToggleAll}
            disabled={isCollecting}
            aria-label="Selecionar todos os leads"
            className="h-4 w-4 rounded border-gray-600 bg-gray-800 text-cyan-500 focus:ring-cyan-500"
          />
          <span>
            Selecionar todos
            <span className="ml-1 text-gray-500">
              ({selectedLeadIds.length} de {leads.length})
            </span>
          </span>
        </label>
        <button
          type="button"
          onClick={onCollectSelected}
          disabled={!selectedLeadIds.length || isCollecting}
          className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-sm font-semibold text-cyan-300 transition-colors hover:bg-cyan-500/20 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isCollecting
            ? `Coletando ${collectionProgress?.current || 1} de ${collectionProgress?.total || selectedLeadIds.length}...`
            : `Obter dados dos selecionados (${selectedLeadIds.length})`}
        </button>
      </div>
      {isCollecting && collectionProgress?.leadName && (
        <p className="border-b border-gray-700/50 px-4 py-2 text-xs text-gray-400" aria-live="polite">
          Pesquisando: {collectionProgress.leadName}
        </p>
      )}
      {collectionError && (
        <p role="alert" className="border-b border-rose-500/20 bg-rose-500/5 px-4 py-3 text-sm text-rose-300">
          Falha ao pesquisar {collectionError.leadName}: {collectionError.message}
          {collectionError.remaining > 0
            ? ` ${collectionError.remaining} lead(s) selecionado(s) não foi(ram) processado(s).`
            : ''}
        </p>
      )}
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700/50">
            <th className="w-10 py-3 px-4" aria-label="Selecionar lead" />
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
                <td className="py-3.5 px-4">
                  <input
                    type="checkbox"
                    checked={selectedLeadIds.includes(lead.id)}
                    onChange={() => onToggleLead?.(lead.id)}
                    disabled={isCollecting}
                    aria-label={`Selecionar ${lead.name}`}
                    className="h-4 w-4 rounded border-gray-600 bg-gray-800 text-cyan-500 focus:ring-cyan-500"
                  />
                </td>
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
                      disabled={isCollecting}
                      className="text-sm font-medium text-cyan-400 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
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
