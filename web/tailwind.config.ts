import type { Config } from 'tailwindcss';

// Ported directly from the RN theme.ts palette. Dark mode uses Tailwind's
// 'class' strategy (a .dark class on <html>) so ThemeContext can toggle it
// the same way it toggled RN's theme context — one flip, whole app follows.
const config: Config = {
  darkMode: 'class',
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#070F0A',
          forest: '#0A2818',
          primary: '#0F5C2E',
          accent: '#22C55E',
          mint: '#D1FAE5',
        },
        signal: {
          bullish: '#16A34A',
          bearish: '#DC2626',
          overbought: '#F59E0B',
          oversold: '#60A5FA',
          neutral: '#9CA3AF',
        },
      },
      fontFamily: {
        sans: ['var(--font-jakarta)', 'sans-serif'],
        display: ['var(--font-fraunces)', 'serif'],
      },
      maxWidth: {
        content: '1100px',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
      },
      animation: {
        marquee: 'marquee 18s linear infinite',
      },
    },
  },
  plugins: [],
};

export default config;
