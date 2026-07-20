'use client';

/**
 * app/(auth)/layout.tsx
 * Wraps Welcome/Login/Signup — intentionally no NavShell here. If someone
 * who's already logged in lands on one of these routes (e.g. hits /login
 * directly via a bookmark), send them straight to the dashboard instead of
 * showing them a login form they don't need.
 */
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/AuthContext';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.replace('/');
    }
  }, [loading, isAuthenticated, router]);

  if (loading) return null;

  return <>{children}</>;
}
