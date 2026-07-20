'use client';

import { TradeIQMark, MoonIcon, SunIcon } from './Icons';
import { useTheme } from '@/lib/ThemeContext';

/**
 * AuthSplitLayout.tsx
 * Desktop: image panel on the left, form content on the right.
 * Mobile: the same image becomes a dark, overlaid background behind the
 * form instead of its own panel — same asset, no separate mobile image
 * needed.
 *
 * Image spec (for /public/images/auth-hero.jpg):
 *  - Portrait-friendly, at least 1200x1600px, JPG or WebP
 *  - Subject: something on-brand for a markets product — a Lagos skyline
 *    at dusk, an abstract green data/candlestick visualization, or a
 *    trading-floor style shot. Avoid real identifiable people.
 *  - Should hold up under a dark gradient overlay (avoid a very bright,
 *    busy image — the overlay needs contrast room for the logo/headline).
 */
export function AuthSplitLayout({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  const { isDark, toggleTheme } = useTheme();
  const SHOW_THEME_TOGGLE = false; // flip true once light mode is revisited

  return (
    <div className="min-h-screen flex flex-col md:flex-row relative">
      {/* Theme toggle — parked for v1, dark-only. Flip SHOW_THEME_TOGGLE to bring it back. */}
      {SHOW_THEME_TOGGLE && (
        <button
          onClick={toggleTheme}
          aria-label="Toggle dark mode"
          className="absolute top-5 right-5 z-10 w-9 h-9 rounded-full bg-black/10 dark:bg-white/10 flex items-center justify-center text-[#0A2233] dark:text-[#F3FBF6]"
        >
          {isDark ? <SunIcon size={16} /> : <MoonIcon size={16} />}
        </button>
      )}

      {/* Image panel — desktop only */}
      <div
        className="hidden md:flex md:w-[46%] md:flex-col md:justify-between md:p-10 relative bg-cover bg-center"
        style={{ backgroundImage: "url('/images/aims-hero.jpg')" }}
      >
        {/* Dark only at the top and bottom where text sits — the middle
            stays clear so the photo is actually visible, not buried under
            a near-opaque color wash. */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/55 via-black/10 to-black/70" />
        <div className="relative flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center">
            <TradeIQMark size={18} variant="dark" />
          </div>
          <span className="font-display text-white text-sm">
            TradeIQ <span className="text-brand-accent">eNGX</span>
          </span>
        </div>
        <div className="relative">
          <h2 className="font-display text-white text-3xl leading-tight mb-2">{title}</h2>
          <p className="text-[#D9E5DE] text-sm max-w-xs">{subtitle}</p>
        </div>
      </div>

      {/* Form panel — full width on mobile with the image as a background */}
      <div className="flex-1 relative flex flex-col justify-center items-center px-6 py-12 md:py-0 bg-white dark:bg-brand-dark">
        <div className="md:hidden absolute inset-0 bg-cover bg-center" style={{ backgroundImage: "url('/images/aims-hero.jpg')" }}>
          {/* Dark theme: photo stays moody and dark. */}
          <div className="hidden dark:block absolute inset-0 bg-gradient-to-b from-black/60 via-black/50 to-black/75" />
          {/* Light theme: mostly white wash, just a hint of the photo through. */}
          <div className="dark:hidden absolute inset-0 bg-gradient-to-b from-white/88 via-white/78 to-white/92" />
        </div>
        <div className="relative w-full max-w-sm text-[#0A2233] dark:text-[#F3FBF6]">
          {children}
        </div>
      </div>
    </div>
  );
}