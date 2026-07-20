'use client';

/**
 * NavShell.tsx
 * Bottom tab bar on mobile, left sidebar on desktop — driven entirely by
 * Tailwind's `md:` breakpoint classes, not JavaScript width checks. Two
 * navs are rendered; CSS `hidden`/`md:flex` decides which one is visible at
 * a given viewport width, which is instant on resize with no layout flash,
 * unlike a JS-based useWindowDimensions approach.
 */
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { TradeIQMark } from './Icons';
import { HomeIcon, MarketIcon, NewsIcon, ProfileIcon } from './Icons';

const NAV_ITEMS = [
  { href: '/', label: 'Home', icon: HomeIcon },
  { href: '/market', label: 'Market', icon: MarketIcon },
  { href: '/news', label: 'News', icon: NewsIcon },
  { href: '/profile', label: 'Profile', icon: ProfileIcon },
];

export function NavShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="md:flex md:min-h-screen">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex md:flex-col md:w-56 md:shrink-0 md:border-r md:border-[#EFEFF2] dark:md:border-[#17251C] md:p-4 md:pt-6">
        <div className="flex items-center gap-2 px-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-[#0A2233] dark:bg-[#F3FBF6] flex items-center justify-center">
            <TradeIQMark size={17} variant="dark" />
          </div>
          <span className="font-display text-sm">TradeIQ <span className="text-brand-primary dark:text-brand-accent">eNGX</span></span>
        </div>
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? 'bg-[#F2F2F7] dark:bg-[#12211A] text-brand-primary dark:text-brand-accent'
                    : 'text-[#8A8FA3] dark:text-[#8FA396] hover:bg-[#F5F6FA] dark:hover:bg-[#0A2818]'
                }`}
              >
                <Icon size={19} />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 max-w-content mx-auto w-full pb-20 md:pb-0 md:px-10 md:py-8">{children}</main>

      {/* Mobile bottom bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 flex justify-around items-center bg-white dark:bg-brand-dark border-t border-[#EFEFF2] dark:border-[#17251C] py-2.5">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex flex-col items-center gap-1 text-[10px] font-semibold ${
                active ? 'text-brand-primary dark:text-brand-accent' : 'text-[#B0B4C2] dark:text-[#5C7568]'
              }`}
            >
              <Icon size={20} />
              {label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
