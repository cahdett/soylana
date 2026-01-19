interface StatCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export function StatCard({ label, value, subValue, trend, className = '' }: StatCardProps) {
  const trendColor = trend === 'up'
    ? 'text-green-400'
    : trend === 'down'
    ? 'text-red-400'
    : 'text-gray-400';

  return (
    <div className={`bg-gray-800 rounded-lg border border-gray-700 p-4 flex flex-col ${className}`}>
      <span className="text-sm text-gray-400">{label}</span>
      <span className="text-2xl font-bold text-white">{value}</span>
      {subValue && (
        <span className={`text-sm ${trendColor}`}>{subValue}</span>
      )}
    </div>
  );
}
