import { MessageCircle } from 'lucide-react';

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full bg-[var(--color-navy)] text-white shadow-md">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-20 items-center justify-between">
          <div className="flex-shrink-0">
            <span className="text-2xl font-bold tracking-tight uppercase tracking-wider font-serif">
              Mota Tobias<span className="text-[var(--color-gold)]">.</span>
            </span>
          </div>
          <div className="flex items-center">
            <a
              href="#"
              className="inline-flex items-center justify-center gap-2 rounded-full bg-[var(--color-gold)] px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-[var(--color-gold-hover)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 transition-all duration-300"
            >
              <MessageCircle className="w-4 h-4" />
              Falar com advogado
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
