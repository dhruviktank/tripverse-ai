"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { tripApi, PlanStreamEvent } from "@/lib/api";
import TripPlanViewer, { type TripPlanData } from "@/components/trip-plan-viewer";

type TripApiResponse = {
  success: boolean;
  plan?: TripPlanData;
  error?: string;
  errors?: string[] | null;
  validation?: PlanStreamEvent["validation"];
  requires_confirmation?: boolean;
  requires_destination?: boolean;
};

const preferenceOptions = [
  "Adventure",
  "Food",
  "Nightlife",
  "Relax",
  "Culture",
  "Nature",
];

export default function PlannerPage() {
  const router = useRouter();
  const [tripDescription, setTripDescription] = useState("");
  const [budget, setBudget] = useState("Balanced");
  const [pace, setPace] = useState("Balanced");
  const [startingFrom, setStartingFrom] = useState("");
  const [duration, setDuration] = useState(7);
  const [preferences, setPreferences] = useState<string[]>(["Food", "Relax"]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [response, setResponse] = useState<TripApiResponse | null>(null);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);
  const [streamPhase, setStreamPhase] = useState<"idle" | "itinerary" | "extras" | "complete">("idle");
  const [confirmingIntent, setConfirmingIntent] = useState(false);

  function togglePreference(item: string) {
    setPreferences((prev) =>
      prev.includes(item)
        ? prev.filter((entry) => entry !== item)
        : [...prev, item],
    );
  }

  async function runPlanning(confirmIntent = false) {
    setLoading(true);
    setResponse(null);
    setSavedMessage(null);
    setStreamPhase("idle");
    setConfirmingIntent(false);

    try {
      await tripApi.planStream(
        {
          trip_description: tripDescription,
          duration_days: duration,
          preferences,
          budget,
          pace,
          starting_from: startingFrom,
          confirm_intent: confirmIntent,
        },
        (eventData: PlanStreamEvent) => {
          if (eventData.event === "validation") {
            setLoading(false);
            setResponse({
              success: false,
              error: eventData.error || "Unable to validate request",
              validation: eventData.validation,
              requires_confirmation: eventData.requires_confirmation,
              requires_destination: eventData.requires_destination,
            });
            setConfirmingIntent(Boolean(eventData.requires_confirmation));
            return;
          }

          if (eventData.event === "itinerary") {
            setStreamPhase("itinerary");
            setResponse((prev) => ({
              success: true,
              plan: {
                ...(prev?.plan || {}),
                ...(eventData.plan as TripPlanData),
              },
            }));
            return;
          }

          if (eventData.event === "extras") {
            setStreamPhase("extras");
            setResponse((prev) => ({
              success: true,
              plan: {
                ...(prev?.plan || {}),
                ...(eventData.plan as TripPlanData),
              },
            }));
            return;
          }

          if (eventData.event === "complete") {
            setStreamPhase("complete");
            setResponse({
              success: true,
              plan: eventData.plan as TripPlanData,
              errors: eventData.errors || null,
            });
            setConfirmingIntent(false);
            return;
          }

          if (eventData.event === "error") {
            setResponse({
              success: false,
              error: eventData.error || "Unable to generate plan",
              errors: eventData.errors || null,
            });
          }
        },
      );
    } catch (error) {
      setResponse({
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Unable to connect to backend",
      });
      setConfirmingIntent(false);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runPlanning(false);
  }

  async function handleConfirmIntentYes() {
    await runPlanning(true);
  }

  function handleConfirmIntentNo() {
    setConfirmingIntent(false);
    setResponse((prev) =>
      prev
        ? {
            ...prev,
            error: "Generation cancelled. Update your request if you want a different trip plan.",
            requires_confirmation: false,
          }
        : prev,
    );
  }

  async function handleSaveTrip() {
    if (!response?.success || !response.plan) return;
    setSaving(true);
    setSavedMessage(null);

    try {
      const result = await tripApi.save({
        title: tripDescription || "Untitled Trip",
        trip_description: tripDescription,
        budget,
        pace,
        starting_from: startingFrom,
        preferences: preferences.join(", "),
        dates: `${duration} days`,
        itinerary_data: response.plan,
        itinerary_text: JSON.stringify(response.plan),
        status: "upcoming",
        travelers: 1,
      });
      setSavedMessage(result.message || "Trip saved!");
      setTimeout(() => router.push("/history"), 1500);
    } catch (error) {
      setSavedMessage(
        error instanceof Error ? error.message : "Failed to save trip",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <header>
        <h1 className="font-display text-5xl text-[var(--on-surface)]">
          Plan New Trip
        </h1>
        <p className="mt-2 text-base text-[var(--on-surface-variant)]">
          Design your next adventure with AI-assisted personalization.
        </p>
      </header>

      {/* ── Form: only the inputs + generate button ── */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid gap-5 md:grid-cols-12">
          {/* Left column */}
          <section className="space-y-5 md:col-span-8">
            <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-5 shadow-[0_14px_35px_-26px_rgba(53,37,205,0.35)]">
              <label className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Destination vibe
              </label>
              <input
                value={tripDescription}
                onChange={(e) => setTripDescription(e.target.value)}
                placeholder="Example: Kyoto temples + modern food scenes"
                className="mt-3 h-12 w-full rounded-xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-4 text-sm outline-none transition focus:border-[var(--primary)]"
                required
              />
              <p className="mt-3 text-xs text-[var(--on-surface-variant)]">
                Trending: Bali, Rome, Lisbon
              </p>
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
                    onChange={(e) => setDuration(Number(e.target.value))}
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
                  onChange={(e) => setStartingFrom(e.target.value)}
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
                  {loading
                    ? streamPhase === "extras"
                      ? "Building food, budget and safety tips..."
                      : "Generating day-by-day itinerary..."
                    : "Ready to generate with AI"}
                </p>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-white">
                  <div
                    className={`h-full bg-[linear-gradient(90deg,#57dffe,#4f46e5)] transition-all ${
                      loading ? "w-2/3 animate-pulse" : "w-1/5"
                    }`}
                  />
                </div>
              </div>
            </article>
          </section>
          {/* /Left column */}

          {/* Right column */}
          <section className="space-y-5 md:col-span-4">
            <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-5">
              <label className="text-xs font-bold tracking-[0.16em] text-[var(--on-surface-variant)] uppercase">
                Budget range
              </label>
              <select
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
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
                onChange={(e) => setPace(e.target.value)}
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
          </section>
          {/* /Right column */}
        </div>
        {/* /grid */}
      </form>
      {/* /form — response lives OUTSIDE so Save never triggers form submit */}

      {/* ── Full-Width Markdown Response Section ── */}
      {response && (
        <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 shadow-[0_14px_35px_-26px_rgba(53,37,205,0.35)]">
          {response.success && response.plan ? (
            <div className="space-y-4">
              <div className="flex items-start justify-between border-b border-[var(--outline-variant)] pb-4">
                <div>
                  <p className="text-xs font-bold tracking-[0.16em] text-[var(--primary)] uppercase">
                    Generated Plan
                  </p>
                  <h3 className="mt-2 text-2xl font-bold text-[var(--on-surface)]">
                    Your AI-Powered Trip Plan
                  </h3>
                </div>
                <div className="text-right">
                  <p className="text-xs text-[var(--on-surface-variant)]">
                    <span className="font-semibold">Sources:</span>{" "}
                    {response.plan.context_sources ?? 0}
                  </p>
                </div>
              </div>

              {loading && streamPhase !== "complete" && (
                <div className="rounded-xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] p-4 text-sm text-[var(--on-surface-variant)]">
                  {streamPhase === "extras"
                    ? "Itinerary ready. Generating food, budget and safety sections..."
                    : "Generating itinerary..."}
                </div>
              )}

              <TripPlanViewer plan={response.plan} compact />

              {/* Save Trip Button */}
              {streamPhase === "complete" ? (
                <button
                  type="button"
                  onClick={handleSaveTrip}
                  disabled={saving}
                  className="w-full rounded-xl bg-emerald-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-emerald-700 disabled:opacity-60"
                >
                  {saving ? "Saving..." : "💾 Save Trip to History"}
                </button>
              ) : (
                <div className="rounded-xl border border-dashed border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-5 py-4 text-center text-sm text-[var(--on-surface-variant)]">
                  Loading Food Culture Budget and Safety tips stay tuned...
                </div>
              )}

              {savedMessage && (
                <p
                  className={`text-center text-sm font-semibold ${
                    savedMessage.includes("Failed") ||
                    savedMessage.includes("error")
                      ? "text-red-600"
                      : "text-emerald-600"
                  }`}
                >
                  {savedMessage}
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-3 text-sm">
              {response.validation ? (
                <div className="rounded-2xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] p-4 text-[var(--on-surface)]">
                  <p className="text-xs font-bold tracking-[0.16em] text-[var(--primary)] uppercase">
                    Request Clarification
                  </p>
                  <p className="mt-2 text-sm leading-relaxed">
                    {response.error || "Please refine your trip request to continue."}
                  </p>
                  {response.requires_destination && (
                    <p className="mt-2 text-xs text-[var(--on-surface-variant)]">
                      Tip: add a destination name to continue planning.
                    </p>
                  )}
                  {confirmingIntent && (
                    <div className="mt-3 flex gap-2">
                      <button
                        type="button"
                        onClick={handleConfirmIntentYes}
                        className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-bold text-white transition hover:bg-emerald-700"
                      >
                        Yes, continue
                      </button>
                      <button
                        type="button"
                        onClick={handleConfirmIntentNo}
                        className="rounded-lg border border-[var(--outline-variant)] bg-white px-4 py-2 text-xs font-bold text-[var(--on-surface)] transition hover:bg-[var(--surface-container-low)]"
                      >
                        No
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">
                  <p className="font-semibold">Unable to generate plan</p>
                  <p className="mt-1">{response.error || "Unknown backend error"}</p>
                  {response.errors && response.errors.length > 0 && (
                    <ul className="mt-2 list-disc pl-5">
                      {response.errors.map((item, idx) => (
                        <li key={`${item}-${idx}`}>{item}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          )}
        </article>
      )}
    </div>
  );
}
