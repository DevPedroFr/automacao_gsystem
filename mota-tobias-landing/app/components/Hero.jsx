import { Star, MessageCircle, ArrowRight, Scale } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative bg-[var(--color-navy-deep)] pt-16 pb-24 lg:pt-32 lg:pb-40 text-white overflow-hidden">
      {/* Subtle abstract background element */}
      <div className="absolute top-0 right-0 -translate-y-12 translate-x-1/3 opacity-10">
        <Scale className="w-[800px] h-[800px] text-white" />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-8 items-center">
          {/* Left Column: Text and CTAs */}
          <div className="max-w-2xl">
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 backdrop-blur-sm">
              <div className="flex gap-1 text-[var(--color-gold)]">
                <Star className="h-4 w-4 fill-current" />
                <Star className="h-4 w-4 fill-current" />
                <Star className="h-4 w-4 fill-current" />
                <Star className="h-4 w-4 fill-current" />
                <Star className="h-4 w-4 fill-current" />
              </div>
              <span className="text-sm font-medium text-white/90">
                5.0 no Google com mais de 170 avaliações
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl mb-6 leading-tight font-serif">
              Advocacia trabalhista em <span className="text-[var(--color-gold)]">Mogi das Cruzes</span>
            </h1>
            
            <p className="text-lg sm:text-xl leading-8 text-gray-300 mb-10 font-sans">
              Atendimento claro, estratégico e responsável para orientar trabalhadores e empresas em demandas trabalhistas.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6">
              <a
                href="#"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full bg-[var(--color-gold)] px-8 py-4 text-base font-semibold text-white shadow-lg hover:bg-[var(--color-gold-hover)] hover:-translate-y-1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 transition-all duration-300"
              >
                <MessageCircle className="w-5 h-5" />
                Solicitar orientação
              </a>
              <a
                href="#atuacao"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full border border-white/30 bg-transparent px-8 py-4 text-base font-semibold text-white hover:bg-white/10 transition-all duration-300"
              >
                Conhecer áreas
                <ArrowRight className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Right Column: Visual Institutional Card */}
          <div className="hidden lg:flex justify-end">
            <div className="w-full max-w-md rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md p-8 shadow-2xl relative">
              <div className="absolute -top-4 -left-4 w-24 h-24 bg-[var(--color-gold)] rounded-full blur-3xl opacity-20"></div>
              <h3 className="text-2xl font-serif mb-4 text-white">Compromisso com o Direito</h3>
              <p className="text-gray-300 leading-relaxed mb-6">
                Nossa atuação é pautada na transparência e no estudo aprofundado de cada caso. 
                Avaliamos cada demanda trabalhista de forma individualizada, buscando sempre o 
                caminho mais estratégico e seguro para a proteção dos seus direitos.
              </p>
              <div className="h-1 w-20 bg-[var(--color-gold)] rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
