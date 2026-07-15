'use client';

export default function LeadFilters({ onFilterChange, onSearchChange, searchValue = '', priorityFilter = '' }) {
  const priorities = [
    { key: '', label: 'Todos' },
    { key: 'A', label: 'A', color: 'bg-green-500' },
    { key: 'B', label: 'B', color: 'bg-yellow-500' },
    { key: 'C', label: 'C', color: 'bg-red-500' },
  ];

  return (
    <div className="flex flex-wrap items-center gap-4">
      {/* Search */}
      <div className="relative flex-1 min-w-[240px]">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          value={searchValue}
          onChange={(e) => onSearchChange?.(e.target.value)}
          placeholder="Buscar leads por nome..."
          className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-colors outline-none"
        />
      </div>

      {/* Priority filter */}
      <div className="flex items-center gap-1.5">
        <span className="text-xs font-medium text-gray-500 mr-1">Prioridade:</span>
        {priorities.map((p) => (
          <button
            key={p.key}
            onClick={() => onFilterChange?.(p.key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
              priorityFilter === p.key
                ? p.color
                  ? `${p.color} text-white shadow-sm`
                  : 'bg-gray-800 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>
  );
}
