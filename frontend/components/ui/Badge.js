const variants = {
  success: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  warning: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  danger: 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
  info: 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30',
  default: 'bg-gray-800/80 text-gray-300 border border-gray-700/50',
};

export default function Badge({ children, variant = 'default', size = 'sm' }) {
  const sizeClass = size === 'sm' ? 'text-xs px-2.5 py-0.5' : 'text-sm px-3.5 py-1';
  return (
    <span className={`inline-flex items-center rounded-full font-semibold tracking-wide ${variants[variant] || variants.default} ${sizeClass}`}>
      {children}
    </span>
  );
}
