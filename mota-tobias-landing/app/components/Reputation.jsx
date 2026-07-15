import { Star, Users, MapPin } from 'lucide-react';

export default function Reputation() {
  return (
    <section className="py-24 bg-white relative -mt-10 rounded-t-[3rem] z-20 shadow-xl border-t border-gray-100">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-serif text-[var(--color-navy)] mb-6">
            Reconhecimento local construído com confiança
          </h2>
          <p className="text-lg text-gray-600 leading-relaxed font-sans">
            A Mota Tobias Advocacia possui forte presença local em Mogi das Cruzes, com avaliação 5.0 no Google e mais de 170 avaliações, reforçando a confiança de clientes que buscaram orientação jurídica.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-5xl mx-auto">
          <div className="rounded-2xl bg-white border border-gray-100 p-8 flex flex-col items-center text-center shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="flex gap-1 text-[var(--color-gold)] mb-5">
              <Star className="h-8 w-8 fill-current" />
            </div>
            <p className="text-[var(--color-navy)] font-semibold text-lg font-sans">5.0 no Google</p>
          </div>
          
          <div className="rounded-2xl bg-white border border-gray-100 p-8 flex flex-col items-center text-center shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="text-[var(--color-navy)] mb-5">
              <Users className="h-10 w-10" />
            </div>
            <p className="text-[var(--color-navy)] font-semibold text-lg font-sans">Mais de 170 avaliações</p>
          </div>
          
          <div className="rounded-2xl bg-white border border-gray-100 p-8 flex flex-col items-center text-center shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="text-[var(--color-navy)] mb-5">
              <MapPin className="h-10 w-10" />
            </div>
            <p className="text-[var(--color-navy)] font-semibold text-lg font-sans">Mogi das Cruzes e região</p>
          </div>
        </div>
      </div>
    </section>
  );
}
