'use client';

/**
 * lib/AuthContext.tsx
 * Holds the JWT + a display username in localStorage. There's no backend
 * "current user" endpoint documented yet, so the username is captured at
 * signup time (the form collects it) and persisted here for the "Welcome,
 * {username}" header greeting. Login alone doesn't collect a username —
 * if someone logs in on a browser that never signed up here before, the
 * greeting falls back to the part of their email before the @.
 */
import React, { createContext, useContext, useEffect, useState } from 'react';

type AuthContextValue = {
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (token: string, username?: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = 'tradeiq-token';
const USERNAME_KEY = 'tradeiq-username';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setToken(localStorage.getItem(TOKEN_KEY));
    setUsername(localStorage.getItem(USERNAME_KEY));
    setLoading(false);
  }, []);

  function login(newToken: string, newUsername?: string) {
    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
    if (newUsername) {
      localStorage.setItem(USERNAME_KEY, newUsername);
      setUsername(newUsername);
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USERNAME_KEY);
    setToken(null);
    setUsername(null);
  }

  return (
    <AuthContext.Provider value={{ token, username, isAuthenticated: !!token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth() must be called within an <AuthProvider>');
  return ctx;
}
