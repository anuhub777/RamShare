import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const ResourceChart = ({ data }) => {
  const chartData = data && data.length > 0 ? data : [
    { time: '10:00', cpu: 25, ram: 40 },
    { time: '10:10', cpu: 45, ram: 50 },
    { time: '10:20', cpu: 30, ram: 45 },
    { time: '10:30', cpu: 65, ram: 70 },
    { time: '10:40', cpu: 40, ram: 60 },
    { time: '10:50', cpu: 55, ram: 65 },
  ];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="ramGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="time" stroke="#64748b" fontSize={12} />
          <YAxis stroke="#64748b" fontSize={12} unit="%" />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, color: '#f8fafc' }}
          />
          <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#cpuGradient)" name="CPU Usage %" />
          <Area type="monotone" dataKey="ram" stroke="#06b6d4" fillOpacity={1} fill="url(#ramGradient)" name="RAM Usage %" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
