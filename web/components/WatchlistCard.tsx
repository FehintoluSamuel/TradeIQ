import { MiniSparkline } from './MiniSparkline';

export function WatchlistCard({
  ticker,
  price,
  changePct,
  sparkline,
  color,
  onClick,
  active,
}: {
  ticker: string;
  price: string;
  changePct: number;
  sparkline: number[];
  color: string;
  onClick: () => void;
  active: boolean;
}) {
  const positive = changePct >= 0;
  return (
    <button
      onClick={onClick}
      className={`text-left bg-[#F5F6FA] dark:bg-[#12211A] rounded-2xl p-4 flex-1 min-w-[150px] transition-shadow ${
        active ? 'ring-2 ring-brand-primary dark:ring-brand-accent' : ''
      }`}
    >
      <div className="flex items-center gap-2 mb-3">
        <div className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-semibold text-white" style={{ backgroundColor: color }}>
          {ticker.slice(0, 2)}
        </div>
        <span className="text-xs font-medium">{ticker}</span>
      </div>
      <div className="mb-2">
        <MiniSparkline data={sparkline} color={positive ? '#16A34A' : '#DC2626'} />
      </div>
      <p className="font-display text-lg">₦{price}</p>
      <p className={`text-xs font-medium ${positive ? 'text-signal-bullish' : 'text-signal-bearish'}`}>
        {positive ? '+' : ''}
        {changePct}%
      </p>
    </button>
  );
}
