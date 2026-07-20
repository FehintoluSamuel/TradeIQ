'use client';

import { useState, FormEvent } from 'react';

type AuthFormValues = { username?: string; email: string; password: string };

type Props = {
  mode: 'login' | 'signup';
  onSubmit: (values: AuthFormValues) => Promise<void>;
  submitting: boolean;
  error: string | null;
};

export function AuthForm({ mode, onSubmit, submitting, error }: Props) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit(mode === 'signup' ? { username, email, password } : { email, password });
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      {mode === 'signup' && (
        <div className="mb-4">
          <label className="block text-xs font-medium text-[#8A8FA3] dark:text-[#8FA396] mb-1.5">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full bg-[#F5F6FA] dark:bg-[#12211A] rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-primary"
            placeholder="yourname"
          />
        </div>
      )}

      <div className="mb-4">
        <label className="block text-xs font-medium text-[#8A8FA3] dark:text-[#8FA396] mb-1.5">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full bg-[#F5F6FA] dark:bg-[#12211A] rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-primary"
          placeholder="you@example.com"
        />
      </div>

      <div className="mb-6">
        <label className="block text-xs font-medium text-[#8A8FA3] dark:text-[#8FA396] mb-1.5">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="w-full bg-[#F5F6FA] dark:bg-[#12211A] rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-primary"
          placeholder="••••••••"
        />
      </div>

      {error && <p className="text-signal-bearish text-xs mb-4">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-[#0A2233] dark:bg-brand-primary text-white rounded-xl py-3.5 text-sm font-semibold disabled:opacity-60"
      >
        {submitting ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
      </button>
    </form>
  );
}
