'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const faqs = [
  {
    question: 'Como funciona o primeiro atendimento?',
    answer: 'No nosso primeiro atendimento, ouvimos seu caso com atenção, avaliamos a documentação básica e apresentamos uma visão jurídica clara sobre os próximos passos recomendados para a sua situação trabalhista.',
  },
  {
    question: 'O escritório atende online?',
    answer: 'Sim, realizamos atendimentos virtuais para maior comodidade, além de disponibilizarmos atendimento presencial em Mogi das Cruzes mediante agendamento prévio.',
  },
  {
    question: 'Atende trabalhadores e empresas?',
    answer: 'Sim, nossa atuação engloba a orientação e defesa tanto de trabalhadores (reclamantes) quanto de empresas (reclamadas), garantindo uma análise completa das relações de trabalho.',
  },
  {
    question: 'Como posso falar com o escritório?',
    answer: 'A forma mais rápida de falar conosco é clicando no botão do WhatsApp disponível no site. Você também pode nos enviar uma mensagem e retornaremos o mais breve possível.',
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);

  const toggleFaq = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="py-24 bg-[var(--color-gray-light)]">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-serif text-[var(--color-navy)] mb-6">
            Perguntas Frequentes
          </h2>
          <div className="h-0.5 w-16 bg-[var(--color-gold)] mx-auto"></div>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div 
              key={index} 
              className="border border-gray-200 rounded-2xl bg-white overflow-hidden transition-all duration-300 shadow-sm"
            >
              <button
                className="w-full px-6 py-5 flex justify-between items-center text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-gold)]"
                onClick={() => toggleFaq(index)}
              >
                <span className="text-lg font-medium text-[var(--color-navy)] font-sans pr-8">{faq.question}</span>
                <div className={`p-2 rounded-full flex-shrink-0 transition-colors ${openIndex === index ? 'bg-[var(--color-navy)] text-white' : 'bg-gray-50 text-gray-500'}`}>
                  <ChevronDown 
                    className={`w-5 h-5 transition-transform duration-300 ${
                      openIndex === index ? 'rotate-180' : ''
                    }`} 
                  />
                </div>
              </button>
              <div 
                className={`px-6 overflow-hidden transition-all duration-300 ease-in-out bg-gray-50/50 ${
                  openIndex === index ? 'max-h-40 py-5 opacity-100 border-t border-gray-100' : 'max-h-0 opacity-0'
                }`}
              >
                <p className="text-gray-600 leading-relaxed font-sans">
                  {faq.answer}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
