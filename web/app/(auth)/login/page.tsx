'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';
import { useAuth } from '@/lib/AuthContext';
import { AuthForm } from '@/components/AuthForm';
import { AuthSplitLayout } from '@/components/AuthSplitLayout';

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(values: { email: string; password: string }) {
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.login(values.email, values.password);
      login(res.access_token);
      router.push('/');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not log in. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthSplitLayout title="Welcome back" subtitle="Track 24 NGX stocks with plain-English AI analysis of every move.">
      <h1 className="font-display text-2xl mb-1">Log in</h1>
      <p className="text-sm opacity-70 mb-8">Continue to TradeIQ eNGX</p>

      <AuthForm mode="login" onSubmit={handleSubmit} submitting={submitting} error={error} />

      <p className="text-sm opacity-70 text-center mt-6">
        Don&apos;t have an account?{' '}
        <Link href="/signup" className="text-brand-accent font-medium">
          Create one
        </Link>
      </p>
    </AuthSplitLayout>
  );
}