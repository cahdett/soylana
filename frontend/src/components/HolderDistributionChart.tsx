import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import type { HolderCategories } from '../types';

interface HolderDistributionChartProps {
  categories: HolderCategories;
}

const COLORS = {
  whale: '#a855f7',    // purple
  dolphin: '#3b82f6',  // blue
  fish: '#06b6d4',     // cyan
  crab: '#10b981',     // green
  shrimp: '#f59e0b',   // yellow
};

export function HolderDistributionChart({ categories }: HolderDistributionChartProps) {
  const data = [
    { name: 'Whale', value: categories.whale, color: COLORS.whale },
    { name: 'Dolphin', value: categories.dolphin, color: COLORS.dolphin },
    { name: 'Fish', value: categories.fish, color: COLORS.fish },
    { name: 'Crab', value: categories.crab, color: COLORS.crab },
    { name: 'Shrimp', value: categories.shrimp, color: COLORS.shrimp },
  ];

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Holder Distribution</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
              }}
              formatter={(value) => [typeof value === 'number' ? value.toLocaleString() : '0', 'Holders']}
            />
            <Legend
              formatter={(value) => <span className="text-gray-300">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
