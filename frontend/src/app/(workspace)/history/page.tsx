"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { tripApi, type TripData } from "@/lib/api";

export default function HistoryPage() {
  const [trips, setTrips] = useState<TripData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("newest");
  const [deleting, setDeleting] = useState<string | null>(null);
  const [togglingFav, setTogglingFav] = useState<string | null>(null);

  const loadTrips = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await tripApi.list(
        filter !== "all" ? filter : undefined,
        sortBy,
      );
      setTrips(data.trips);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load trips");
    } finally {
      setLoading(false);
    }
  }, [filter, sortBy]);

  useEffect(() => {
    loadTrips();
  }, [filter, sortBy, loadTrips]);

  async function handleDelete(tripId: string) {
    if (!confirm("Are you sure you want to delete this trip?")) return;
    setDeleting(tripId);
    try {
      await tripApi.delete(tripId);
      setTrips(trips.filter((t) => t.id !== tripId));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete trip");
    } finally {
      setDeleting(null);
    }
  }

  async function handleToggleFavorite(tripId: string) {
    setTogglingFav(tripId);
    try {
      const result = await tripApi.toggleFavorite(tripId);
      setTrips(trips.map((t) => (t.id === tripId ? result.trip : t)));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to toggle favorite");
    } finally {
      setTogglingFav(null);
    }
  }

  const cardGradients = [
    "linear-gradient(135deg,#6ac5f6,#1f8dd6)",
    "linear-gradient(135deg,#1e2b55,#3c4de0)",
    "linear-gradient(135deg,#245a4a,#6fbfa2)",
    "linear-gradient(135deg,#d67b6b,#a73c3c)",
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-8">
      <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="font-display text-5xl text-[var(--on-surface)]">
            Trip History
          </h1>
          <p className="mt-2 text-base text-[var(--on-surface-variant)]">
            Relive your past adventures curated by AI.
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded-lg border border-[var(--outline-variant)] bg-white px-4 py-2 text-sm font-medium outline-none transition focus:border-[var(--primary)]"
          >
            <option value="all">All Trips</option>
            <option value="upcoming">Upcoming</option>
            <option value="past">Past</option>
            <option value="favorites">Favorites</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-lg border border-[var(--outline-variant)] bg-white px-4 py-2 text-sm font-medium outline-none transition focus:border-[var(--primary)]"
          >
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
            <option value="budget_high">Budget: High</option>
            <option value="budget_low">Budget: Low</option>
          </select>
        </div>
      </header>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="mx-auto h-10 w-10 rounded-full border-4 border-[var(--primary)] border-t-transparent animate-spin" />
            <p className="mt-4 text-sm text-[var(--on-surface-variant)]">
              Loading your trips...
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-sm font-semibold text-red-700">{error}</p>
          <button
            onClick={loadTrips}
            className="mt-3 rounded-xl bg-red-600 px-4 py-2 text-sm font-bold text-white"
          >
            Retry
          </button>
        </div>
      )}

      {/* Trips Grid */}
      {!loading && !error && trips.length > 0 && (
        <section className="grid gap-5 md:grid-cols-3">
          {trips.map((trip, index) => {
            const createdDate = new Date(trip.created_at);
            const monthYear = createdDate.toLocaleDateString("en-US", {
              month: "short",
              year: "numeric",
            });

            return (
              <article
                key={trip.id}
                className="rounded-3xl border border-[var(--outline-variant)] bg-white shadow-[0_15px_35px_-28px_rgba(53,37,205,0.4)] overflow-hidden transition hover:shadow-[0_20px_50px_-28px_rgba(53,37,205,0.5)]"
              >
                <div
                  className="h-32 rounded-t-3xl"
                  style={
                    trip.thumbnail_url
                      ? {
                          backgroundImage: `url('${trip.thumbnail_url}')`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center'
                        }
                      : {
                          background: cardGradients[(trip.id?.length || 0) % cardGradients.length],
                        }
                  }
                />
                <div className="p-4">
                  <p className="inline-flex rounded-full bg-[var(--primary-fixed)] px-3 py-1 text-xs font-semibold text-[var(--primary)]">
                    {monthYear}
                  </p>
                  <h2 className="mt-3 text-2xl font-bold line-clamp-2">
                    {trip.title}
                  </h2>
                  <p className="text-sm text-[var(--on-surface-variant)]">
                    {trip.starting_from}
                  </p>

                  <div className="mt-5 grid grid-cols-2 gap-2 text-sm">
                    <div className="rounded-xl bg-[var(--surface-container-low)] p-3">
                      <p className="text-[11px] text-[var(--on-surface-variant)] uppercase">
                        Status
                      </p>
                      <p className="font-semibold text-[var(--primary)] capitalize">
                        {trip.status}
                      </p>
                    </div>
                    <div className="rounded-xl bg-[var(--surface-container-low)] p-3">
                      <p className="text-[11px] text-[var(--on-surface-variant)] uppercase">
                        Budget
                      </p>
                      <p className="font-semibold text-[var(--primary)]">
                        {trip.budget_total ? `$${trip.budget_total}` : "–"}
                      </p>
                    </div>
                  </div>

                  <div className="mt-5 flex gap-2">
                    <Link
                      href={`/itinerary/${trip.id}`}
                      className="flex-1 rounded-xl border border-[var(--outline-variant)] bg-white py-2 text-sm font-bold text-[var(--primary)] transition hover:bg-[var(--primary-fixed)]"
                    >
                      View
                    </Link>
                    <button
                      onClick={() => handleToggleFavorite(trip.id)}
                      disabled={togglingFav === trip.id}
                      className="rounded-xl border border-[var(--outline-variant)] bg-white px-3 py-2 text-lg transition hover:bg-[var(--primary-fixed)] disabled:opacity-50"
                      title={
                        trip.is_favorite
                          ? "Remove from favorites"
                          : "Add to favorites"
                      }
                    >
                      {trip.is_favorite ? "★" : "☆"}
                    </button>
                    <button
                      onClick={() => handleDelete(trip.id)}
                      disabled={deleting === trip.id}
                      className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm font-bold text-red-600 transition hover:bg-red-100 disabled:opacity-50"
                    >
                      {deleting === trip.id ? "..." : "🗑"}
                    </button>
                  </div>
                </div>
              </article>
            );
          })}
        </section>
      )}

      {/* Empty State */}
      {!loading && !error && trips.length === 0 && (
        <section className="rounded-3xl border border-dashed border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-6 py-16 text-center">
          <p className="font-display text-3xl text-[var(--primary)]">
            No trips found
          </p>
          <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
            {filter !== "all"
              ? `No ${filter} trips yet.`
              : "Your trip history appears here as you plan more with your AI assistant."}
          </p>
          <Link
            href="/planner"
            className="mt-6 inline-block rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-bold text-white transition hover:bg-[var(--primary-container)]"
          >
            Create Your First Trip
          </Link>
        </section>
      )}
    </div>
  );
}
