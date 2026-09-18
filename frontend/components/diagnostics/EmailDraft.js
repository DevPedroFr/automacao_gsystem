'use client';

import { useState } from 'react';
import Card from '@/components/ui/Card';
import { Mail, MessageCircle, Copy, Check, MessageSquare } from 'lucide-react';

const InstagramIcon = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="20" x="2" y="2" rx="5" ry="5"/>
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
    <line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>
  </svg>
);

export default function EmailDraft({ emailText = '', whatsappText = '', instagramText = '' }) {
  const [activeTab, setActiveTab] = useState('email');
  const [copied, setCopied] = useState(false);

  const drafts = {
    email: { label: 'E-mail', icon: <Mail size={14} />, text: emailText },
    whatsapp: { label: 'WhatsApp', icon: <MessageCircle size={14} />, text: whatsappText },
    instagram: { label: 'Instagram DM', icon: <InstagramIcon size={14} />, text: instagramText },
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

  if (!emailText && !whatsappText && !instagramText) {
    return (
      <Card padding="p-8" className="bg-gray-900/40 backdrop-blur-md border border-gray-700/50 shadow-xl h-full flex flex-col items-center justify-center text-center">
        <MessageSquare size={24} className="text-gray-500 mb-4" />
        <h3 className="text-gray-300 font-bold mb-2">Mensagens Não Encontradas</h3>
        <p className="text-sm text-gray-500">Ocorreu um erro na geração das mensagens. Clique em "Regenerar Diagnóstico" para gerar novamente.</p>
      </Card>
    );
  }

  return (
    <Card padding="p-6" className="bg-gray-900/40 backdrop-blur-md border border-gray-700/50 shadow-xl no-print">
      <div className="flex flex-col space-y-4">
        {/* Header and Copy Button */}
        <div className="flex items-center justify-between border-b border-gray-700/50 pb-4">
          <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
            <MessageSquare size={16} className="text-cyan-400" /> Mensagens de Abordagem
          </h3>
          <button
            onClick={handleCopy}
            disabled={!activeContent}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all duration-300 shadow-sm ${
              copied
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 hover:shadow-[0_0_15px_rgba(6,182,212,0.2)] disabled:opacity-50 disabled:cursor-not-allowed'
            }`}
          >
            {copied ? (
              <>
                <Check size={14} /> Copiado!
              </>
            ) : (
              <>
                <Copy size={14} /> Copiar Mensagem
              </>
            )}
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-gray-700/50 overflow-x-auto">
          {Object.entries(drafts).map(([key, draft]) => {
            if (!draft.text) return null;
            return (
              <button
                key={key}
                onClick={() => {
                  setActiveTab(key);
                  setCopied(false);
                }}
                className={`flex items-center gap-2 px-6 py-3 text-sm font-semibold transition-all duration-300 border-b-2 -mb-px whitespace-nowrap ${
                  activeTab === key
                    ? 'border-cyan-400 text-cyan-400 bg-cyan-500/5'
                    : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500 hover:bg-gray-800/30'
                }`}
              >
                <span className={activeTab === key ? 'animate-pulse' : ''}>{draft.icon}</span>
                <span>{draft.label}</span>
              </button>
            );
          })}
        </div>

        {/* Message Content Area */}
        <div className="mt-4">
          {activeContent ? (
            <textarea
              readOnly
              value={activeContent}
              className="w-full h-64 p-5 bg-gray-950/50 border border-gray-700/50 rounded-xl text-xs text-gray-300 leading-relaxed font-mono resize-none focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all shadow-inner"
            />
          ) : (
            <p className="text-xs text-gray-500 italic py-4 text-center bg-gray-900/50 rounded-xl border border-gray-800/50">
              Nenhuma mensagem disponível para este canal.
            </p>
          )}
        </div>
      </div>
    </Card>
  );
}
