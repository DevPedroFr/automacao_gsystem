export default function About() {
  return (
    <section className="py-24 bg-[var(--color-navy-deep)] relative overflow-hidden">
      {/* Decorative Gold Accent */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[200px] h-1 bg-[var(--color-gold)]"></div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-4xl mx-auto p-8 sm:p-12 lg:p-16 text-center">
          <h2 className="text-3xl sm:text-4xl font-serif text-white mb-8 leading-tight">
            Orientação jurídica com clareza, responsabilidade e proximidade
          </h2>
          <div className="h-0.5 w-16 bg-[var(--color-gold)] mx-auto mb-8"></div>
          <p className="text-lg text-gray-300 leading-relaxed font-sans max-w-3xl mx-auto">
            A Mota Tobias Advocacia atua com foco em oferecer orientação jurídica clara, atendimento humanizado e análise responsável de cada situação. A página apresenta uma visão institucional do escritório, destacando sua reputação local e sua atuação em demandas trabalhistas.
          </p>
        </div>
      </div>
    </section>
  );
}
