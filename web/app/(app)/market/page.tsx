'use client';

import { useEffect, useState } from 'react';
import { api, MarketSnapshot, ApiError } from '@/lib/api';
import { IndexChart } from '@/components/Charts';
import { MetricCard } from '@/components/MetricCard';

const MOCK_TREND = [102400, 102100, 102800, 103200, 103000, 103900, 104200, 104982];

export default function MarketPage() {
  const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getMarketSnapshot()
      .then(setSnapshot)
      .catch((e) =>
        setError(
          e instanceof ApiError
            ? e.message
            : 'Could not reach the server. If this is the first request in a while, it may be waking up.'
        )
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="px-4 pt-6 text-sm text-[#8A8FA3] dark:text-[#8FA396]">Loading market data…</p>;
  if (error) return <p className="px-4 pt-6 text-sm text-signal-bearish">{error}</p>;
  if (!snapshot) return null;

  const positive = snapshot.asi_change_percent >= 0;

  return (
    <div className="px-4 pt-4 md:pt-0">
      <h1 className="text-2xl md:text-[28px] font-semibold mb-1">Market overview</h1>
      <p className="text-sm text-[#8A8FA3] dark:text-[#8FA396] mb-6">
        {new Date(snapshot.date).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}
      </p>

      <div className="bg-[#D1FAE5] dark:bg-gradient-to-br dark:from-brand-primary dark:to-brand-forest rounded-2xl p-4 mb-6">
        <p className="text-xs text-[#0F5C2E] dark:text-[#8FEFB4] mb-1">NGX All-Share Index</p>
        <div className="flex items-baseline gap-2 mb-3">
          <span className="font-display text-3xl text-[#0A2818] dark:text-white">
            {snapshot.all_share_index.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
          <span className={`text-sm font-semibold ${positive ? 'text-[#0F5C2E] dark:text-[#8FEFB4]' : 'text-signal-bearish'}`}>
            {positive ? '▲' : '▼'} {Math.abs(snapshot.asi_change_percent)}%
          </span>
        </div>
        <IndexChart data={MOCK_TREND} />
        <div className="flex gap-4 mt-3">
          <span className="text-xs font-medium text-[#0F5C2E] dark:text-[#8FEFB4]">▲ {snapshot.breadth.advancers} advancers</span>
          <span className="text-xs font-medium text-signal-bearish">▼ {snapshot.breadth.decliners} decliners</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-6">
        <MetricCard label="Total market cap" value={`₦${(snapshot.market_cap.total / 1e12).toFixed(2)}T`} />
        <MetricCard label="Volume traded" value={snapshot.volume.toLocaleString()} />
      </div>
    </div>
  );
}
