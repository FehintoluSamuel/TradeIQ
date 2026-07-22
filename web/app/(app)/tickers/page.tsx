'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, Signal, ApiError } from '@/lib/api';
import { TickerLogo } from '@/components/TickerLogo';

export default function AllTickersPage() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    api
      .getAllSignals()
      .then(setSignals)
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load tickers.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="px-4 pt-4 md:pt-0">
      <h1 className="text-2xl md:text-[28px] font-semibold mb-6">All Stocks</h1>

      {loading && <p className="text-sm text-[#8A8FA3] dark:text-[#8FA396]">Loading…</p>}
      {error && <p className="text-sm text-signal-bearish">{error}</p>}

      <div className="flex flex-col divide-y divide-[#EFEFF2] dark:divide-[#17251C]">
        {signals.map((s) => (
          <button
            key={s.ticker}
            onClick={() => router.push(`/?ticker=${s.ticker}`)}
            className="flex items-center justify-between py-3.5 text-left hover:opacity-70 transition-opacity"
          >
            <div className="flex items-center gap-3">
              <TickerLogo ticker={s.ticker} size={38} />
              <div>
                <p className="text-sm font-semibold">{s.ticker}</p>
                <p className="text-xs text-[#8A8FA3] dark:text-[#8FA396] max-w-[220px] truncate">
                  {s.signal_reason}
                </p>
              </div>
            </div>
            <div className="text-right shrink-0 pl-3">
              <p className="text-sm font-semibold">₦{parseFloat(s.close).toLocaleString()}</p>
              <p className={`text-xs font-medium ${s.change_pct >= 0 ? 'text-signal-bullish' : 'text-signal-bearish'}`}>
                {s.change_pct >= 0 ? '+' : ''}
                {s.change_pct}%
              </p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
