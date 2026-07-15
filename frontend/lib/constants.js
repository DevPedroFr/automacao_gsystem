export const PRIORITY_CONFIG = {
  A: { label: 'Prioridade A', color: '#22C55E', bgClass: 'bg-green-100 text-green-800', dotClass: 'bg-green-500' },
  B: { label: 'Prioridade B', color: '#F59E0B', bgClass: 'bg-yellow-100 text-yellow-800', dotClass: 'bg-yellow-500' },
  C: { label: 'Prioridade C', color: '#EF4444', bgClass: 'bg-red-100 text-red-800', dotClass: 'bg-red-500' },
};

export const STATUS_CONFIG = {
  processing: { label: 'Processando', bgClass: 'bg-blue-100 text-blue-800', icon: '⏳' },
  completed: { label: 'Concluído', bgClass: 'bg-green-100 text-green-800', icon: '✅' },
  failed: { label: 'Falhou', bgClass: 'bg-red-100 text-red-800', icon: '❌' },
};
