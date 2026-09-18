'use client';

import { useState, useEffect } from 'react';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import { PRIORITY_CONFIG } from '@/lib/constants';
import Link from 'next/link';

const STATUS_COLUMNS = [
  { id: 'new', label: 'Novo', color: 'border-cyan-500' },
  { id: 'contacted', label: 'Contatado', color: 'border-blue-500' },
  { id: 'negotiation', label: 'Em Negociação', color: 'border-yellow-500' },
  { id: 'won', label: 'Fechado (Ganho)', color: 'border-emerald-500' },
  { id: 'lost', label: 'Perdido', color: 'border-rose-500' },
];

export default function CRMPage() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [draggedLead, setDraggedLead] = useState(null);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    try {
      const data = await fetchApi('/leads');
      setLeads(data.data || []);
    } catch (err) {
      console.error('Erro ao carregar leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateLeadStatus = async (leadId, newStatus) => {
    // Optimistic UI update
    setLeads(current => current.map(l => l.id === leadId ? { ...l, commercial_status: newStatus } : l));
    try {
      await fetchApi(`/leads/${leadId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
    } catch (err) {
      console.error('Erro ao atualizar status:', err);
      loadLeads(); // rollback on error
    }
  };

  const handleDragStart = (e, lead) => {
    setDraggedLead(lead);
    e.dataTransfer.effectAllowed = 'move';
    // Small delay to allow the drag image to be generated before making the original invisible
    setTimeout(() => {
      e.target.style.opacity = '0.5';
    }, 0);
  };

  const handleDragEnd = (e) => {
    e.target.style.opacity = '1';
    setDraggedLead(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, targetStatus) => {
    e.preventDefault();
    if (draggedLead && draggedLead.commercial_status !== targetStatus) {
      updateLeadStatus(draggedLead.id, targetStatus);
    }
  };

  const getPriorityVariant = (priority) => {
    const map = { A: 'success', B: 'warning', C: 'danger' };
    return map[priority] || 'default';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[50vh]">
        <div className="animate-spin w-8 h-8 border-3 border-cyan-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-100">CRM Vendas</h1>
        <p className="text-sm text-gray-400">Acompanhe e movimente as oportunidades de todas as campanhas.</p>
      </div>

      <div className="flex-1 flex gap-4 overflow-x-auto pb-4 snap-x">
        {STATUS_COLUMNS.map(column => {
          const columnLeads = leads.filter(l => (l.commercial_status || 'new') === column.id);
          
          return (
            <div 
              key={column.id}
              className={`flex-shrink-0 w-80 bg-gray-900/40 rounded-xl border-t-4 ${column.color} flex flex-col snap-center`}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, column.id)}
            >
              <div className="p-4 border-b border-gray-800/50 flex justify-between items-center bg-gray-900/60 rounded-t-xl">
                <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider">{column.label}</h2>
                <span className="bg-gray-800 text-gray-400 text-xs px-2 py-1 rounded-md font-medium">
                  {columnLeads.length}
                </span>
              </div>
              
              <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
                {columnLeads.map(lead => {
                  const pConf = PRIORITY_CONFIG[lead.priority] || {};
                  
                  return (
                    <div
                      key={lead.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, lead)}
                      onDragEnd={handleDragEnd}
                      className="cursor-grab active:cursor-grabbing transform transition-all hover:-translate-y-1"
                    >
                      <Card className="hover:border-gray-600/50" padding="p-4">
                        <div className="flex justify-between items-start mb-2">
                          <Link href={`/leads/${lead.id}`} className="font-bold text-gray-200 hover:text-cyan-400 transition-colors text-sm truncate pr-2">
                            {lead.name}
                          </Link>
                          <Badge variant={getPriorityVariant(lead.priority)} size="sm" className="shrink-0">
                            {pConf.label || lead.priority}
                          </Badge>
                        </div>
                        
                        <div className="text-xs text-gray-500 mb-3 truncate">
                          {lead.city || 'Cidade desconhecida'}
                        </div>
                        
                        <div className="flex justify-between items-center pt-2 border-t border-gray-700/50">
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wide">DMS</span>
                            <span className="text-sm font-black text-cyan-400">{lead.dms || 0}</span>
                          </div>
                          
                          {/* Botões visíveis apenas no mobile para mover entre colunas se o drag and drop for ruim na tela de toque */}
                          <div className="md:hidden flex gap-1">
                            <button 
                              onClick={() => {
                                const currentIndex = STATUS_COLUMNS.findIndex(c => c.id === column.id);
                                if (currentIndex > 0) updateLeadStatus(lead.id, STATUS_COLUMNS[currentIndex - 1].id);
                              }}
                              className="p-1 text-gray-500 hover:text-white bg-gray-800 rounded disabled:opacity-30"
                              disabled={column.id === 'new'}
                            >
                              {'<'}
                            </button>
                            <button 
                              onClick={() => {
                                const currentIndex = STATUS_COLUMNS.findIndex(c => c.id === column.id);
                                if (currentIndex < STATUS_COLUMNS.length - 1) updateLeadStatus(lead.id, STATUS_COLUMNS[currentIndex + 1].id);
                              }}
                              className="p-1 text-gray-500 hover:text-white bg-gray-800 rounded disabled:opacity-30"
                              disabled={column.id === 'lost'}
                            >
                              {'>'}
                            </button>
                          </div>
                        </div>
                      </Card>
                    </div>
                  );
                })}
                
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
    </div>
  );
}
