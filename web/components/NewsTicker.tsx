'use client';

import { useEffect, useState } from 'react';
import { api, NewsArticle, ApiError } from '@/lib/api';

export function NewsTicker() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);

  useEffect(() => {
    api
      .getNews()
      .then((res) => setArticles(res.articles))
      .catch((e) => {
        // Non-critical for the dashboard — fail silently rather than
        // blocking the rest of the page over a news-strip fetch.
        if (e instanceof ApiError) console.warn('News ticker fetch failed:', e.message);
      });
  }, []);

  if (articles.length === 0) return null;

  // Duplicate the list so the marquee loops seamlessly instead of jumping.
  const loop = [...articles, ...articles];

  return (
    <div className="bg-[#0A2233] dark:bg-[#12211A] rounded-2xl py-3 overflow-hidden mb-6">
      <div className="flex items-center gap-2 px-4 mb-2">
        <span className="w-1.5 h-1.5 rounded-full bg-signal-bearish animate-pulse" />
        <span className="text-[10px] font-semibold text-signal-bearish tracking-wide">LIVE</span>
        <span className="text-[10px] text-[#8A8FA3]">Newsflash</span>
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
