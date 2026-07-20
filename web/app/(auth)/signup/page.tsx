'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';
import { useAuth } from '@/lib/AuthContext';
import { AuthForm } from '@/components/AuthForm';
import { AuthSplitLayout } from '@/components/AuthSplitLayout';

export default function SignupPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(values: { username?: string; email: string; password: string }) {
    setSubmitting(true);
    setError(null);
    try {
      // The doc doesn't confirm what /auth/signup returns — only /auth/login's
      // response shape is documented. Signing up then explicitly logging in
      // right after is the safer path until that's confirmed either way.
      await api.signup(values.username ?? '', values.email, values.password);
      const res = await api.login(values.email, values.password);
      login(res.access_token);
      router.push('/');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not create your account. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthSplitLayout title="Create your account" subtitle="Start tracking NGX signals with plain-English AI analysis in minutes.">
      <h1 className="font-display text-2xl mb-1">Sign up</h1>
      <p className="text-sm opacity-70 mb-8">Create your TradeIQ eNGX account</p>

      <AuthForm mode="signup" onSubmit={handleSubmit} submitting={submitting} error={error} />

      <p className="text-sm opacity-70 text-center mt-6">
        Already have an account?{' '}
        <Link href="/login" className="text-brand-accent font-medium">
          Log in
        </Link>
      </p>
    </AuthSplitLayout>
  );
}