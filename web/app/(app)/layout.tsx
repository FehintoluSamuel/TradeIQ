'use client';

/**
 * app/(app)/layout.tsx
 * Wraps Dashboard/Market/News/Profile in NavShell. This is the actual
 * login gate: if the auth check finishes and there's no token, redirect
 * to /welcome before rendering any protected content.
 */
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/AuthContext';
import { NavShell } from '@/components/NavShell';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.replace('/welcome');
    }
  }, [loading, isAuthenticated, router]);

  if (loading || !isAuthenticated) return null;

  return <NavShell>{children}</NavShell>;
}
