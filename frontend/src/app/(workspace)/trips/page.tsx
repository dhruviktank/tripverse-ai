"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { tripApi, type TripData } from "@/lib/api";

interface TimelineDay {
  day: string;
  title: string;
  items: Array<{
    time: string;
    type: string;
    name: string;
    details: string;
  }>;
}

function parseItineraryToTimeline(itineraryText: string | null): TimelineDay[] {
  if (!itineraryText) return [];

  // Simple parsing: extract day sections from markdown
  const dayRegex = /\*{0,2}Day\s+(\d+):\s*([^\n]+)\*{0,2}/gi;
  const matches = [...itineraryText.matchAll(dayRegex)];

  return matches.map((match) => ({
    day: String(parseInt(match[1])).padStart(2, "0"),
    title: match[2],
    items: [
      {
        time: "Full Day",
        type: "Activity",
        name: "Planned itinerary",
        details: "See full details in itinerary view",
      },
    ],
  }));
}

export default function TripsPage() {
  const { user } = useAuth();
  const [activeTrip, setActiveTrip] = useState<TripData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<TimelineDay[]>([]);

  useEffect(() => {
    async function loadActiveTrip() {
      try {
        const data = await tripApi.list("upcoming");
        if (data.trips.length > 0) {
          const trip = data.trips[0];
          setActiveTrip(trip);
          setTimeline(parseItineraryToTimeline(trip.itinerary_text));
        } else {
          setError("No upcoming trips found. Create one to see it here!");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load trips");
      } finally {
        setLoading(false);
      }
    }
    loadActiveTrip();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 rounded-full border-4 border-[var(--primary)] border-t-transparent animate-spin" />
          <p className="mt-4 text-sm text-[var(--on-surface-variant)]">
            Loading your trips...
          </p>
        </div>
      </div>
    );
  }

  if (error || !activeTrip) {
    return (
      <div className="rounded-3xl border border-dashed border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-6 py-16 text-center">
        <p className="font-display text-3xl text-[var(--primary)]">
          No upcoming trips
        </p>
        <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
          {error ||
            "Your upcoming trips will appear here. Create one to get started!"}
        </p>
        <Link
          href="/planner"
          className="mt-6 inline-block rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-bold text-white transition hover:bg-[var(--primary-container)]"
        >
          Plan a Trip
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl space-y-8">
      {/* Header */}
      <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-bold tracking-[0.16em] text-[var(--secondary)] uppercase">
            Current Plan
          </p>
          <h1 className="mt-2 font-display text-5xl text-[var(--on-surface)]">
            {activeTrip.title}
          </h1>
          <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
            {activeTrip.starting_from}
            {activeTrip.dates && ` | ${activeTrip.dates}`}
            {activeTrip.travelers &&
              ` | ${activeTrip.travelers} traveler${activeTrip.travelers !== 1 ? "s" : ""}`}
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            href={`/itinerary/${activeTrip.id}`}
            className="rounded-xl border border-[var(--outline-variant)] bg-white px-5 py-3 text-sm font-semibold text-[var(--on-surface)] transition hover:bg-[var(--surface-container-low)]"
          >
            Full Itinerary
          </Link>
          <Link
            href="/history"
            className="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-bold text-white transition hover:bg-[var(--primary-container)]"
          >
            View All Trips
          </Link>
        </div>
      </header>

      {/* Timeline */}
      {timeline.length > 0 ? (
        <div className="space-y-8">
          {timeline.map((day, i) => (
            <section
              key={day.day}
              className="grid gap-5 lg:grid-cols-[1fr_280px]"
            >
              <div>
                <div className="mb-4 flex items-center gap-3">
                  <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--primary)] text-lg font-bold text-white">
                    {day.day}
                  </span>
                  <div>
                    <h2 className="text-3xl font-bold text-[var(--on-surface)]">
                      {day.title}
                    </h2>
                  </div>
                </div>

                <article className="overflow-hidden rounded-3xl border border-[var(--outline-variant)] bg-white shadow-[0_15px_40px_-30px_rgba(53,37,205,0.45)]">
                  <div
                    className="h-48"
                    style={{
                      background:
                        i === 0
                          ? "linear-gradient(135deg,#5fb3ff,#1f69cb)"
                          : i === 1
                            ? "linear-gradient(135deg,#4999d3,#2f6aa8)"
                            : "linear-gradient(135deg,#3d7a9e,#2a5680)",
                    }}
                  />
                  <div className="space-y-5 p-5">
                    {day.items.map((item) => (
                      <div
                        key={`${item.time}-${item.name}`}
                        className="border-l-2 border-[var(--primary-fixed)] pl-4"
                      >
                        <p className="text-xs font-bold tracking-wide text-[var(--primary)] uppercase">
                          {item.time} | {item.type}
                        </p>
                        <h3 className="mt-1 text-xl font-semibold text-[var(--on-surface)]">
                          {item.name}
                        </h3>
                        <p className="mt-1 text-sm text-[var(--on-surface-variant)]">
                          {item.details}
                        </p>
                      </div>
                    ))}
                  </div>
                </article>
              </div>

              <aside className="space-y-4">
                <article className="rounded-2xl border border-[var(--outline-variant)] bg-white p-4">
                  <p className="text-xs font-bold tracking-wide text-[var(--primary)] uppercase">
                    Trip Info
                  </p>
                  <div className="mt-3 space-y-2 text-sm">
                    <div>
                      <p className="text-[11px] text-[var(--on-surface-variant)]">
                        Budget Type
                      </p>
                      <p className="font-semibold text-[var(--on-surface)] capitalize">
                        {activeTrip.budget}
                      </p>
                    </div>
                    <div>
                      <p className="text-[11px] text-[var(--on-surface-variant)]">
                        Pace
                      </p>
                      <p className="font-semibold text-[var(--on-surface)] capitalize">
                        {activeTrip.pace}
                      </p>
                    </div>
                    {activeTrip.budget_total && (
                      <div>
                        <p className="text-[11px] text-[var(--on-surface-variant)]">
                          Budget Total
                        </p>
                        <p className="font-semibold text-[var(--primary)]">
                          ${activeTrip.budget_total}
                        </p>
                      </div>
                    )}
                  </div>
                </article>
              </aside>
            </section>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-[var(--outline-variant)] bg-[var(--surface-container-low)] p-6 text-center">
          <p className="text-sm text-[var(--on-surface-variant)]">
            Itinerary timeline will appear here once trip details are loaded.
          </p>
        </div>
      )}
    </div>
  );
}
