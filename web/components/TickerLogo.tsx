'use client';

import { useState } from 'react';

/**
 * TickerLogo.tsx
 * Tries /public/images/logos/{TICKER}.png, then .jpg, then .jpeg — in that
 * order — before falling back to a colored initials circle. This handles
 * mixed file formats across the logo set (some .png, some .jpg) without
 * requiring every file to be renamed to match one exact extension.
 */
const EXTENSIONS = ['png', 'jpg', 'jpeg'] as const;

export function TickerLogo({ ticker, size = 32 }: { ticker: string; size?: number }) {
  const [attemptIndex, setAttemptIndex] = useState(0);
  const exhausted = attemptIndex >= EXTENSIONS.length;

  if (exhausted) {
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
      src={`/images/logos/${ticker}.${EXTENSIONS[attemptIndex]}`}
      alt={ticker}
      width={size}
      height={size}
      className="rounded-full object-cover shrink-0"
      onError={() => setAttemptIndex((prev) => prev + 1)}
    />
  );
}