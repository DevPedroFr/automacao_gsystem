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
          <label htmlFor="niche" className="block text-sm font-bold text-gray-300 uppercase tracking-wider mb-2">
            Nicho / Segmento
          </label>
          <input
            id="niche"
            type="text"
            value={niche}
            onChange={(e) => setNiche(e.target.value)}
            placeholder="Ex: Clínicas Odontológicas"
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700/50 rounded-xl text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all outline-none shadow-inner"
            required
            disabled={loading}
          />
        </div>
        <div>
          <label htmlFor="location" className="block text-sm font-bold text-gray-300 uppercase tracking-wider mb-2">
            Localização
          </label>
          <input
            id="location"
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Ex: São Paulo, SP"
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700/50 rounded-xl text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all outline-none shadow-inner"
            required
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="minRating" className="block text-sm font-bold text-gray-300 uppercase tracking-wider mb-2">
              Nota Mínima
            </label>
            <select
              id="minRating"
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700/50 rounded-xl text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all outline-none shadow-inner appearance-none"
              disabled={loading}
            >
              <option value="0">Qualquer Nota</option>
              <option value="3.5">Acima de 3.5</option>
              <option value="4.0">Acima de 4.0 (Bom)</option>
              <option value="4.5">Acima de 4.5 (Excelente)</option>
            </select>
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-bold text-gray-300 uppercase tracking-wider mb-2">
              Status de Funcionamento
            </label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700/50 rounded-xl text-sm text-white focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all outline-none shadow-inner appearance-none"
              disabled={loading}
            >
              <option value="open">Apenas Abertos</option>
              <option value="all">Todos</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="negativeKeywords" className="block text-sm font-bold text-gray-300 uppercase tracking-wider mb-2">
            Palavras-chave Negativas <span className="text-gray-600 font-normal normal-case">(opcional)</span>
          </label>
          <input
            id="negativeKeywords"
            type="text"
            value={negativeKeywords}
            onChange={(e) => setNegativeKeywords(e.target.value)}
            placeholder="Ex: franquia, hospital, prefeitura"
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700/50 rounded-xl text-sm text-white placeholder-gray-600 focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all outline-none shadow-inner"
            disabled={loading}
          />
        </div>

        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-sm font-medium text-rose-400">
            {error}
          </div>
        )}

        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-4 border-t border-gray-700/50 mt-6">
          <button 
            type="button" 
            onClick={handleClose} 
            disabled={loading}
            className="px-6 py-3 rounded-xl text-sm font-bold text-gray-400 bg-gray-800/50 hover:bg-gray-800 hover:text-white transition-colors"
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            disabled={loading}
            className="px-6 py-3 rounded-xl text-sm font-bold text-white bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 shadow-[0_0_15px_rgba(6,182,212,0.4)] transition-all flex items-center gap-2"
          >
            {loading ? 'Iniciando...' : 'Iniciar Radar'} <span className="text-lg leading-none">🚀</span>
          </button>
        </div>
      </form>
    </Modal>
  );
}
