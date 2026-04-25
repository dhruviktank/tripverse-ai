'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export default function RegisterPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    const formData = new FormData(e.currentTarget);
    const full_name = formData.get('full_name') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const confirm_password = formData.get('confirm_password') as string;

    // Client-side validation
    if (password !== confirm_password) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || 'Registration failed. Please try again.');
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
          <h1 className="font-display text-4xl text-[var(--on-surface)] mb-2 tracking-tight font-bold">Create an account</h1>
          <p className="text-[var(--on-surface-variant)] text-lg">Join 50,000+ travelers planning with AI</p>
        </div>

        {error && (
          <div className="mb-6 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="full_name" className="text-sm font-medium text-[var(--on-surface-variant)] block">Full Name</label>
            <div className="relative">
              <input 
                id="full_name" 
                name="full_name" 
                type="text" 
                required
                placeholder="John Doe" 
                className="w-full h-14 px-4 bg-[var(--surface-container-lowest)] border border-[var(--outline-variant)] rounded-xl neumorphic-input focus:border-[var(--primary-container)] focus:ring-0 outline-none" 
              />
            </div>
          </div>

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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-[var(--on-surface-variant)] block">Password</label>
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
            
            <div className="space-y-2">
              <label htmlFor="confirm_password" className="text-sm font-medium text-[var(--on-surface-variant)] block">Confirm Password</label>
              <div className="relative">
                <input 
                  id="confirm_password" 
                  name="confirm_password" 
                  type="password" 
                  required
                  placeholder="••••••••" 
                  className="w-full h-14 px-4 bg-[var(--surface-container-lowest)] border border-[var(--outline-variant)] rounded-xl neumorphic-input focus:border-[var(--primary-container)] focus:ring-0 outline-none" 
                />
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3 py-2">
            <input 
              id="terms" 
              type="checkbox" 
              required
              className="mt-1 rounded border-[var(--outline-variant)] text-[var(--primary)] focus:ring-[var(--primary-container)]" 
            />
            <label htmlFor="terms" className="text-xs text-[var(--on-surface-variant)]">
              I agree to the <Link href="#" className="text-[var(--primary)] hover:underline">Terms of Service</Link> and <Link href="#" className="text-[var(--primary)] hover:underline">Privacy Policy</Link>.
            </label>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full h-14 bg-[var(--primary-container)] text-white rounded-xl text-lg font-semibold shadow-lg shadow-indigo-500/20 active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:active:scale-100"
          >
            {loading ? 'Creating account...' : 'Sign Up'}
            {!loading && (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
                <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
              </svg>
            )}
          </button>
        </form>

        <div className="mt-10 text-center">
          <p className="text-[var(--on-surface-variant)] text-lg">
            Already have an account?{' '}
            <Link href="/login" className="text-[var(--primary)] font-semibold hover:underline transition-all">Log in</Link>
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
