'use client';

import { useCallback, useEffect, useState } from 'react';
import { api, NewsArticle, ApiError } from '@/lib/api';

export default function NewsPage() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback((isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    api
      .getNewsExplained()
      .then((res) => setArticles(res.articles))
      .catch((e) =>
        setError(
          e instanceof ApiError
            ? e.message
            : 'Could not reach the news service. If this is the first request in a while, it may be waking up.'
        )
      )
      .finally(() => {
        setLoading(false);
        setRefreshing(false);
      });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="px-4 pt-4 md:pt-0">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl md:text-[28px] font-semibold">News</h1>
        <button
          onClick={() => load(true)}
          disabled={refreshing}
          className="text-xs font-medium text-brand-primary dark:text-brand-accent disabled:opacity-50"
        >
          {refreshing ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {loading && <p className="text-sm text-[#8A8FA3] dark:text-[#8FA396]">Loading news…</p>}
      {error && <p className="text-sm text-signal-bearish">{error}</p>}
      {!loading && !error && articles.length === 0 && (
        <p className="text-sm text-[#8A8FA3] dark:text-[#8FA396]">No news available right now.</p>
      )}

      <div className="flex flex-col gap-4 pb-8">
        {articles.map((article, i) => (
          <div
            key={i}
            className="bg-[#FAFBFC] dark:bg-[#0A2818] border border-[#EFEFF2] dark:border-[#17251C] rounded-2xl p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[11px] font-medium text-[#8A8FA3] dark:text-[#8FA396]">{article.source}</span>
              <span className="text-[11px] text-[#B0B4C2] dark:text-[#5C7568]">·</span>
              <span className="text-[11px] text-[#8A8FA3] dark:text-[#8FA396]">{article.published_at}</span>
            </div>
            <h2 className="text-sm font-semibold mb-2 leading-snug">{article.title}</h2>
            {article.explanation && (
              <p className="text-sm leading-relaxed text-[#0A2233] dark:text-[#F3FBF6] opacity-90">
                {article.explanation}
              </p>
            )}
            {article.url && (
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-3 text-xs font-medium text-brand-primary dark:text-brand-accent"
              >
                Read original →
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
