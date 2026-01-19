import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { HolderDeltas } from '../types';

interface HolderDeltasChartProps {
  deltas: HolderDeltas;
}

export function HolderDeltasChart({ deltas }: HolderDeltasChartProps) {
  const data = [
    { name: '1h', value: deltas.hour_1 },
    { name: '2h', value: deltas.hours_2 },
    { name: '4h', value: deltas.hours_4 },
    { name: '12h', value: deltas.hours_12 },
    { name: '1d', value: deltas.day_1 },
    { name: '3d', value: deltas.days_3 },
    { name: '7d', value: deltas.days_7 },
    { name: '14d', value: deltas.days_14 },
    { name: '30d', value: deltas.days_30 },
  ];

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Holder Changes</h3>
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
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.value >= 0 ? '#10b981' : '#ef4444'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
