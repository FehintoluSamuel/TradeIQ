import Link from 'next/link';
import { TradeIQMark } from '@/components/Icons';

export default function WelcomePage() {
  return (
    <div
      className="min-h-screen bg-cover bg-center flex flex-col justify-between px-6 py-10 md:items-center relative"
      style={{ backgroundImage: "url('/images/aims-hero.jpg')" }}
    >
      <div className="absolute inset-0 bg-gradient-to-b from-brand-dark/70 via-brand-forest/25 to-brand-dark/85" />
      <div className="relative w-full max-w-sm flex flex-col justify-between min-h-[calc(100vh-5rem)]">
        <div className="mt-10">
          <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center mb-5">
            <TradeIQMark size={26} variant="dark" />
          </div>
          <h1 className="font-display text-white text-[29px] leading-tight mb-3">
            NGX signals,
            <br />
            explained simply.
          </h1>
          <p className="text-[#A8C3B4] text-sm leading-relaxed max-w-[260px]">
            Track 24 Nigerian Exchange stocks with plain-English AI analysis of every move.
          </p>
        </div>

        <div>
          <Link
            href="/login"
            className="block w-full bg-white text-[#0A2818] rounded-2xl py-4 text-center text-sm font-semibold mb-2.5"
          >
            Log in
          </Link>
          <Link
            href="/signup"
            className="block w-full border border-white/25 text-[#F3FBF6] rounded-2xl py-4 text-center text-sm font-medium mb-4"
          >
            Create account
          </Link>
          <p className="text-[#5C8570] text-[10.5px] text-center leading-relaxed">
            By continuing you agree to TradeIQ eNGX&apos;s
            <br />
            <span className="text-[#8FEFB4]">Terms of Use</span> and{' '}
            <span className="text-[#8FEFB4]">Privacy Policy</span>
          </p>
        </div>
      </div>
    </div>
  );
}