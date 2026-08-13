export default function StatCard({ title, value, subtitle, icon, trend, trendValue }) {
  const trendColor = trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-rose-400' : 'text-gray-400';
  const trendArrow = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '';

  return (
    <div className="bg-card backdrop-blur-md rounded-2xl shadow-lg border border-cardBorder p-6 hover:border-cyan-500/40 hover:shadow-[0_0_20px_rgba(6,182,212,0.15)] transition-all duration-300 animate-fade-in group">
      <div className="flex items-start gap-4">
        {icon && (
          <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-400 truncate">{title}</p>
          <div className="flex items-baseline gap-2 mt-1">
            <p className="text-3xl font-bold text-gray-100 tracking-tight">{value}</p>
            {trendValue && (
              <span className={`text-sm font-medium ${trendColor}`}>
                {trendArrow} {trendValue}
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
      </div>
    </div>
  );
}
