'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Link from 'next/link';

const STATUS_COLUMNS = [
  { id: 'new', label: 'Novo', color: 'border-t-cyan-300/70' },
  { id: 'contacted', label: 'Contatado', color: 'border-t-blue-300/70' },
  { id: 'negotiation', label: 'Interessado', color: 'border-t-amber-300/70' },
  { id: 'won', label: 'Fechado (Ganho)', color: 'border-t-emerald-300/70' },
  { id: 'paid', label: 'Pago', color: 'border-t-violet-300/70' },
  { id: 'lost', label: 'Perdido', color: 'border-t-rose-300/70' },
];

const COMPANY_NAMES = {
  g_system: 'G-System',
  spy_car: 'Spy Car',
};

function formatLastRecord(value) {
  if (!value) return 'Sem registros';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? '—'
    : date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

export default function CRMPage() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [accessLevel, setAccessLevel] = useState(null);
  const [companyFilter, setCompanyFilter] = useState('all');
  const [draggedLead, setDraggedLead] = useState(null);

  useEffect(() => {
    let active = true;

    const loadAccessLevel = async () => {
      try {
        const response = await fetch('/api/auth');
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || 'Não foi possível identificar seu perfil.');
        const level = result?.user?.access_level;
        if (!level) throw new Error('Perfil de acesso não encontrado.');
        if (active) setAccessLevel(level);
      } catch (err) {
        if (active) {
          setError(err.message || 'Não foi possível carregar seu perfil.');
          setLoading(false);
        }
      }
    };

    loadAccessLevel();
    return () => {
      active = false;
    };
  }, []);

  const loadLeads = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (accessLevel === 'diretoria' && companyFilter !== 'all') {
        params.set('tenant_id', companyFilter);
      }
      const query = params.toString();
      const data = await fetchApi(`/leads${query ? `?${query}` : ''}`);
      setLeads(data.data || []);
    } catch (err) {
      console.error('Erro ao carregar leads:', err);
      setError(err.message || 'Não foi possível carregar os leads do CRM.');
    } finally {
      setLoading(false);
    }
  }, [accessLevel, companyFilter]);

  useEffect(() => {
    if (accessLevel) loadLeads();
  }, [accessLevel, loadLeads]);

  const updateLeadStatus = async (leadId, newStatus) => {
    setLeads(current => current.map(lead => (
      lead.id === leadId ? { ...lead, commercial_status: newStatus } : lead
    )));
    try {
      await fetchApi(`/leads/${leadId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
      await loadLeads();
    } catch (err) {
      console.error('Erro ao atualizar status:', err);
      await loadLeads();
      setError(err.message || 'Não foi possível atualizar o status do lead.');
    }
  };

  const handleDragStart = (event, lead) => {
    setDraggedLead(lead);
    event.dataTransfer.effectAllowed = 'move';
    setTimeout(() => {
      event.target.style.opacity = '0.5';
    }, 0);
  };

  const handleDragEnd = (event) => {
    event.target.style.opacity = '1';
    setDraggedLead(null);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (event, targetStatus) => {
    event.preventDefault();
    if (draggedLead && draggedLead.commercial_status !== targetStatus) {
      updateLeadStatus(draggedLead.id, targetStatus);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[50vh]">
        <div className="animate-spin w-8 h-8 border-3 border-cyan-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-200/60">
            Workspace <span className="mx-1 text-gray-700">/</span> Pipeline
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-gray-100 sm:text-3xl">CRM Vendas</h1>
          <p className="mt-1 text-sm text-gray-400">Acompanhe somente os leads adicionados ao CRM.</p>
        </div>
        {accessLevel === 'diretoria' && (
          <label className="flex flex-col gap-1 text-xs font-semibold text-gray-400">
            Empresa
            <select
              value={companyFilter}
              onChange={(event) => setCompanyFilter(event.target.value)}
              className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 focus:border-cyan-500 focus:outline-none"
            >
              <option value="all">Ambos</option>
              <option value="g_system">G-System</option>
              <option value="spy_car">Spy Car</option>
            </select>
          </label>
        )}
      </div>

      {error && (
        <p role="alert" className="mb-4 rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          {error}
        </p>
      )}

      {leads.length === 0 ? (
        <Card className="flex flex-col items-center justify-center min-h-64 text-center p-8">
          <h2 className="text-lg font-semibold text-gray-200">
            {companyFilter === 'all' ? 'Seu CRM está vazio' : 'Nenhum lead no CRM para esta empresa'}
          </h2>
          <p className="text-sm text-gray-400 mt-2 max-w-md">
            {companyFilter === 'all'
              ? 'Adicione somente os leads que deseja acompanhar usando o botão “Adicionar ao CRM” na lista da campanha.'
              : 'Tente outra empresa no filtro ou adicione leads ao CRM pela lista da campanha.'}
          </p>
          <Link
            href="/campaigns"
            className="mt-5 px-4 py-2 rounded-lg bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20 text-sm font-semibold transition-colors"
          >
            Ver campanhas
          </Link>
        </Card>
      ) : (
        <div className="flex-1 flex gap-4 overflow-x-auto pb-4 snap-x">
          {STATUS_COLUMNS.map(column => {
            const columnLeads = leads.filter(lead => (lead.commercial_status || 'new') === column.id);

            return (
              <div
                key={column.id}
                className={`flex-shrink-0 w-80 overflow-hidden rounded-2xl border border-white/[0.07] border-t-2 bg-[#09111d]/75 shadow-[0_12px_36px_rgba(0,0,0,0.16)] backdrop-blur-xl ${column.color} flex flex-col snap-center`}
                onDragOver={handleDragOver}
                onDrop={(event) => handleDrop(event, column.id)}
              >
                <div className="flex items-center justify-between border-b border-white/[0.06] bg-white/[0.02] p-4">
                  <h2 className="text-xs font-semibold uppercase tracking-[0.1em] text-gray-300">{column.label}</h2>
                  <span className="rounded-lg border border-white/[0.07] bg-white/[0.04] px-2 py-1 font-mono text-[10px] font-medium text-gray-400">
                    {columnLeads.length}
                  </span>
                </div>

                <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
                  {columnLeads.map(lead => (
                    <div
                      key={lead.id}
                      draggable
                      onDragStart={(event) => handleDragStart(event, lead)}
                      onDragEnd={handleDragEnd}
                      className="cursor-grab active:cursor-grabbing transform transition-all hover:-translate-y-1"
                    >
                      <Card className="hover:border-gray-600/50 hover:bg-gray-800/30 transition-colors cursor-pointer" padding="0">
                        <Link href={`/crm/${lead.id}`} className="block p-4">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-bold text-gray-200 hover:text-cyan-400 transition-colors text-sm truncate pr-2 block">
                              {lead.name}
                            </span>
                            {accessLevel === 'diretoria' && (
                              <Badge variant={lead.tenant_id === 'spy_car' ? 'warning' : 'info'} size="sm" className="shrink-0">
                                {COMPANY_NAMES[lead.tenant_id] || 'Empresa'}
                              </Badge>
                            )}
                          </div>

                          <div className="text-xs text-gray-500 mb-3 truncate">
                            {lead.city || 'Cidade desconhecida'}
                          </div>

                          <div className="flex justify-between items-center pt-2 border-t border-gray-700/50">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wide">Último registro</span>
                            <span className="text-xs font-semibold text-gray-300">{formatLastRecord(lead.last_record_at)}</span>
                          </div>
                        </Link>

                        <div className="flex justify-end pb-3 px-4">
                          <div className="md:hidden flex gap-1">
                            <button
                              onClick={() => {
                                const currentIndex = STATUS_COLUMNS.findIndex(item => item.id === column.id);
                                if (currentIndex > 0) updateLeadStatus(lead.id, STATUS_COLUMNS[currentIndex - 1].id);
                              }}
                              className="p-1 text-gray-500 hover:text-white bg-gray-800 rounded disabled:opacity-30"
                              disabled={column.id === 'new'}
                              aria-label="Mover lead para a etapa anterior"
                            >
                              {'<'}
                            </button>
                            <button
                              onClick={() => {
                                const currentIndex = STATUS_COLUMNS.findIndex(item => item.id === column.id);
                                if (currentIndex < STATUS_COLUMNS.length - 1) updateLeadStatus(lead.id, STATUS_COLUMNS[currentIndex + 1].id);
                              }}
                              className="p-1 text-gray-500 hover:text-white bg-gray-800 rounded disabled:opacity-30"
                              disabled={column.id === 'lost'}
                              aria-label="Mover lead para a próxima etapa"
                            >
                              {'>'}
                            </button>
                          </div>
                        </div>
                      </Card>
                    </div>
                  ))}

                  {columnLeads.length === 0 && (
                    <div className="h-24 flex items-center justify-center border-2 border-dashed border-gray-800 rounded-lg">
                      <p className="text-xs text-gray-600 font-medium">Solte aqui</p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
