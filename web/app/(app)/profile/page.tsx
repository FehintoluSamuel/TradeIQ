'use client';

/**
 * app/(app)/profile/page.tsx
 * The doc doesn't document a "get current user" endpoint, so there's no
 * user info (name, email) to display yet beyond confirming someone's
 * logged in. Logout is fully real — it clears the token via AuthContext,
 * and the (app) layout's redirect effect takes it from there.
 */
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/AuthContext';

export default function ProfilePage() {
  const { logout } = useAuth();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push('/welcome');
  }

  return (
    <div className="px-4 pt-4 md:pt-0">
      <h1 className="text-2xl md:text-[28px] font-semibold mb-6">Profile</h1>
      <p className="text-sm text-[#8A8FA3] dark:text-[#8FA396] mb-8">
        Account details aren&apos;t available from the backend yet — this will show your name and email
        once a &quot;current user&quot; endpoint is added.
      </p>
      <button
        onClick={handleLogout}
        className="border border-signal-bearish text-signal-bearish rounded-xl px-5 py-3 text-sm font-medium"
      >
        Log out
      </button>
    </div>
  );
}
