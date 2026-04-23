'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    try {
      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || 'Invalid email or password');
        setLoading(false);
        return;
      }

      // Store token and user info
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Redirect to dashboard
      router.push('/dashboard');
    } catch {
      setError('Unable to connect to server. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[480px]">
      <div className="glass-card rounded-2xl p-10 shadow-xl shadow-indigo-500/5">
        <div className="text-center mb-10">
          <h1 className="font-display text-4xl text-[var(--on-surface)] mb-2 tracking-tight font-bold">Welcome back</h1>
          <p className="text-[var(--on-surface-variant)] text-lg">Log in to continue your journey</p>
        </div>

        {error && (
          <div className="mb-6 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium text-[var(--on-surface-variant)] block">Email Address</label>
            <div className="relative">
              <input 
                id="email" 
                name="email" 
                type="email" 
                required
                placeholder="name@company.com" 
                className="w-full h-14 px-4 bg-[var(--surface-container-lowest)] border border-[var(--outline-variant)] rounded-xl neumorphic-input focus:border-[var(--primary-container)] focus:ring-0 outline-none" 
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label htmlFor="password" className="text-sm font-medium text-[var(--on-surface-variant)] block">Password</label>
              <Link href="#" className="text-sm text-[var(--primary)] hover:underline">Forgot password?</Link>
            </div>
            <div className="relative">
              <input 
                id="password" 
                name="password" 
                type="password" 
                required
                placeholder="••••••••" 
                className="w-full h-14 px-4 bg-[var(--surface-container-lowest)] border border-[var(--outline-variant)] rounded-xl neumorphic-input focus:border-[var(--primary-container)] focus:ring-0 outline-none" 
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full h-14 mt-4 bg-[var(--primary-container)] text-white rounded-xl text-lg font-semibold shadow-lg shadow-indigo-500/20 active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:active:scale-100"
          >
            {loading ? 'Logging in...' : 'Log In'}
            {!loading && (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
                <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
              </svg>
            )}
          </button>
        </form>

        <div className="mt-10 text-center">
          <p className="text-[var(--on-surface-variant)] text-lg">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-[var(--primary)] font-semibold hover:underline transition-all">Sign up</Link>
          </p>
        </div>
      </div>

      <div className="mt-6 flex items-center justify-center gap-2 opacity-60">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
          <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
        <span className="text-xs uppercase tracking-tighter">Bank-grade encryption for your data</span>
      </div>
    </div>
  );
}
