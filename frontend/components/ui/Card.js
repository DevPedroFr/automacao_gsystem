export default function Card({ children, className = '', padding = 'p-6', hoverEffect = true }) {
  return (
    <div className={`
      relative
      bg-card backdrop-blur-xl 
      rounded-2xl shadow-xl 
      border border-cardBorder 
      ${hoverEffect ? 'hover:border-cyan-500/40 hover:shadow-[0_8px_32px_rgba(6,182,212,0.15)] hover:-translate-y-1' : ''}
      transition-all duration-500 ease-out
      ${padding} ${className}
    `}>
      {/* Subtle inner highlight for 3D effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.04] to-transparent pointer-events-none rounded-2xl" />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
