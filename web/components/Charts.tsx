'use client';

import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, ReferenceLine } from 'recharts';

export function PriceChart({ data }: { data: { date: string; close: number; ma7?: number; ma30?: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="currentColor" opacity={0.4} />
        <YAxis tick={{ fontSize: 10 }} stroke="currentColor" opacity={0.4} width={48} />
        <Line type="monotone" dataKey="close" stroke="#22C55E" strokeWidth={2} dot={false} name="Price" />
        <Line type="monotone" dataKey="ma7" stroke="#F59E0B" strokeWidth={1.5} dot={false} name="MA7" strokeDasharray="4 2" />
        <Line type="monotone" dataKey="ma30" stroke="#60A5FA" strokeWidth={1.5} dot={false} name="MA30" strokeDasharray="4 2" />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function RsiChart({ data }: { data: { date: string; rsi: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={140}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="currentColor" opacity={0.4} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} stroke="currentColor" opacity={0.4} width={32} />
        <ReferenceLine y={70} stroke="#DC2626" strokeDasharray="3 3" opacity={0.5} />
        <ReferenceLine y={30} stroke="#16A34A" strokeDasharray="3 3" opacity={0.5} />
        <Area type="monotone" dataKey="rsi" stroke="#A78BFA" fill="#A78BFA" fillOpacity={0.15} strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function IndexChart({ data, color = '#0F5C2E' }: { data: number[]; color?: string }) {
  const points = data.map((value, i) => ({ i, value }));
  return (
    <ResponsiveContainer width="100%" height={90}>
      <AreaChart data={points} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="indexFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.2} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area type="monotone" dataKey="value" stroke={color} fill="url(#indexFill)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
