'use client';

import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

export default function Modal({ isOpen, onClose, title, children }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen || !mounted) return null;

  const modalContent = (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-md"
        onClick={onClose}
      />

      {/* Modal container */}
      <div className="relative z-10 flex max-h-[90vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#0b1421]/95 shadow-[0_24px_90px_rgba(0,0,0,0.55),0_0_40px_rgba(34,211,238,0.06)] backdrop-blur-2xl animate-slide-up">
        {/* Header */}
        <div className="flex shrink-0 items-center justify-between border-b border-white/[0.07] px-6 py-4">
          <h2 className="text-lg font-semibold tracking-tight text-gray-100">{title}</h2>
          <button
            onClick={onClose}
            className="rounded-lg border border-transparent p-1.5 text-gray-500 transition-colors hover:border-white/[0.08] hover:bg-white/[0.05] hover:text-white"
            aria-label="Fechar janela"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4 overflow-y-auto">{children}</div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}
