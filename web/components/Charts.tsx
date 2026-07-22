'use client';

import {
  ComposedChart,
  Area,
  Line,
  AreaChart,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceArea,
  Tooltip,
  TooltipProps,
} from 'recharts';

type PricePoint = { date: string; close: number; ma7?: number; ma30?: number };
type RsiPoint = { date: string; rsi: number };

// Custom tooltip content instead of Recharts' plain default box, so it
// matches the app's own styling and shows exactly what a beginner needs:
// the date, and the price (plus MA7/MA30 if present) at that point.
function PriceTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload || payload.length === 0) return null;
  const point = payload[0].payload as PricePoint;
  return (
    <div className="bg-white dark:bg-[#12211A] border border-[#EFEFF2] dark:border-[#17251C] rounded-lg px-3 py-2 shadow-md">
      <p className="text-[10px] text-[#8A8FA3] dark:text-[#8FA396] mb-1">{label}</p>
      <p className="text-xs font-semibold text-[#0A2233] dark:text-white">₦{point.close?.toLocaleString()}</p>
      {point.ma7 !== undefined && <p className="text-[10px] text-[#B45309]">MA7: ₦{point.ma7.toLocaleString()}</p>}
      {point.ma30 !== undefined && <p className="text-[10px] text-[#1D4ED8]">MA30: ₦{point.ma30.toLocaleString()}</p>}
    </div>
  );
}

function RsiTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload || payload.length === 0) return null;
  const point = payload[0].payload as RsiPoint;
  return (
    <div className="bg-white dark:bg-[#12211A] border border-[#EFEFF2] dark:border-[#17251C] rounded-lg px-3 py-2 shadow-md">
      <p className="text-[10px] text-[#8A8FA3] dark:text-[#8FA396] mb-1">{label}</p>
      <p className="text-xs font-semibold text-[#0A2233] dark:text-white">RSI: {point.rsi.toFixed(1)}</p>
    </div>
  );
}

export function PriceChart({ data }: { data: PricePoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22C55E" stopOpacity={0.28} />
            <stop offset="100%" stopColor="#22C55E" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="currentColor" opacity={0.4} />
        <YAxis tick={{ fontSize: 10 }} stroke="currentColor" opacity={0.4} width={48} />
        <Tooltip content={<PriceTooltip />} cursor={{ stroke: '#0F5C2E', strokeDasharray: '3 3', strokeOpacity: 0.4 }} />
        <Area type="monotone" dataKey="close" stroke="#0F5C2E" strokeWidth={2} fill="url(#priceFill)" name="Price" />
        <Line type="monotone" dataKey="ma7" stroke="#F59E0B" strokeWidth={1.5} dot={false} name="MA7" strokeDasharray="4 2" />
        <Line type="monotone" dataKey="ma30" stroke="#60A5FA" strokeWidth={1.5} dot={false} name="MA30" strokeDasharray="4 2" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function RsiChart({ data }: { data: RsiPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={140}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="currentColor" opacity={0.4} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} stroke="currentColor" opacity={0.4} width={32} />
        <ReferenceArea y1={70} y2={100} fill="#DC2626" fillOpacity={0.08} strokeOpacity={0} />
        <ReferenceArea y1={0} y2={30} fill="#16A34A" fillOpacity={0.08} strokeOpacity={0} />
        <Tooltip content={<RsiTooltip />} cursor={{ stroke: '#A78BFA', strokeDasharray: '3 3', strokeOpacity: 0.4 }} />
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
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload || payload.length === 0) return null;
            return (
              <div className="bg-white dark:bg-[#12211A] border border-[#EFEFF2] dark:border-[#17251C] rounded-lg px-2.5 py-1.5 shadow-md">
                <p className="text-[11px] font-semibold text-[#0A2233] dark:text-white">
                  {(payload[0].value as number).toLocaleString()}
                </p>
              </div>
            );
          }}
        />
        <Area type="monotone" dataKey="value" stroke={color} fill="url(#indexFill)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}