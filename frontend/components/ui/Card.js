export default function Card({ children, className = '', padding = 'p-6', hoverEffect = true }) {
  return (
    <div className={`group/card relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[rgba(12,21,34,0.78)] shadow-[0_12px_40px_rgba(0,0,0,0.18)] backdrop-blur-xl ${hoverEffect ? 'transition-all duration-300 hover:-translate-y-0.5 hover:border-cyan-300/20 hover:shadow-[0_18px_48px_rgba(0,0,0,0.28),0_0_24px_rgba(34,211,238,0.05)]' : ''} ${padding} ${className}`}>
      <div className="pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/25 to-transparent" />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/[0.025] via-transparent to-cyan-400/[0.015]" />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
