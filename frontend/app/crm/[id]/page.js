'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ChevronLeft, MessageSquareText } from 'lucide-react';
import { fetchApi } from '@/lib/api';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

const STATUS_LABELS = {
  new: 'Novo',
  contacted: 'Contatado',
  negotiation: 'Interessado',
  won: 'Fechado (Ganho)',
  paid: 'Pago',
  lost: 'Perdido',
};

function formatRecordDate(value) {
  if (!value) return 'Data não disponível';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Data não disponível'
    : date.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
}

function getRecordTitle(record) {
  if (record.record_type === 'status_change') {
    const previous = STATUS_LABELS[record.previous_status] || record.previous_status;
    const next = STATUS_LABELS[record.new_status] || record.new_status;
    return `Etapa alterada de ${previous} para ${next}`;
  }
  if (record.record_type === 'crm_added') return 'Lead adicionado ao CRM';
  return 'Anotação';
}

export default function CrmLeadRecordsPage() {
  const { id: leadId } = useParams();
  const router = useRouter();
  const [lead, setLead] = useState(null);
  const [records, setRecords] = useState([]);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const loadRecordsPage = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [leadResult, recordsResult] = await Promise.all([
        fetchApi(`/leads/${leadId}`),
        fetchApi(`/leads/${leadId}/records`),
      ]);
      setLead(leadResult?.data || leadResult);
      setRecords(recordsResult?.data || []);
    } catch (err) {
      console.error('Erro ao carregar registros do lead:', err);
      setError(err.message || 'Não foi possível carregar os registros deste lead.');
    } finally {
      setLoading(false);
    }
  }, [leadId]);

  useEffect(() => {
    loadRecordsPage();
  }, [loadRecordsPage]);

  const addRecord = async (event) => {
    event.preventDefault();
    const note = content.trim();
    if (!note || saving) return;

    setSaving(true);
    setError('');
    try {
      const result = await fetchApi(`/leads/${leadId}/records`, {
        method: 'POST',
        body: JSON.stringify({ content: note }),
      });
      setRecords(current => [result.data, ...current]);
      setContent('');
    } catch (err) {
      console.error('Erro ao salvar registro do lead:', err);
      setError(err.message || 'Não foi possível salvar o registro.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="animate-spin w-8 h-8 border-3 border-cyan-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="space-y-4 py-16 text-center">
        <p role="alert" className="text-sm text-rose-400">{error || 'Lead não encontrado.'}</p>
        <div className="flex justify-center gap-3">
          <Button variant="secondary" onClick={() => router.push('/crm')}>Voltar ao CRM</Button>
          {error && <Button onClick={loadRecordsPage}>Tentar novamente</Button>}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 animate-fade-in">
      <button
        onClick={() => router.push('/crm')}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-cyan-400 transition-colors font-medium"
      >
        <ChevronLeft size={16} />
        Voltar ao CRM
      </button>

      <div>
        <h1 className="text-2xl font-bold text-gray-100">Registros do lead</h1>
        <p className="mt-1 text-sm text-gray-400">{lead.name}{lead.city ? ` · ${lead.city}` : ''}</p>
      </div>

      {error && (
        <p role="alert" className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          {error}
        </p>
      )}

      <Card>
        <form onSubmit={addRecord} className="space-y-4">
          <div>
            <label htmlFor="crm-record-content" className="text-sm font-semibold text-gray-200">
              Novo registro
            </label>
            <textarea
              id="crm-record-content"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              maxLength={5000}
              rows={4}
              required
              placeholder="Descreva o contato, retorno ou observação sobre este lead..."
              className="mt-2 w-full resize-y rounded-xl border border-gray-700 bg-gray-950/60 p-3 text-sm text-gray-100 placeholder:text-gray-600 focus:border-cyan-500 focus:outline-none"
            />
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-xs text-gray-500">Seu usuário e a data serão salvos automaticamente.</span>
            <Button type="submit" loading={saving} disabled={!content.trim()}>
              Salvar registro
            </Button>
          </div>
        </form>
      </Card>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-100">Histórico</h2>
        {records.length === 0 ? (
          <Card className="py-10 text-center">
            <MessageSquareText className="mx-auto text-gray-600" size={24} />
            <p className="mt-3 text-sm text-gray-400">Ainda não há registros para este lead.</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {records.map(record => (
              <Card key={record.id} className="border-gray-800/80" padding="p-4">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <h3 className="text-sm font-semibold text-gray-100">{getRecordTitle(record)}</h3>
                  <time className="shrink-0 text-xs text-gray-500">{formatRecordDate(record.created_at)}</time>
                </div>
                {record.content && record.record_type !== 'crm_added' && (
                  <p className="mt-3 whitespace-pre-wrap text-sm text-gray-300">{record.content}</p>
                )}
                <p className="mt-3 text-xs text-gray-500">
                  Registrado por <span className="font-semibold text-gray-300">{record.created_by}</span>
                </p>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
