'use client';

import { useEffect, useState } from 'react';
import { api, NewsArticle, ApiError } from '@/lib/api';

/**
 * NewsTicker.tsx
 * Genuinely fetches from GET /market/news — not hardcoded. Previously this
 * failed silently (console.warn only) if the request failed, which made it
 * indistinguishable from "not actually wired up." Now shows a real loading
 * state and a real error message, so a failure is visible and debuggable
 * instead of just rendering nothing.
 */
export function NewsTicker() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getNews()
      .then((res) => setArticles(res.articles))
      .catch((e) =>
        setError(
          e instanceof ApiError
            ? e.message
            : 'Could not reach the news service. If this is the first request in a while, it may be waking up.'
        )
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="bg-[#0A2233] dark:bg-[#12211A] rounded-2xl py-3 px-4 mb-6">
        <p className="text-xs text-[#8A8FA3] dark:text-[#8FA396]">Loading newsflash…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-[#0A2233] dark:bg-[#12211A] rounded-2xl py-3 px-4 mb-6">
        <p className="text-xs text-signal-bearish">Newsflash unavailable: {error}</p>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="bg-[#0A2233] dark:bg-[#12211A] rounded-2xl py-3 px-4 mb-6">
        <p className="text-xs text-[#8A8FA3] dark:text-[#8FA396]">No news available right now.</p>
      </div>
    );
  }

  // Duplicate the list so the marquee loops seamlessly instead of jumping.
  const loop = [...articles, ...articles];

  return (
    <div className="bg-[#0A2233] dark:bg-[#12211A] rounded-2xl py-3 overflow-hidden mb-6">
      <div className="flex items-center gap-2 px-4 mb-2">
        <span className="w-1.5 h-1.5 rounded-full bg-signal-bearish animate-pulse" />
        <span className="text-[10px] font-semibold text-signal-bearish tracking-wide">LIVE</span>
        <span className="text-[10px] text-[#8A8FA3]">Stockflash</span>
      </div>
      <div className="overflow-hidden whitespace-nowrap">
        <div className="inline-flex gap-10 animate-marquee">
          {loop.map((article, i) => (
            <span key={i} className="text-sm text-white px-2">
              {article.title}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
