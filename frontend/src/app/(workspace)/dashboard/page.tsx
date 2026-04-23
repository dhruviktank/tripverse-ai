"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { tripApi, type TripData, type DashboardStats } from "@/lib/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await tripApi.dashboardStats();
        setStats(data.stats);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load dashboard",
        );
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  const firstName = user?.full_name?.split(" ")[0] || "Traveler";

  // Gradient palette for trip cards
  const cardGradients = [
    "linear-gradient(135deg,#7cc0ff,#2f77e6)",
    "linear-gradient(135deg,#1a1f4d,#3f63d8)",
    "linear-gradient(135deg,#253955,#3a77b4)",
    "linear-gradient(135deg,#4f46e5,#7c3aed)",
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-8">
      {/* Header */}
      <section className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold text-[var(--on-surface-variant)]">
            Hello, {firstName}
          </p>
          <h1 className="mt-1 font-display text-4xl text-[var(--on-surface)] sm:text-5xl">
            Where should the AI take you next?
          </h1>
        </div>
        <div className="flex gap-3">
          <Link
            href="/planner"
            className="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-bold text-white transition hover:bg-[var(--primary-container)]"
          >
            Create Trip
          </Link>
          <Link
            href="/history"
            className="rounded-xl border border-[var(--outline-variant)] bg-white px-5 py-3 text-sm font-bold text-[var(--primary)]"
          >
            View Trips
          </Link>
        </div>
      </section>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="mx-auto h-10 w-10 rounded-full border-4 border-[var(--primary)] border-t-transparent animate-spin" />
            <p className="mt-4 text-sm text-[var(--on-surface-variant)]">
              Loading your dashboard...
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm font-semibold text-red-700">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-3 rounded-xl bg-red-600 px-4 py-2 text-sm font-bold text-white"
          >
            Retry
          </button>
        </div>
      )}

      {/* Content */}
      {!loading && !error && stats && (
        <>
          {/* AI Recommendation + Quick Stats */}
          <section className="grid gap-6 md:grid-cols-12">
            <article className="relative overflow-hidden rounded-3xl border border-indigo-200/40 bg-[linear-gradient(145deg,#4f46e5,#2f23bd)] p-7 text-white shadow-[0_24px_60px_-35px_rgba(53,37,205,0.7)] md:col-span-8">
              <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-cyan-300/20 blur-3xl" />
              <p className="inline-flex rounded-full bg-white/20 px-3 py-1 text-[11px] font-semibold tracking-wide uppercase">
                AI Recommendation
              </p>
              <h2 className="mt-4 max-w-2xl font-display text-4xl">
                A serene escape to the Amalfi Coast
              </h2>
              <p className="mt-3 max-w-xl text-sm text-white/90">
                Based on your saved preferences, this 7-day route balances
                coastal views, local food walks, and relaxed transit windows.
              </p>
              <div className="mt-6 flex gap-3">
                <Link
                  href="/planner"
                  className="rounded-xl bg-white px-4 py-2 text-sm font-bold text-[var(--primary)]"
                >
                  Start Planning
                </Link>
                <button className="rounded-xl border border-white/50 px-4 py-2 text-sm font-semibold">
                  Estimated 4h setup
                </button>
              </div>
            </article>

            <div className="space-y-4 md:col-span-4">
              <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 shadow-[0_14px_35px_-28px_rgba(53,37,205,0.35)]">
                <p className="text-4xl font-black text-[var(--primary)]">
                  {stats.total_trips}
                </p>
                <p className="mt-2 text-base font-semibold text-[var(--on-surface)]">
                  Total Adventures
                </p>
                <p className="mt-1 text-sm text-[var(--on-surface-variant)]">
                  Since joining TripVerse
                </p>
              </article>
              <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 shadow-[0_14px_35px_-28px_rgba(53,37,205,0.35)]">
                <p className="text-4xl font-black text-[var(--primary)]">
                  {stats.upcoming_trips}
                </p>
                <p className="mt-2 text-base font-semibold text-[var(--on-surface)]">
                  Upcoming Trips
                </p>
                <p className="mt-1 text-sm text-[var(--on-surface-variant)]">
                  {stats.average_budget > 0
                    ? `Avg budget: $${stats.average_budget.toLocaleString()}`
                    : "Plan your first trip!"}
                </p>
              </article>
            </div>
          </section>

          {/* Recent Trips */}
          <section>
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-display text-3xl">Recent Trips</h3>
              <Link
                href="/history"
                className="text-sm font-bold text-[var(--primary)]"
              >
                View all
              </Link>
            </div>

            {stats.recent_trips.length === 0 ? (
              <div className="rounded-3xl border border-[var(--outline-variant)] bg-white p-12 text-center">
                <p className="text-lg font-semibold text-[var(--on-surface-variant)]">
                  No trips yet! 🌍
                </p>
                <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
                  Head to the AI Planner to create your first adventure.
                </p>
                <Link
                  href="/planner"
                  className="mt-4 inline-flex rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-bold text-white"
                >
                  Plan a Trip
                </Link>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
                {stats.recent_trips.map((trip: TripData, idx: number) => (
                  <Link
                    key={trip.id}
                    href={`/itinerary/${trip.id}`}
                    className="group rounded-3xl border border-[var(--outline-variant)] bg-white p-4 shadow-[0_12px_30px_-22px_rgba(77,68,227,0.35)] transition hover:shadow-lg hover:-translate-y-1"
                  >
                    <div
                      className="mb-4 h-36 rounded-2xl"
                      style={{
                        background: cardGradients[idx % cardGradients.length],
                      }}
                    />
                    <p className="inline-flex rounded-full bg-[var(--secondary-container)]/40 px-3 py-1 text-xs font-semibold text-[var(--on-secondary-container)]">
                      {trip.status}
                    </p>
                    <h4 className="mt-3 text-xl font-bold text-[var(--on-surface)] group-hover:text-[var(--primary)] transition">
                      {trip.title}
                    </h4>
                    <p className="mt-1 text-sm text-[var(--on-surface-variant)]">
                      {trip.dates || trip.created_at?.split("T")[0] || "—"}
                    </p>
                  </Link>
                ))}
              </div>
            )}
          </section>
        </>
      )}

      {/* Empty state when no stats and no error */}
      {!loading && !error && !stats && (
        <div className="rounded-3xl border border-[var(--outline-variant)] bg-white p-16 text-center">
          <p className="text-lg font-semibold text-[var(--on-surface-variant)]">
            Welcome to TripVerse AI! Start by planning your first trip.
          </p>
          <Link
            href="/planner"
            className="mt-6 inline-flex rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-bold text-white"
          >
            Go to AI Planner
          </Link>
        </div>
      )}
    </div>
  );
}
