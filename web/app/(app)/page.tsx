'use client';

/**
 * app/(app)/page.tsx — Home / Dashboard
 * Layout order: header -> hero index card with signal chips -> watchlist
 * (sparkline cards for a few tickers) -> scrolling news ticker, placed
 * mid-screen, between the watchlist and the detailed per-ticker view ->
 * selector tabs + metrics + charts + explain button for whichever ticker
 * is selected (doc's Screen 1 spec, kept from the previous build).
 */
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useTheme } from '@/lib/ThemeContext';
import { api, Stock, Signal, Price, MarketSnapshot, ApiError } from '@/lib/api';
import { BellIcon, MoonIcon, SunIcon, hexForSignal, bgForSignal } from '@/components/Icons';
import { PriceChart, RsiChart } from '@/components/Charts';
import { MetricCard } from '@/components/MetricCard';
import { WatchlistCard } from '@/components/WatchlistCard';
import { NewsTicker } from '@/components/NewsTicker';

const WATCHLIST_SIZE = 4;

export default function HomePage() {
  const { isDark, toggleTheme } = useTheme();

  const [stocks, setStocks] = useState<Stock[]>([]);
  const [allSignals, setAllSignals] = useState<Signal[]>([]);
  const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
  const [watchlistSparklines, setWatchlistSparklines] = useState<Record<string, number[]>>({});

  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [signal, setSignal] = useState<Signal | null>(null);
  const [prices, setPrices] = useState<Price[]>([]);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    Promise.all([api.getStocks(), api.getAllSignals(), api.getMarketSnapshot()])
      .then(async ([stocksRes, signalsRes, snapshotRes]) => {
        if (cancelled) return;
        setStocks(stocksRes);
        setAllSignals(signalsRes);
        setSnapshot(snapshotRes);

        // Support deep-linking from /tickers ("See all") — if the URL has
        // ?ticker=X and it's a real ticker, select that one instead of
        // always defaulting to the first stock in the list.
        const requested = new URLSearchParams(window.location.search).get('ticker');
        const isValidRequested = requested && stocksRes.some((s) => s.ticker === requested);
        setSelectedTicker(isValidRequested ? requested : stocksRes[0]?.ticker ?? null);

        const watchlistTickers = signalsRes.slice(0, WATCHLIST_SIZE).map((s) => s.ticker);
        const sparklineEntries = await Promise.all(
          watchlistTickers.map(async (ticker) => {
            try {
              const p = await api.getPrices(ticker, 14);
              return [ticker, p.slice().reverse().map((price) => parseFloat(price.close))] as const;
            } catch {
              return [ticker, []] as const;
            }
          })
        );
        if (!cancelled) setWatchlistSparklines(Object.fromEntries(sparklineEntries));
      })
      .catch((e) => setError(e instanceof ApiError ? e.message : 'Could not load market data.'));

    return () => {
      cancelled = true;
    };
  }, []);

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
  const watchlistSignals = allSignals.slice(0, WATCHLIST_SIZE);

  return (
    <div className="px-4 pt-4 md:pt-0">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl md:text-[28px] font-semibold">Dashboard</h1>
        <div className="flex items-center gap-2">
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

      {snapshot && (
        <div className="bg-[#F5F6FA] dark:bg-[#12211A] border border-[#EFEFF2] dark:border-[#17251C] rounded-3xl p-5 mb-6">
          <p className="text-xs text-[#8A8FA3] dark:text-[#8FA396] mb-1">NGX All-Share Index</p>
          <div className="flex items-baseline gap-2 mb-4">
            <span className="font-display text-[#0A2233] dark:text-white text-[26px]">
              {snapshot.all_share_index.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
            <span className={`text-xs font-semibold ${snapshot.asi_change_percent >= 0 ? 'text-signal-bullish' : 'text-signal-bearish'}`}>
              {snapshot.asi_change_percent >= 0 ? '▲' : '▼'} {Math.abs(snapshot.asi_change_percent)}%
            </span>
          </div>
          <div className="flex gap-2 overflow-x-auto no-scrollbar">
            {allSignals.slice(0, 5).map((s) => (
              <span
                key={s.ticker}
                className={`shrink-0 bg-white dark:bg-[#0A2818] text-[11px] font-medium px-3 py-1.5 rounded-full whitespace-nowrap border border-[#EFEFF2] dark:border-[#17251C] ${
                  s.change_pct >= 0 ? 'text-signal-bullish' : 'text-signal-bearish'
                }`}
              >
                {s.ticker} {s.change_pct >= 0 ? '+' : ''}
                {s.change_pct}%
              </span>
            ))}
          </div>
        </div>
      )}

      {watchlistSignals.length > 0 && (
        <>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold">Watchlist</h2>
            <Link href="/tickers" className="text-xs text-brand-primary dark:text-brand-accent font-medium">
              See all
            </Link>
          </div>
          <div className="flex gap-3 overflow-x-auto no-scrollbar mb-6 -mx-4 px-4 md:mx-0 md:px-0">
            {watchlistSignals.map((s) => (
              <WatchlistCard
                key={s.ticker}
                ticker={s.ticker}
                price={parseFloat(s.close).toLocaleString()}
                changePct={s.change_pct}
                sparkline={watchlistSparklines[s.ticker] ?? []}
                color={hexForSignal(s.signal)}
                active={selectedTicker === s.ticker}
                onClick={() => setSelectedTicker(s.ticker)}
              />
            ))}
          </div>
        </>
      )}

      <NewsTicker />

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

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <MetricCard label="Close" value={`₦${parseFloat(signal.close).toLocaleString()}`} />
            <MetricCard label="MA7" value={signal.ma7 ? `₦${parseFloat(signal.ma7).toLocaleString()}` : '—'} />
            <MetricCard label="MA30" value={signal.ma30 ? `₦${parseFloat(signal.ma30).toLocaleString()}` : '—'} />
            <MetricCard label="RSI" value={signal.rsi.toFixed(1)} />
          </div>

          <p className="text-sm text-[#8A8FA3] dark:text-[#8FA396] leading-relaxed mb-6">{signal.signal_reason}</p>

          <div className="bg-[#FAFBFC] dark:bg-[#0A2818] border border-[#EFEFF2] dark:border-[#17251C] rounded-2xl p-4 mb-4">
            <p className="text-sm font-semibold mb-2">Price · MA7 · MA30</p>
            <PriceChart data={chartData} />
          </div>

          <div className="bg-[#FAFBFC] dark:bg-[#0A2818] border border-[#EFEFF2] dark:border-[#17251C] rounded-2xl p-4 mb-6">
            <p className="text-sm font-semibold mb-2">RSI (14)</p>
            <RsiChart data={rsiData} />
          </div>

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
