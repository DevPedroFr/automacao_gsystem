export const PRIORITY_CONFIG = {
  A: { label: 'Prioridade A', color: '#22C55E', bgClass: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30', dotClass: 'bg-emerald-400' },
  B: { label: 'Prioridade B', color: '#F59E0B', bgClass: 'bg-amber-500/15 text-amber-400 border border-amber-500/30', dotClass: 'bg-amber-400' },
  C: { label: 'Prioridade C', color: '#EF4444', bgClass: 'bg-rose-500/15 text-rose-400 border border-rose-500/30', dotClass: 'bg-rose-400' },
};

export const STATUS_CONFIG = {
  processing: { label: 'Processando', bgClass: 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30', icon: '⏳' },
  completed: { label: 'Concluído', bgClass: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30', icon: '✅' },
  failed: { label: 'Falhou', bgClass: 'bg-rose-500/15 text-rose-400 border border-rose-500/30', icon: '❌' },
};
