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
    // Light-only for v1 — this was previously locked to dark for the auth
    // screens specifically, but that setting is global and was making the
    // entire app (Dashboard/Market/News) render dark too, not just Welcome/
    // Login/Signup. White is the main surface color for the app; green is
    // an accent only. Toggle infrastructure kept intact for later.
    setIsDark(false);
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
