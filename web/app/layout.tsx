import type { Metadata, Viewport } from 'next';
import { Plus_Jakarta_Sans, Fraunces } from 'next/font/google';
import { ThemeProvider } from '@/lib/ThemeContext';
import { AuthProvider } from '@/lib/AuthContext';
import './globals.css';

const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-jakarta',
});
const fraunces = Fraunces({
  subsets: ['latin'],
  weight: ['500'],
  variable: '--font-fraunces',
});

export const metadata: Metadata = {
  title: 'TradeIQ eNGX',
  description: 'NGX market signals, explained simply.',
};

// Explicit, rather than relying on Next.js's default — this is the most
// common root cause of a site rendering "zoomed out"/not fitting on a
// phone: without width=device-width, mobile browsers assume a desktop-width
// viewport (~980px) and shrink everything to fit, making it look broken.
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${jakarta.variable} ${fraunces.variable} font-sans bg-white dark:bg-brand-dark text-[#0A2233] dark:text-[#F3FBF6] overflow-x-hidden`}
      >
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
