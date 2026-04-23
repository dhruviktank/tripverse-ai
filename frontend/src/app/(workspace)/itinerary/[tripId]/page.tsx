"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { tripApi, type TripData } from "@/lib/api";

export default function ItineraryDetailPage() {
  const router = useRouter();
  const params = useParams();
  const tripId = params.tripId as string;

  const [trip, setTrip] = useState<TripData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadTrip() {
      try {
        const data = await tripApi.get(tripId);
        setTrip(data.trip);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load trip");
      } finally {
        setLoading(false);
      }
    }
    loadTrip();
  }, [tripId]);

  async function handleSave() {
    if (!trip) return;
    setSaving(true);
    setSavedMessage(null);
    try {
      await tripApi.update(trip.id, {
        title: trip.title,
        trip_description: trip.trip_description,
        status: trip.status,
        itinerary_text: trip.itinerary_text,
      });
      setSavedMessage("Trip saved successfully!");
      setTimeout(() => setSavedMessage(null), 3000);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to save trip");
    } finally {
      setSaving(false);
    }
  }

  async function handleRegenerate() {
    if (!trip) return;
    setRegenerating(true);
    try {
      const result = await tripApi.regenerate(trip.id);
      setTrip(result.trip);
      setSavedMessage("Itinerary regenerated successfully!");
      setTimeout(() => setSavedMessage(null), 3000);
    } catch (err) {
      alert(
        err instanceof Error ? err.message : "Failed to regenerate itinerary",
      );
    } finally {
      setRegenerating(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 rounded-full border-4 border-[var(--primary)] border-t-transparent animate-spin" />
          <p className="mt-4 text-sm text-[var(--on-surface-variant)]">
            Loading itinerary...
          </p>
        </div>
      </div>
    );
  }

  if (error || !trip) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
        <p className="text-sm font-semibold text-red-700">
          {error || "Trip not found"}
        </p>
        <button
          onClick={() => router.push("/history")}
          className="mt-3 rounded-xl bg-red-600 px-4 py-2 text-sm font-bold text-white"
        >
          Back to History
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-6xl space-y-8">
      {/* Header */}
      <header className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs font-bold tracking-[0.16em] text-[var(--secondary)] uppercase">
            {trip.status} trip
          </p>
          <h1 className="mt-2 font-display text-5xl text-[var(--on-surface)]">
            {trip.title}
          </h1>
          <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
            {trip.starting_from} | {trip.travelers} traveler(s) | Budget: $
            {trip.budget_total || "–"}
          </p>
          {trip.dates && (
            <p className="mt-1 text-xs text-[var(--on-surface-variant)]">
              {trip.dates}
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleSave}
            disabled={saving}
            className="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-bold text-white transition hover:bg-[var(--primary-container)] disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="rounded-xl border border-[var(--outline-variant)] bg-white px-5 py-3 text-sm font-bold text-[var(--primary)] transition hover:bg-[var(--primary-fixed)] disabled:opacity-50"
          >
            {regenerating ? "Regenerating..." : "Regenerate"}
          </button>
        </div>
      </header>

      {/* Success Message */}
      {savedMessage && (
        <div className="rounded-xl border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-semibold text-green-700">{savedMessage}</p>
        </div>
      )}

      {/* Trip Description */}
      <section className="space-y-4">
        <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 shadow-[0_14px_35px_-26px_rgba(53,37,205,0.35)]">
          <h2 className="text-xl font-bold text-[var(--on-surface)]">
            Trip Overview
          </h2>
          <div className="mt-4 grid gap-6 md:grid-cols-4">
            <div>
              <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Trip Type
              </p>
              <p className="mt-2 font-semibold text-[var(--primary)] capitalize">
                {trip.budget}
              </p>
            </div>
            <div>
              <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Pace
              </p>
              <p className="mt-2 font-semibold text-[var(--primary)] capitalize">
                {trip.pace}
              </p>
            </div>
            <div>
              <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Travelers
              </p>
              <p className="mt-2 font-semibold text-[var(--primary)]">
                {trip.travelers}
              </p>
            </div>
            <div>
              <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Status
              </p>
              <p className="mt-2 font-semibold text-[var(--primary)] capitalize">
                {trip.status}
              </p>
            </div>
          </div>
          <div className="mt-6">
            <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
              Description
            </p>
            <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
              {trip.trip_description}
            </p>
          </div>
          {trip.preferences && (
            <div className="mt-4">
              <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Preferences
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {trip.preferences.split(",").map((pref) => (
                  <span
                    key={pref.trim()}
                    className="rounded-full bg-[var(--primary-fixed)] px-3 py-1 text-xs font-semibold text-[var(--primary)]"
                  >
                    {pref.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}
        </article>
      </section>

      {/* Itinerary Text */}
      <section className="space-y-4">
        <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 shadow-[0_14px_35px_-26px_rgba(53,37,205,0.35)]">
          <h2 className="text-xl font-bold text-[var(--on-surface)]">
            Your Itinerary
          </h2>
          {trip.itinerary_text ? (
            <div className="mt-4 prose prose-sm max-w-none rounded-xl bg-[var(--surface-container-low)] p-6">
              <style>{`
                .prose-viewer h1, .prose-viewer h2, .prose-viewer h3 {
                  color: var(--on-surface);
                  margin-top: 1.2em;
                  margin-bottom: 0.6em;
                  font-weight: 700;
                }
                .prose-viewer h1 { font-size: 1.8em; }
                .prose-viewer h2 { font-size: 1.4em; }
                .prose-viewer h3 { font-size: 1.2em; }
                .prose-viewer p, .prose-viewer li {
                  color: var(--on-surface-variant);
                  line-height: 1.6;
                  margin: 0.5em 0;
                }
                .prose-viewer ul, .prose-viewer ol {
                  margin-left: 1.5em;
                  margin: 0.8em 0;
                }
                .prose-viewer li { margin: 0.3em 0; }
                .prose-viewer strong { color: var(--primary); font-weight: 600; }
                .prose-viewer em { font-style: italic; color: var(--on-surface); }
                .prose-viewer code {
                  background: var(--surface);
                  padding: 0.2em 0.4em;
                  border-radius: 4px;
                  font-family: monospace;
                  color: var(--primary);
                }
                .prose-viewer blockquote {
                  border-left: 4px solid var(--primary);
                  padding-left: 1em;
                  margin: 1em 0;
                  color: var(--on-surface-variant);
                }
                .prose-viewer hr {
                  border: none;
                  border-top: 2px solid var(--outline-variant);
                  margin: 1.5em 0;
                }
              `}</style>
              <div className="prose-viewer text-[var(--on-surface)]">
                <ReactMarkdown>{trip.itinerary_text}</ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="mt-4 rounded-xl border border-dashed border-[var(--outline-variant)] bg-[var(--surface-container-low)] p-6 text-center">
              <p className="text-sm text-[var(--on-surface-variant)]">
                No itinerary generated yet.
              </p>
              <button
                onClick={handleRegenerate}
                className="mt-3 rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-bold text-white"
              >
                Generate Itinerary
              </button>
            </div>
          )}
        </article>
      </section>

      {/* Budget Info */}
      {(trip.budget_spent || trip.budget_total) && (
        <section className="space-y-4">
          <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 shadow-[0_14px_35px_-26px_rgba(53,37,205,0.35)]">
            <h2 className="text-xl font-bold text-[var(--on-surface)]">
              Budget
            </h2>
            <div className="mt-4 grid gap-6 md:grid-cols-2">
              <div>
                <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                  Total Budget
                </p>
                <p className="mt-2 text-2xl font-bold text-[var(--primary)]">
                  ${trip.budget_total || "–"}
                </p>
              </div>
              <div>
                <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                  Spent
                </p>
                <p className="mt-2 text-2xl font-bold text-[var(--on-surface)]">
                  ${trip.budget_spent || "–"}
                </p>
              </div>
            </div>
          </article>
        </section>
      )}

      {/* Back Button */}
      <div className="flex gap-3">
        <button
          onClick={() => router.push("/history")}
          className="rounded-xl border border-[var(--outline-variant)] bg-white px-5 py-3 text-sm font-bold text-[var(--on-surface)] transition hover:bg-[var(--surface-container-low)]"
        >
          ← Back to History
        </button>
      </div>
    </div>
  );
}
