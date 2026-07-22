'use client';

import { useState } from 'react';

/**
 * TickerLogo.tsx
 * Looks for /public/images/logos/{TICKER}.png. Falls back to a colored
 * initials circle if that file doesn't exist yet — so the app works today
 * and upgrades automatically once real logo files are added, no code
 * change needed later.
 */
export function TickerLogo({ ticker, size = 32 }: { ticker: string; size?: number }) {
  const [errored, setErrored] = useState(false);

  if (errored) {
    return (
      <div
        className="rounded-full bg-brand-primary flex items-center justify-center text-white font-semibold shrink-0"
        style={{ width: size, height: size, fontSize: size * 0.32 }}
      >
        {ticker.slice(0, 2)}
      </div>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={`/images/logos/${ticker}.png`}
      alt={ticker}
      width={size}
      height={size}
      className="rounded-full object-cover shrink-0"
      onError={() => setErrored(true)}
    />
  );
}
