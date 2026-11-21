'use client';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className = '',
  ...props
}) {
  const baseClasses = 'inline-flex items-center justify-center gap-2 rounded-xl font-semibold tracking-[0.01em] transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#080d16] active:scale-[0.98]';

  const variantClasses = {
    primary: 'border border-cyan-200/20 bg-gradient-to-br from-cyan-400 to-sky-600 text-slate-950 shadow-[0_8px_24px_rgba(8,145,178,0.2)] hover:brightness-110 hover:shadow-[0_10px_30px_rgba(8,145,178,0.28)] focus:ring-cyan-300',
    secondary: 'border border-white/10 bg-white/[0.045] text-gray-200 shadow-sm hover:border-cyan-300/20 hover:bg-white/[0.08] hover:text-white focus:ring-cyan-400/50',
    danger: 'border border-rose-300/15 bg-rose-500/90 text-white shadow-sm hover:bg-rose-400 focus:ring-rose-400',
    ghost: 'border border-transparent bg-transparent text-gray-300 hover:border-white/[0.07] hover:bg-white/[0.045] hover:text-white focus:ring-gray-500',
  };

  const sizeClasses = {
    sm: 'text-sm px-3 py-1.5',
    md: 'text-sm px-4 py-2.5',
    lg: 'text-base px-6 py-3',
  };

  const isDisabled = disabled || loading;

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant] || variantClasses.primary} ${sizeClasses[size] || sizeClasses.md} ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      disabled={isDisabled}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      )}
      {children}
    </button>
  );
}
