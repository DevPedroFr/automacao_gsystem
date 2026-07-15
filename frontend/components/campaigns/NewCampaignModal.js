'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { fetchApi } from '@/lib/api';

export default function NewCampaignModal({ isOpen, onClose, onSuccess }) {
  const [niche, setNiche] = useState('');
  const [location, setLocation] = useState('');
  const [minRating, setMinRating] = useState('4.0');
  const [status, setStatus] = useState('open');
  const [negativeKeywords, setNegativeKeywords] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!niche.trim() || !location.trim()) return;

    setLoading(true);
    setError('');

    try {
      const result = await fetchApi('/campaigns', {
        method: 'POST',
        body: JSON.stringify({ 
          niche: niche.trim(), 
          location: location.trim(),
          minRating: parseFloat(minRating),
          status,
          negativeKeywords: negativeKeywords.split(',').map(k => k.trim()).filter(Boolean)
        }),
      });
      setNiche('');
      setLocation('');
      setMinRating('4.0');
      setStatus('open');
      setNegativeKeywords('');
      onSuccess?.(result);
    } catch (err) {
      setError(err.message || 'Erro ao criar campanha');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setNiche('');
      setLocation('');
      setMinRating('4.0');
      setStatus('open');
      setNegativeKeywords('');
      setError('');
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Nova Campanha de Prospecção">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="niche" className="block text-sm font-medium text-gray-700 mb-1.5">
            Nicho / Segmento
          </label>
          <input
            id="niche"
            type="text"
            value={niche}
            onChange={(e) => setNiche(e.target.value)}
            placeholder="Ex: Clínicas Odontológicas"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-colors outline-none"
            required
            disabled={loading}
          />
        </div>
        <div>
          <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1.5">
            Localização
          </label>
          <input
            id="location"
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Ex: São Paulo, SP"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-colors outline-none"
            required
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="minRating" className="block text-sm font-medium text-gray-700 mb-1.5">
              Nota Mínima
            </label>
            <select
              id="minRating"
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-colors outline-none bg-white"
              disabled={loading}
            >
              <option value="0">Qualquer Nota</option>
              <option value="3.5">Acima de 3.5</option>
              <option value="4.0">Acima de 4.0 (Bom)</option>
              <option value="4.5">Acima de 4.5 (Excelente)</option>
            </select>
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1.5">
              Status de Funcionamento
            </label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-colors outline-none bg-white"
              disabled={loading}
            >
              <option value="open">Apenas Abertos</option>
              <option value="all">Todos</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="negativeKeywords" className="block text-sm font-medium text-gray-700 mb-1.5">
            Palavras-chave Negativas <span className="text-gray-400 font-normal">(opcional)</span>
          </label>
          <input
            id="negativeKeywords"
            type="text"
            value={negativeKeywords}
            onChange={(e) => setNegativeKeywords(e.target.value)}
            placeholder="Ex: franquia, hospital, prefeitura (separado por vírgula)"
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-colors outline-none"
            disabled={loading}
          />
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={handleClose} disabled={loading}>
            Cancelar
          </Button>
          <Button type="submit" loading={loading}>
            Iniciar Radar 🔍
          </Button>
        </div>
      </form>
    </Modal>
  );
}
