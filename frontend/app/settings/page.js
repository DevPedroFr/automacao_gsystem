'use client';

import { useState, useEffect } from 'react';
import { fetchApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function SettingsPage() {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [toast, setToast] = useState(null);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    async function loadSettings() {
      try {
        setLoading(true);
        const res = await fetchApi('/settings');
        if (res?.data?.webhook_url) {
          setWebhookUrl(res.data.webhook_url);
        }
      } catch (err) {
        showToast('error', 'Erro ao carregar configurações');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadSettings();
  }, []);

  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      const res = await fetchApi('/settings', {
        method: 'POST',
        body: JSON.stringify({ webhook_url: webhookUrl }),
      });
      if (res?.data?.webhook_url !== undefined) {
        setWebhookUrl(res.data.webhook_url);
      }
      showToast('success', 'Configurações salvas com sucesso!');
    } catch (err) {
      showToast('error', err.message || 'Erro ao salvar configurações');
    } finally {
      setSaving(false);
    }
  };

  const handleTestWebhook = async () => {
    try {
      setTesting(true);
      setTestResult(null);
      const res = await fetchApi('/settings/test-webhook', {
        method: 'POST',
        body: JSON.stringify({ webhook_url: webhookUrl }),
      });
      if (res.success) {
        setTestResult({ success: true, message: res.message });
        showToast('success', 'Webhook de teste disparado com sucesso!');
      } else {
        setTestResult({ success: false, message: res.message, details: res.details });
        showToast('error', 'Falha no teste do webhook');
      }
    } catch (err) {
      setTestResult({ success: false, message: err.message });
      showToast('error', 'Falha ao conectar com a URL do webhook');
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="h-8 bg-gray-800/60 rounded-xl w-64 animate-pulse-soft border border-gray-700/30" />
        <div className="bg-gray-900/60 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 h-96 animate-pulse-soft" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-xl shadow-2xl border text-sm font-semibold backdrop-blur-xl transition-all duration-300 animate-slide-up flex items-center gap-2 ${
            toast.type === 'success'
              ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300 shadow-[0_0_20px_rgba(16,185,129,0.2)]'
              : 'bg-rose-950/80 border-rose-500/40 text-rose-300 shadow-[0_0_20px_rgba(244,63,94,0.2)]'
          }`}
        >
          <span>{toast.type === 'success' ? '✅' : '❌'}</span>
          <span>{toast.message}</span>
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Configurações & Integrações</h1>
        <p className="text-sm text-gray-400 mt-1">
          Configure automações para n8n/Make.com e consulte as especificações da API.
        </p>
      </div>

      {/* Webhooks Panel */}
      <Card>
        <h2 className="text-lg font-bold text-gray-100 mb-4 flex items-center gap-2">
          <span>📡</span> Automação em Tempo Real (Webhooks)
        </h2>
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label htmlFor="webhookUrl" className="block text-sm font-semibold text-gray-300 mb-2">
              URL do Webhook (Make.com ou n8n)
            </label>
            <input
              id="webhookUrl"
              type="url"
              placeholder="https://hook.us1.make.com/... ou https://n8n.seu-servidor.com/..."
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700/50 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all shadow-inner"
            />
            <p className="text-xs text-gray-400 mt-2 leading-relaxed">
              O sistema disparará requisições POST JSON automaticamente quando uma busca for concluída
              (<code className="font-mono bg-gray-800 border border-gray-700/60 px-1.5 py-0.5 rounded text-cyan-300">campaign_completed</code>) ou 
              quando um diagnóstico de lead for gerado (<code className="font-mono bg-gray-800 border border-gray-700/60 px-1.5 py-0.5 rounded text-cyan-300">diagnostic_generated</code>).
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button type="submit" loading={saving}>
              Salvar Configurações
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={handleTestWebhook}
              loading={testing}
              disabled={!webhookUrl}
            >
              Enviar Webhook de Teste 🧪
            </Button>
          </div>
        </form>

        {/* Test results */}
        {testResult && (
          <div
            className={`mt-5 p-4 border rounded-xl text-sm backdrop-blur-md ${
              testResult.success
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300 animate-fade-in'
                : 'bg-rose-500/10 border-rose-500/30 text-rose-300 animate-fade-in'
            }`}
          >
            <p className="font-semibold">{testResult.success ? 'Conexão Estabelecida!' : 'Falha na Conexão'}</p>
            <p className="mt-1 text-xs opacity-90">{testResult.message}</p>
            {testResult.details && (
              <pre className="mt-2 p-3 bg-gray-950/70 border border-gray-800 rounded-lg text-xs font-mono overflow-x-auto whitespace-pre-wrap text-gray-300">
                {testResult.details}
              </pre>
            )}
          </div>
        )}
      </Card>

      {/* API Reference */}
      <Card>
        <h2 className="text-lg font-bold text-gray-100 mb-4 flex items-center gap-2">
          <span>📚</span> Guia de API (Integração Direta)
        </h2>
        <p className="text-sm text-gray-400 mb-5 leading-relaxed">
          Se você prefere que o Make.com ou n8n faça a consulta ativa (*pull*) ou dispare ações diretamente, use os endpoints da nossa API local:
        </p>

        <div className="space-y-6">
          {/* Endpoint 1 */}
          <div className="border-t border-gray-800 pt-5 first:border-0 first:pt-0">
            <div className="flex items-center gap-2">
              <span className="bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-semibold text-xs px-2.5 py-0.5 rounded-full font-mono">POST</span>
              <span className="font-mono text-sm font-semibold text-gray-200">/api/campaigns</span>
            </div>
            <p className="text-xs text-gray-400 mt-1.5">Dispara a busca de novos leads (Radar) para um nicho e cidade.</p>
            <div className="mt-3 bg-gray-950/60 border border-gray-800 rounded-xl p-4 shadow-inner">
              <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">Exemplo de Payload (Request):</p>
              <pre className="text-xs font-mono text-cyan-200/90 overflow-x-auto">
{`{
  "niche": "Clínicas Odontológicas",
  "location": "Curitiba, PR"
}`}
              </pre>
            </div>
          </div>

          {/* Endpoint 2 */}
          <div className="border-t border-gray-800 pt-5">
            <div className="flex items-center gap-2">
              <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold text-xs px-2.5 py-0.5 rounded-full font-mono">GET</span>
              <span className="font-mono text-sm font-semibold text-gray-200">/api/campaigns/:id</span>
            </div>
            <p className="text-xs text-gray-400 mt-1.5">Retorna os dados da campanha, incluindo o <code className="bg-gray-800 border border-gray-700/60 px-1.5 py-0.5 rounded text-cyan-300">status</code> ("processing", "completed", "failed").</p>
          </div>

          {/* Endpoint 3 */}
          <div className="border-t border-gray-800 pt-5">
            <div className="flex items-center gap-2">
              <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold text-xs px-2.5 py-0.5 rounded-full font-mono">GET</span>
              <span className="font-mono text-sm font-semibold text-gray-200">/api/campaigns/:campaignId/leads</span>
            </div>
            <p className="text-xs text-gray-400 mt-1.5">Lista todos os leads obtidos na campanha, com filtros opcionais.</p>
          </div>

          {/* Endpoint 4 */}
          <div className="border-t border-gray-800 pt-5">
            <div className="flex items-center gap-2">
              <span className="bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-semibold text-xs px-2.5 py-0.5 rounded-full font-mono">POST</span>
              <span className="font-mono text-sm font-semibold text-gray-200">/api/leads/:leadId/diagnostic</span>
            </div>
            <p className="text-xs text-gray-400 mt-1.5">Gera o diagnóstico de IA (com rascunho de e-mail e prompt do Stitch) para um lead específico.</p>
            <div className="mt-3 bg-gray-950/60 border border-gray-800 rounded-xl p-4 shadow-inner">
              <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">Exemplo de Resposta (Response):</p>
              <pre className="text-xs font-mono text-cyan-200/90 overflow-x-auto max-h-40 overflow-y-auto">
{`{
  "data": {
    "lead_id": "uuid-do-lead",
    "diagnostic_status": "completed",
    "observed_facts": "- Avaliação no Google: 4.8...",
    "inferences": "O site possui carregamento lento...",
    "recommendations": "- Otimizar imagens...",
    "email_draft": "Subject: Growth opportunity...",
    "stitch_prompt": "Create a landing page for..."
  }
}`}
              </pre>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
