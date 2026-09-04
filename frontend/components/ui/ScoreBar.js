export default function ScoreBar({ value = 0, label = '', showValue = true }) {
  const clampedValue = Math.max(0, Math.min(100, value));

  const getColor = (val) => {
    if (val < 40) return '#EF4444';
    if (val < 70) return '#F59E0B';
    return '#22C55E';
  };

  const color = getColor(clampedValue);

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-1.5">
          {label && <span className="text-xs font-medium text-gray-400">{label}</span>}
          {showValue && (
            <span className="text-xs font-bold" style={{ color }}>
              {clampedValue}
            </span>
          )}
        </div>
      )}
      <div className="w-full h-2 bg-gray-900/80 border border-gray-700/50 rounded-full overflow-hidden shadow-inner">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${clampedValue}%`,
            backgroundColor: color,
          }}
        />
      </div>
    </div>
  );
}
