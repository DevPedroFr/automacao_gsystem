import { MessageCircle } from 'lucide-react';

export default function CTA() {
  return (
    <section className="py-24 relative overflow-hidden bg-[var(--color-navy)]">
      {/* Decorative gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-[var(--color-navy-deep)] to-[var(--color-navy)] opacity-90 -z-10" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        <div className="max-w-3xl mx-auto bg-white/5 border border-white/10 rounded-[3rem] p-10 sm:p-16 backdrop-blur-sm shadow-2xl">
          <h2 className="text-3xl sm:text-5xl font-serif text-white mb-6 leading-tight">
            Precisa de orientação jurídica trabalhista?
          </h2>
          <div className="h-1 w-20 bg-[var(--color-gold)] mx-auto mb-8 rounded-full"></div>
          <p className="text-xl text-gray-300 mb-10 leading-relaxed font-sans max-w-2xl mx-auto">
            Entre em contato com o escritório para explicar sua situação e receber uma orientação inicial clara e profissional.
          </p>
          <a
            href="#"
            className="inline-flex items-center justify-center gap-2 rounded-full bg-[var(--color-gold)] px-10 py-5 text-lg font-semibold text-white shadow-xl hover:bg-[var(--color-gold-hover)] hover:-translate-y-1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 transition-all duration-300"
          >
            <MessageCircle className="w-6 h-6" />
            Falar pelo WhatsApp
          </a>
        </div>
      </div>
    </section>
  );
}
