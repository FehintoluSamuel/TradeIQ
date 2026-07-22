const API_BASE_URL = 'https://tradeiq-12gh.onrender.com';
const MARKET_INTEL_BASE_URL = 'https://tradeiq-microservices.onrender.com';
const TOKEN_KEY = 'tradeiq-token'; // must match lib/AuthContext.tsx

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response wasn't JSON, keep statusText
    }
    throw new ApiError(detail, res.status);
  }
  return res.json();
}

// Protected endpoints (stocks, prices, signals) need this header — it was
// missing entirely before, which is why those calls were failing with
// "Not authenticated" even after a successful login.
function authHeaders(): HeadersInit {
  const token = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export type Stock = { id: number; ticker: string; full_name: string; sector: string };
export type Price = { date: string; open: string; high: string; low: string; close: string; volume: number };
export type Signal = {
  ticker: string;
  date: string;
  close: string;
  change_pct: number;
  ma7: string | null;
  ma30: string | null;
  rsi: number;
  signal: 'bullish' | 'bearish' | 'neutral' | 'overbought' | 'oversold';
  signal_reason: string;
};
export type MarketSnapshot = {
  date: string;
  all_share_index: number;
  asi_change: number;
  asi_change_percent: number;
  ytd_change_percent: number;
  deals: number;
  volume: number;
  value_traded: number;
  market_cap: { equities: number; total: number };
  breadth: { advancers: number; decliners: number; unchanged: number };
};
export type NewsArticle = {
  title: string;
  description: string;
  source: string;
  published_at: string;
  url: string | null;
  explanation?: string;
};
export type AuthResponse = { access_token: string; token_type: string };

export const api = {
  getStocks: () => request<Stock[]>(`${API_BASE_URL}/api/v1/stocks`, { headers: authHeaders() }),
  getPrices: (ticker: string, limit = 30) =>
    request<Price[]>(`${API_BASE_URL}/api/v1/prices/${ticker}?limit=${limit}`, { headers: authHeaders() }),
  getAllSignals: () => request<Signal[]>(`${API_BASE_URL}/api/v1/signals/all`, { headers: authHeaders() }),
  getSignal: (ticker: string) =>
    request<Signal>(`${API_BASE_URL}/api/v1/signals/${ticker}`, { headers: authHeaders() }),
  explainSignal: (ticker: string) =>
    request<{ ticker: string; explanation: string }>(`${API_BASE_URL}/api/v1/signals/${ticker}/explain`, {
      headers: authHeaders(),
    }),
  getMarketSnapshot: () => request<MarketSnapshot>(`${MARKET_INTEL_BASE_URL}/market/snapshot`),
  getNews: () => request<{ articles: NewsArticle[] }>(`${MARKET_INTEL_BASE_URL}/market/news`),

  // Login is form-urlencoded with a field literally named "username" that
  // holds the email address — matches the doc's OAuth2-password-flow shape
  // exactly, even though the field name reads oddly.
  login: (email: string, password: string) => {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);
    return request<AuthResponse>(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    });
  },

  // Signup is plain JSON with a separate username and email field.
  signup: (username: string, email: string, password: string) =>
    request<AuthResponse>(`${API_BASE_URL}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    }),
};
