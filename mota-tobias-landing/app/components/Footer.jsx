export default function Footer() {
  return (
    <footer className="bg-[var(--color-navy-deep)] pt-16 pb-8 border-t border-white/5">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-8 mb-12">
          <div>
            <h3 className="text-xl font-bold tracking-tight text-white uppercase tracking-wider mb-4 font-serif">
              Mota Tobias<span className="text-[var(--color-gold)]">.</span>
            </h3>
            <p className="text-gray-400 font-sans">
              Mogi das Cruzes, SP
            </p>
          </div>
          <div className="md:text-right">
            <h4 className="text-sm font-semibold text-[var(--color-gold)] uppercase tracking-wider mb-4 font-sans">
              Aviso Institucional
            </h4>
            <p className="text-sm text-gray-400 leading-relaxed md:ml-auto max-w-sm font-sans border-l-2 md:border-l-0 md:border-r-2 border-[var(--color-gold)]/30 pl-4 md:pl-0 md:pr-4">
              As informações desta página têm caráter exclusivamente informativo e não representam promessa de resultado.
            </p>
          </div>
        </div>
        
        <div className="pt-8 border-t border-white/10 text-center">
          <p className="text-sm text-gray-500 font-sans">
            &copy; {new Date().getFullYear()} Mota Tobias Advocacia. Todos os direitos reservados.
          </p>
        </div>
      </div>
    </footer>
  );
}
