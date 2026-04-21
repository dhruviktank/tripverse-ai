"use client";

import { FormEvent, useMemo, useState } from "react";

type TripPlan = {
  trip_description?: string;
  budget?: string;
  pace?: string;
  starting_from?: string;
  itinerary?: string;
  context_sources?: number;
};

type TripApiResponse = {
  success: boolean;
  plan?: TripPlan;
  error?: string;
  errors?: string[] | null;
};

const preferenceOptions = ["Adventure", "Food", "Nightlife", "Relax", "Culture", "Nature"];

export default function PlannerPage() {
  const [tripDescription, setTripDescription] = useState("");
  const [budget, setBudget] = useState("Balanced");
  const [pace, setPace] = useState("Balanced");
  const [startingFrom, setStartingFrom] = useState("");
  const [duration, setDuration] = useState(7);
  const [preferences, setPreferences] = useState<string[]>(["Food", "Relax"]);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<TripApiResponse | null>(null);

  const apiBaseUrl = useMemo(() => {
    const envUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    return envUrl && envUrl.trim() ? envUrl.trim() : "http://localhost:8000";
  }, []);

  function togglePreference(item: string) {
    setPreferences((prev) =>
      prev.includes(item) ? prev.filter((entry) => entry !== item) : [...prev, item],
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch(`${apiBaseUrl}/api/trips/plan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          trip_description: `${tripDescription}. Duration: ${duration} days. Preferences: ${preferences.join(", ")}`,
          budget,
          pace,
          starting_from: startingFrom,
        }),
      });

      const data = (await res.json()) as TripApiResponse;
      if (!res.ok) {
        setResponse({
          success: false,
          error: data.error || `Request failed with status ${res.status}`,
          errors: data.errors || null,
        });
      } else {
        setResponse(data);
      }
    } catch (error) {
      setResponse({
        success: false,
        error: error instanceof Error ? error.message : "Unable to connect to backend",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <header>
        <h1 className="font-display text-5xl text-[var(--on-surface)]">Plan New Trip</h1>
        <p className="mt-2 text-base text-[var(--on-surface-variant)]">
          Design your next adventure with AI-assisted personalization.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="grid gap-5 md:grid-cols-12">
        <section className="space-y-5 md:col-span-8">
          <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-5 shadow-[0_14px_35px_-26px_rgba(53,37,205,0.35)]">
            <label className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
              Destination vibe
            </label>
            <input
              value={tripDescription}
              onChange={(event) => setTripDescription(event.target.value)}
              placeholder="Example: Kyoto temples + modern food scenes"
              className="mt-3 h-12 w-full rounded-xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-4 text-sm outline-none transition focus:border-[var(--primary)]"
              required
            />
            <p className="mt-3 text-xs text-[var(--on-surface-variant)]">Trending: Bali, Rome, Lisbon</p>
          </article>

          <div className="grid gap-5 sm:grid-cols-2">
            <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-5">
              <label className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Duration
              </label>
              <div className="mt-3 flex items-center justify-between">
                <input
                  type="range"
                  min={1}
                  max={30}
                  value={duration}
                  onChange={(event) => setDuration(Number(event.target.value))}
                  className="w-full accent-[var(--primary)]"
                />
                <span className="ml-3 rounded-full bg-[var(--primary-fixed)] px-3 py-1 text-xs font-bold text-[var(--primary)]">
                  {duration} days
                </span>
              </div>
            </article>

            <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-5">
              <label className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Starting from
              </label>
              <input
                value={startingFrom}
                onChange={(event) => setStartingFrom(event.target.value)}
                placeholder="Example: New York"
                className="mt-3 h-12 w-full rounded-xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-4 text-sm outline-none transition focus:border-[var(--primary)]"
                required
              />
            </article>
          </div>

          <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-5">
            <p className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
              Travel preferences
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {preferenceOptions.map((item) => {
                const selected = preferences.includes(item);
                return (
                  <button
                    key={item}
                    type="button"
                    onClick={() => togglePreference(item)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                      selected
                        ? "bg-[var(--secondary-container)] text-[var(--on-secondary-container)]"
                        : "border border-[var(--outline-variant)] text-[var(--on-surface-variant)]"
                    }`}
                  >
                    {item}
                  </button>
                );
              })}
            </div>
          </article>

          <article className="rounded-3xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] p-6">
            <div className="mx-auto max-w-md text-center">
              <div className="mx-auto h-14 w-14 rounded-full border-2 border-[var(--primary)]/40 bg-white" />
              <p className="mt-4 text-base font-semibold text-[var(--primary)]">
                {loading ? "Analyzing destinations..." : "Ready to generate with AI"}
              </p>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-white">
                <div
                  className={`h-full bg-[linear-gradient(90deg,#57dffe,#4f46e5)] transition-all ${
                    loading ? "w-2/3" : "w-1/5"
                  }`}
                />
              </div>
            </div>
          </article>
        </section>

        <section className="space-y-5 md:col-span-4">
          <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-5">
            <label className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
              Budget range
            </label>
            <select
              value={budget}
              onChange={(event) => setBudget(event.target.value)}
              className="mt-3 h-12 w-full rounded-xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-4 text-sm outline-none"
            >
              <option>Value explorer</option>
              <option>Balanced</option>
              <option>Luxury moments</option>
            </select>

            <label className="mt-5 block text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
              Pace
            </label>
            <select
              value={pace}
              onChange={(event) => setPace(event.target.value)}
              className="mt-3 h-12 w-full rounded-xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-4 text-sm outline-none"
            >
              <option>Relaxed</option>
              <option>Balanced</option>
              <option>High energy</option>
            </select>

            <button
              type="submit"
              disabled={loading}
              className="mt-6 inline-flex h-12 w-full items-center justify-center rounded-xl bg-[var(--primary)] px-5 text-sm font-bold text-white transition hover:bg-[var(--primary-container)] disabled:opacity-60"
            >
              {loading ? "Generating..." : "Generate Trip with AI"}
            </button>
          </article>

          {response && (
            <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-4">
              {response.success && response.plan ? (
                <div className="space-y-2 text-sm">
                  <p className="font-bold text-[var(--primary)]">Generated Plan</p>
                  <p>
                    <span className="font-semibold">Route:</span> {response.plan.starting_from} -{" "}
                    {response.plan.trip_description}
                  </p>
                  <p>
                    <span className="font-semibold">Budget:</span> {response.plan.budget}
                  </p>
                  <p>
                    <span className="font-semibold">Pace:</span> {response.plan.pace}
                  </p>
                  <p>
                    <span className="font-semibold">Context Sources:</span>{" "}
                    {response.plan.context_sources ?? 0}
                  </p>
                  <div className="mt-2 rounded-xl bg-[var(--surface-container-low)] p-3 text-xs whitespace-pre-wrap">
                    {response.plan.itinerary || "No itinerary generated."}
                  </div>
                </div>
              ) : (
                <div className="space-y-2 text-sm text-red-700">
                  <p className="font-semibold">Unable to generate plan</p>
                  <p>{response.error || "Unknown backend error"}</p>
                  {response.errors && response.errors.length > 0 && (
                    <ul className="list-disc pl-5">
                      {response.errors.map((item, idx) => (
                        <li key={`${item}-${idx}`}>{item}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </article>
          )}
        </section>
      </form>
    </div>
  );
}
