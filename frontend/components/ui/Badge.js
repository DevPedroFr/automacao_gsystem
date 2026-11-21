const variants = {
  success: 'border border-emerald-300/15 bg-emerald-400/[0.09] text-emerald-300',
  warning: 'border border-amber-300/15 bg-amber-400/[0.09] text-amber-200',
  danger: 'border border-rose-300/15 bg-rose-400/[0.09] text-rose-300',
  info: 'border border-cyan-300/15 bg-cyan-400/[0.08] text-cyan-200',
  default: 'border border-white/[0.09] bg-white/[0.045] text-gray-300',
};

export default function Badge({ children, variant = 'default', size = 'sm' }) {
  const sizeClass = size === 'sm' ? 'px-2.5 py-1 text-[10px]' : 'px-3 py-1.5 text-xs';
  return (
    <span className={`inline-flex items-center rounded-full font-semibold uppercase tracking-[0.08em] backdrop-blur-sm ${variants[variant] || variants.default} ${sizeClass}`}>
      {children}
    </span>
  );
}
