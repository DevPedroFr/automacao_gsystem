import Card from './Card';

export default function StatCard({ title, value, subtitle, icon, trend, trendValue }) {
  const trendColor = trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-rose-400' : 'text-gray-400';
  const trendArrow = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '';

  return (
    <Card className="group animate-fade-in" padding="p-5 sm:p-6">
      <div className="flex items-start gap-4">
        {icon && (
          <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border border-cyan-300/15 bg-gradient-to-br from-cyan-300/[0.12] to-indigo-400/[0.06] text-cyan-200 shadow-[inset_0_1px_0_rgba(255,255,255,0.07)] transition-all duration-300 group-hover:border-cyan-200/30 group-hover:text-white">
            {icon}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="truncate text-xs font-medium uppercase tracking-[0.1em] text-gray-500">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <p className="text-3xl font-semibold tracking-tight text-gray-100">{value}</p>
            {trendValue && (
              <span className={`text-sm font-semibold tracking-wide ${trendColor}`}>
                {trendArrow} {trendValue}
              </span>
            )}
          </div>
          {subtitle && <p className="mt-1.5 text-xs font-medium text-gray-500">{subtitle}</p>}
        </div>
      </div>
    </Card>
  );
}
