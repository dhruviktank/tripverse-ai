'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.replace('/login');
    } else {
      setAuthorized(true);
    }
  }, [router]);

  if (!authorized) {
    // Show a brief loading state while checking auth
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-[var(--on-surface-variant)] text-lg">Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
}
