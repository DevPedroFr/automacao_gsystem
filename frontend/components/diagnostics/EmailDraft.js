'use client';

import { useState } from 'react';
import Card from '@/components/ui/Card';

export default function EmailDraft({ emailText = '', whatsappText = '', instagramText = '' }) {
  const [activeTab, setActiveTab] = useState('email');
  const [copied, setCopied] = useState(false);

  const drafts = {
    email: { label: '📧 E-mail', text: emailText },
    whatsapp: { label: '💬 WhatsApp', text: whatsappText },
    instagram: { label: '📸 Instagram DM', text: instagramText },
  };

  const activeContent = drafts[activeTab]?.text || '';

  const handleCopy = async () => {
    if (!activeContent) return;
    try {
      await navigator.clipboard.writeText(activeContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const textarea = document.createElement('textarea');
      textarea.value = activeContent;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!emailText && !whatsappText && !instagramText) return null;

  return (
    <Card>
      <div className="flex flex-col space-y-4">
        {/* Header and Copy Button */}
        <div className="flex items-center justify-between border-b border-gray-100 pb-3">
          <h3 className="text-base font-bold text-gray-900 flex items-center gap-1.5">
            <span>📢</span> Mensagens de Abordagem
          </h3>
          <button
            onClick={handleCopy}
            disabled={!activeContent}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition-all duration-200 ${
              copied
                ? 'bg-green-100 text-green-700 border border-green-200'
                : 'bg-cyan-50 text-cyan-700 border border-cyan-150 hover:bg-cyan-100'
            }`}
          >
            {copied ? '✓ Copiado!' : '📋 Copiar Mensagem'}
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-gray-200">
          {Object.entries(drafts).map(([key, draft]) => {
            if (!draft.text) return null;
            return (
              <button
                key={key}
                onClick={() => {
                  setActiveTab(key);
                  setCopied(false);
                }}
                className={`px-4 py-2 text-xs font-bold border-b-2 transition-all duration-200 -mb-px ${
                  activeTab === key
                    ? 'border-cyan-500 text-cyan-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {draft.label}
              </button>
            );
          })}
        </div>

        {/* Message Content Area */}
        <div>
          {activeContent ? (
            <textarea
              readOnly
              value={activeContent}
              className="w-full h-56 p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-gray-700 leading-relaxed font-mono resize-none focus:outline-none"
            />
          ) : (
            <p className="text-xs text-gray-400 italic py-4 text-center">Nenhuma mensagem disponível para este canal.</p>
          )}
        </div>
      </div>
    </Card>
  );
}
