'use client';

/**
 * app/page.tsx — Home / Dashboard
 * Matches the handoff doc's actual Screen 1 spec: a stock selector, signal
 * badge, four metric cards, price chart with MA overlay, RSI chart, and an
 * Explain button — per ticker, not the index-wide view (that's /market).
 */
import { useEffect, useState } from 'react';
import { useTheme } from '@/lib/ThemeContext';
import { api, Stock, Signal, Price, ApiError } from '@/lib/api';
import { BellIcon, MoonIcon, SunIcon, colorForSignal, bgForSignal } from '@/components/Icons';
import { PriceChart, RsiChart } from '@/components/Charts';
import { MetricCard } from '@/components/MetricCard';

export default function HomePage() {
  const { isDark, toggleTheme } = useTheme();

  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [signal, setSignal] = useState<Signal | null>(null);
  const [prices, setPrices] = useState<Price[]>([]);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load the stock list once, select the first ticker by default.
  useEffect(() => {
    api
      .getStocks()
      .then((data) => {
        setStocks(data);
        if (data.length > 0) setSelectedTicker(data[0].ticker);
      })
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load stocks.'));
  }, []);

  // Load signal + prices whenever the selected ticker changes.
  useEffect(() => {
    if (!selectedTicker) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    setExplanation(null);

    Promise.all([api.getSignal(selectedTicker), api.getPrices(selectedTicker, 30)])
      .then(([signalRes, pricesRes]) => {
        if (cancelled) return;
        setSignal(signalRes);
        setPrices(pricesRes);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(
          e instanceof ApiError
            ? e.message
            : 'Could not reach the server. If this is the first request in a while, it may be waking up.'
        );
      })
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [selectedTicker]);

  async function handleExplain() {
    if (!selectedTicker) return;
    setExplaining(true);
    try {
      const res = await api.explainSignal(selectedTicker);
      setExplanation(res.explanation);
    } catch (e) {
      setExplanation(e instanceof ApiError ? `Could not generate explanation: ${e.message}` : 'Could not generate explanation.');
    } finally {
      setExplaining(false);
    }
  }

  const chartData = prices
    .slice()
    .reverse()
    .map((p) => ({
      date: p.date.slice(5),
      close: parseFloat(p.close),
      ma7: signal?.ma7 ? parseFloat(signal.ma7) : undefined,
      ma30: signal?.ma30 ? parseFloat(signal.ma30) : undefined,
    }));

  const rsiData = chartData.map((d) => ({ date: d.date, rsi: signal?.rsi ?? 50 }));

  return (
    <div className="px-4 pt-4 md:pt-0">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl md:text-[28px] font-semibold">Dashboard</h1>
        <div className="flex items-center gap-2">
          {/* Theme toggle — parked for v1, dark-only */}
          {false && (
            <button
              onClick={toggleTheme}
              aria-label="Toggle dark mode"
              className="w-8 h-8 rounded-full bg-[#F2F2F7] dark:bg-[#12211A] flex items-center justify-center hover:opacity-70 transition-opacity"
            >
              {isDark ? <SunIcon /> : <MoonIcon />}
            </button>
          )}
          <button
            aria-label="Notifications"
            className="w-8 h-8 rounded-full bg-[#F2F2F7] dark:bg-[#12211A] flex items-center justify-center hover:opacity-70 transition-opacity"
          >
            <BellIcon />
          </button>
        </div>
      </div>

      {/* Stock selector */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-5 -mx-4 px-4 md:mx-0 md:px-0 no-scrollbar">
        {stocks.map((stock) => (
          <button
            key={stock.ticker}
            onClick={() => setSelectedTicker(stock.ticker)}
            className={`shrink-0 px-3.5 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
              selectedTicker === stock.ticker
                ? 'bg-[#0A2233] dark:bg-brand-primary text-white'
                : 'bg-[#F5F6FA] dark:bg-[#0A2818] text-[#8A8FA3] dark:text-[#8FA396]'
            }`}
          >
            {stock.ticker}
          </button>
        ))}
      </div>

      {loading && <p className="text-sm text-[#8A8FA3] dark:text-[#8FA396]">Loading…</p>}
      {error && <p className="text-sm text-signal-bearish">{error}</p>}

      {signal && !loading && (
        <>
          {/* Price + signal badge */}
          <div className="flex items-start justify-between mb-5">
            <div>
              <p className="text-xs text-[#8A8FA3] dark:text-[#8FA396]">{selectedTicker}</p>
              <p className="font-display text-3xl">₦{parseFloat(signal.close).toLocaleString()}</p>
              <p className={`text-sm font-medium ${signal.change_pct >= 0 ? 'text-signal-bullish' : 'text-signal-bearish'}`}>
                {signal.change_pct >= 0 ? '+' : ''}
                {signal.change_pct}%
              </p>
            </div>
            <span className={`text-xs font-semibold px-3 py-1.5 rounded-full text-white ${bgForSignal(signal.signal)}`}>
              {signal.signal.toUpperCase()}
            </span>
          </div>

          {/* Metric cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <MetricCard label="Close" value={`₦${parseFloat(signal.close).toLocaleString()}`} />
            <MetricCard label="MA7" value={signal.ma7 ? `₦${parseFloat(signal.ma7).toLocaleString()}` : '—'} />
            <MetricCard label="MA30" value={signal.ma30 ? `₦${parseFloat(signal.ma30).toLocaleString()}` : '—'} />
            <MetricCard label="RSI" value={signal.rsi.toFixed(1)} />
          </div>

          {/* Signal reason */}
          <p className="text-sm text-[#8A8FA3] dark:text-[#8FA396] leading-relaxed mb-6">{signal.signal_reason}</p>

          {/* Price chart */}
          <div className="bg-[#FAFBFC] dark:bg-[#0A2818] border border-[#EFEFF2] dark:border-[#17251C] rounded-2xl p-4 mb-4">
            <p className="text-sm font-semibold mb-2">Price · MA7 · MA30</p>
            <PriceChart data={chartData} />
          </div>

          {/* RSI chart */}
          <div className="bg-[#FAFBFC] dark:bg-[#0A2818] border border-[#EFEFF2] dark:border-[#17251C] rounded-2xl p-4 mb-6">
            <p className="text-sm font-semibold mb-2">RSI (14)</p>
            <RsiChart data={rsiData} />
          </div>

          {/* Explain button */}
          <button
            onClick={handleExplain}
            disabled={explaining}
            className="w-full bg-[#0A2233] dark:bg-brand-primary text-white rounded-full py-3.5 text-sm font-medium disabled:opacity-60 mb-6"
          >
            {explaining ? 'Generating explanation…' : 'Explain this signal'}
          </button>

          {explanation && (
            <div className="bg-[#F5F6FA] dark:bg-[#12211A] rounded-2xl p-4 mb-8">
              <p className="text-sm leading-relaxed">{explanation}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}