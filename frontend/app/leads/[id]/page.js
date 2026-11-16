'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { ChevronLeft, MapPin, Star, ExternalLink } from 'lucide-react';

const pendingResearchRequests = new Map();

function requestLeadResearch(leadId) {
  const pendingRequest = pendingResearchRequests.get(leadId);
  if (pendingRequest) return pendingRequest;

  const request = fetchApi(`/leads/${leadId}/research`, { method: 'POST' }).then(
    (result) => result?.data || result,
  );
  pendingResearchRequests.set(leadId, request);
  request.then(
    () => {
      if (pendingResearchRequests.get(leadId) === request) pendingResearchRequests.delete(leadId);
    },
    () => {
      if (pendingResearchRequests.get(leadId) === request) pendingResearchRequests.delete(leadId);
    },
  );
  return request;
}

export default function LeadDetailPage() {
  const params = useParams();
  const router = useRouter();
  const leadId = params.id;
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [research, setResearch] = useState(null);
  const [researchLoading, setResearchLoading] = useState(true);
  const [researchError, setResearchError] = useState('');

  const loadLead = useCallback(async () => {
    try {
      setError('');
      const result = await fetchApi(`/leads/${leadId}`);
      setLead(result?.data || result);
    } catch (err) {
      console.error('Erro ao carregar dados do lead:', err);
      setError(err.message || 'Não foi possível carregar os dados do lead.');
    } finally {
      setLoading(false);
    }
  }, [leadId]);

  const loadResearch = useCallback(async () => {
    try {
      setResearchError('');
      setResearchLoading(true);
      setResearch(await requestLeadResearch(leadId));
    } catch (err) {
      console.error('Erro ao pesquisar dados públicos do lead:', err);
      setResearchError(err.message || 'Não foi possível pesquisar os dados públicos.');
    } finally {
      setResearchLoading(false);
    }
  }, [leadId]);

  useEffect(() => {
    loadLead();
  }, [loadLead]);

  useEffect(() => {
    loadResearch();
  }, [loadResearch]);

  if (loading) {
    return (
      <div className="bg-gray-900/60 rounded-2xl border border-gray-700/50 p-6 h-40 animate-pulse-soft" />
    );
  }

  if (error || !lead) {
    return (
      <div className="space-y-4 text-center py-16">
        <p className="text-sm text-rose-400">{error || 'Lead não encontrado.'}</p>
        <div className="flex justify-center gap-3">
          <Button variant="secondary" onClick={() => router.back()}>
            Voltar
          </Button>
          {error && <Button onClick={loadLead}>Tentar novamente</Button>}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-cyan-400 transition-colors font-medium"
      >
        <ChevronLeft size={16} />
        Voltar à campanha
      </button>

      <h1 className="text-2xl font-bold text-gray-100">Dados do lead</h1>

      <Card>
        <div className="space-y-5">
          <h2 className="text-xl font-semibold text-gray-100">{lead.name}</h2>

          <div className="flex items-start gap-2 text-sm text-gray-300">
            <MapPin size={18} className="mt-0.5 shrink-0 text-cyan-400" />
            <span>{lead.address || lead.city || 'Endereço não informado'}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-300">
            <Star size={18} className="fill-yellow-400 text-yellow-400" />
            <span>
              {lead.google_rating != null
                ? `${lead.google_rating} estrelas no Google`
                : 'Sem avaliação no Google'}
            </span>
          </div>
        </div>
      </Card>

      <Card>
        <div className="space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-100">Informações públicas da empresa</h2>
            <p className="text-xs text-gray-400 mt-1">
              Pesquisa feita na web com base no nome e endereço do lead.
            </p>
          </div>

          {researchLoading ? (
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <span className="animate-spin w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full" />
              Pesquisando fontes públicas...
            </div>
          ) : researchError ? (
            <div className="space-y-3">
              <p className="text-sm text-rose-400">{researchError}</p>
              <Button variant="secondary" onClick={loadResearch}>
                Tentar novamente
              </Button>
            </div>
          ) : research ? (
            <>
              <dl className="grid gap-4 sm:grid-cols-2">
                {[
                  ['Responsável', research.responsible_name],
                  ['Cargo', research.responsible_role],
                  ['Telefone comercial público', research.public_business_phone],
                  ['Abertura da empresa', research.opening_date],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-xl border border-gray-700/50 bg-gray-950/40 p-4">
                    <dt className="text-xs font-semibold uppercase tracking-wide text-gray-400">{label}</dt>
                    <dd className="mt-2 text-sm text-gray-100">{value || 'Não encontrado em fonte pública'}</dd>
                  </div>
                ))}
              </dl>

              <div>
                <h3 className="text-sm font-semibold text-gray-200">Fontes</h3>
                {research.sources?.length ? (
                  <ul className="mt-2 space-y-2">
                    {research.sources.map((source) => (
                      <li key={source.url}>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-sm text-cyan-400 hover:text-cyan-300"
                        >
                          {source.title}
                          <ExternalLink size={13} />
                        </a>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-gray-500 mt-1">Nenhuma fonte foi citada para esta pesquisa.</p>
                )}
              </div>
            </>
          ) : null}
        </div>
      </Card>
    </div>
  );
}
