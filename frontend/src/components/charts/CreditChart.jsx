import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const CreditChart = ({ data }) => {
  const chartData = data && data.length > 0 ? data : [
    { day: 'Mon', earned: 45, spent: 20 },
    { day: 'Tue', earned: 80, spent: 35 },
    { day: 'Wed', earned: 60, spent: 50 },
    { day: 'Thu', earned: 120, spent: 70 },
    { day: 'Fri', earned: 95, spent: 40 },
    { day: 'Sat', earned: 140, spent: 60 },
  ];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
          <YAxis stroke="#64748b" fontSize={12} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, color: '#f8fafc' }}
          />
          <Bar dataKey="earned" fill="#10b981" name="Earned" radius={[4, 4, 0, 0]} />
          <Bar dataKey="spent" fill="#ef4444" name="Spent" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
