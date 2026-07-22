export function TradeIQMark({ size = 20, variant = 'light' }: { size?: number; variant?: 'dark' | 'light' }) {
  const bars = variant === 'dark' ? ['#0F5C2E', '#1D8449', '#22C55E'] : ['#A7F3D0', '#4ADE80', '#0F5C2E'];
  const line = variant === 'dark' ? '#D1FAE5' : '#0A2233';
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <rect x="5" y="24" width="6" height="11" rx="1.5" fill={bars[0]} />
      <rect x="15" y="17" width="6" height="18" rx="1.5" fill={bars[1]} />
      <rect x="25" y="9" width="6" height="26" rx="1.5" fill={bars[2]} />
      <path d="M6 23 L14 16 L20 19 L32 6" stroke={line} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M25 6 L32 6 L32 13" stroke={line} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function BellIcon({ className = '', size = 16 }: { className?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M6 10C6 6.68629 8.68629 4 12 4C15.3137 4 18 6.68629 18 10V14L20 17H4L6 14V10Z" stroke="currentColor" strokeWidth={1.7} strokeLinejoin="round" />
      <path d="M9.5 17C9.5 18.3807 10.6193 19.5 12 19.5C13.3807 19.5 14.5 18.3807 14.5 17" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" />
    </svg>
  );
}

export function MoonIcon({ className = '', size = 16 }: { className?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M20 14.5C18.7 15.9 16.9 16.75 15 16.75C11 16.75 7.75 13.5 7.75 9.5C7.75 7.6 8.6 5.8 10 4.5C6.05 5.1 3 8.5 3 12.6C3 17.1 6.65 20.75 11.15 20.75C15 20.75 18.25 18.1 19.15 14.5H20Z" fill="currentColor" />
    </svg>
  );
}

export function SunIcon({ className = '', size = 16 }: { className?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth={1.7} />
      <path d="M12 2.5V4.5M12 19.5V21.5M4.5 12H2.5M21.5 12H19.5M5.6 5.6L4.9 4.9M19.1 19.1L18.4 18.4M18.4 5.6L19.1 4.9M4.9 19.1L5.6 18.4" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" />
    </svg>
  );
}

export function HomeIcon({ className = '', size = 20 }: { className?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M4 11L12 4L20 11V19A1 1 0 0119 20H5A1 1 0 014 19V11Z" stroke="currentColor" strokeWidth={1.8} strokeLinejoin="round" />
    </svg>
  );
}

export function MarketIcon({ className = '', size = 20 }: { className?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <rect x="4" y="12" width="3.5" height="8" rx="1" stroke="currentColor" strokeWidth={1.8} />
      <rect x="10.25" y="7" width="3.5" height="13" rx="1" stroke="currentColor" strokeWidth={1.8} />
      <rect x="16.5" y="4" width="3.5" height="16" rx="1" stroke="currentColor" strokeWidth={1.8} />
    </svg>
  );
}

export function NewsIcon({ className = '', size = 20 }: { className?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <rect x="4" y="5" width="16" height="15" rx="1.5" stroke="currentColor" strokeWidth={1.8} />
      <path d="M7.5 9H16.5M7.5 12.5H16.5M7.5 16H13" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" />
    </svg>
  );
}

export function ProfileIcon({ className = '', size = 20 }: { className?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="8" r="3.2" stroke="currentColor" strokeWidth={1.8} />
      <path d="M5 20C5 16.5 8 14.5 12 14.5C16 14.5 19 16.5 19 20" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" />
    </svg>
  );
}

export function colorForSignal(signal: string): string {
  const map: Record<string, string> = {
    bullish: 'text-signal-bullish',
    bearish: 'text-signal-bearish',
    overbought: 'text-signal-overbought',
    oversold: 'text-signal-oversold',
    neutral: 'text-signal-neutral',
  };
  return map[signal.toLowerCase()] ?? map.neutral;
}

export function bgForSignal(signal: string): string {
  const map: Record<string, string> = {
    bullish: 'bg-signal-bullish',
    bearish: 'bg-signal-bearish',
    overbought: 'bg-signal-overbought',
    oversold: 'bg-signal-oversold',
    neutral: 'bg-signal-neutral',
  };
  return map[signal.toLowerCase()] ?? map.neutral;
}

// For spots needing a literal color value (inline style props, SVG stroke),
// where a Tailwind class string like the two helpers above can't be used.
export function hexForSignal(signal: string): string {
  const map: Record<string, string> = {
    bullish: '#16A34A',
    bearish: '#DC2626',
    overbought: '#F59E0B',
    oversold: '#60A5FA',
    neutral: '#9CA3AF',
  };
  return map[signal.toLowerCase()] ?? map.neutral;
}
