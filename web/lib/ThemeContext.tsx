'use client';

/**
 * lib/ThemeContext.tsx
 * Toggles a `dark` class on <html>, which Tailwind's darkMode:'class'
 * strategy picks up everywhere via dark: variants. Persists the choice in
 * localStorage — the doc's caution about localStorage is specifically
 * about storing sensitive data like JWTs there, not UI preferences like
 * this, so it's the right tool here.
 */
import React, { createContext, useContext, useEffect, useState } from 'react';

type ThemeContextValue = {
  isDark: boolean;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Dark-only for v1 — light mode is parked, not deleted. Re-enable by
    // restoring the localStorage/system-preference check that used to be
    // here, and un-hiding the toggle buttons in AuthSplitLayout and the
    // Dashboard header.
    setIsDark(true);
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem('tradeiq-theme', isDark ? 'dark' : 'light');
  }, [isDark, mounted]);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme: () => setIsDark((prev) => !prev) }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme() must be called within a <ThemeProvider>');
  return ctx;
}