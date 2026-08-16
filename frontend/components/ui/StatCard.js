import Card from './Card';

export default function StatCard({ title, value, subtitle, icon, trend, trendValue }) {
  const trendColor = trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-rose-400' : 'text-gray-400';
  const trendArrow = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '';

  return (
    <Card className="group animate-fade-in" padding="p-6">
      <div className="flex items-start gap-4">
        {icon && (
          <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-110 group-hover:shadow-[0_0_15px_rgba(6,182,212,0.4)] group-hover:border-cyan-400/50 transition-all duration-300">
            {icon}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-400 truncate">{title}</p>
          <div className="flex items-baseline gap-2 mt-2">
            <p className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 tracking-tight drop-shadow-sm">{value}</p>
            {trendValue && (
              <span className={`text-sm font-semibold tracking-wide ${trendColor}`}>
                {trendArrow} {trendValue}
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs text-gray-500 mt-1.5 font-medium tracking-wide">{subtitle}</p>}
        </div>
      </div>
    </Card>
  );
}
