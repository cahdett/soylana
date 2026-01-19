import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { HolderBreakdowns } from '../types';

interface ValueBreakdownChartProps {
  breakdowns: HolderBreakdowns;
}

export function ValueBreakdownChart({ breakdowns }: ValueBreakdownChartProps) {
  const data = [
    { name: '>$10', value: breakdowns.holders_over_10_usd },
    { name: '>$100', value: breakdowns.holders_over_100_usd },
    { name: '>$1K', value: breakdowns.holders_over_1000_usd },
    { name: '>$10K', value: breakdowns.holders_over_10000_usd },
    { name: '>$100K', value: breakdowns.holders_over_100k_usd },
    { name: '>$1M', value: breakdowns.holders_over_1m_usd },
  ];

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Holders by Value</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
            <YAxis stroke="#9ca3af" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
              }}
              formatter={(value) => [typeof value === 'number' ? value.toLocaleString() : '0', 'Holders']}
            />
            <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
