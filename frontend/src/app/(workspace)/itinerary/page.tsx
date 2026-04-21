"use client";

import { useMemo, useState } from "react";

type ActivityType = "transportation" | "experience" | "dining";

type ItineraryActivity = {
  id: string;
  time: string;
  title: string;
  type: ActivityType;
  description: string;
  duration: string;
  meta: string;
  actionLabel: string;
};

type ItineraryDay = {
  day: number;
  title: string;
  activities: ItineraryActivity[];
  food: ItineraryActivity[];
  notes: string[];
};

type ItineraryPayload = {
  tripName: string;
  dates: string;
  travelers: string;
  budgetSpent: string;
  budgetTotal: string;
  weather: string;
  weatherMeta: string;
  days: ItineraryDay[];
};

const itineraryJson: ItineraryPayload = {
  tripName: "Amalfi Coast Adventure",
  dates: "Oct 12 - Oct 18, 2024",
  travelers: "2 Adults",
  budgetSpent: "2,450",
  budgetTotal: "5,000",
  weather: "24C",
  weatherMeta: "Mostly sunny | Wind 12km/h | Humidity 45%",
  days: [
    {
      day: 1,
      title: "Arrival & Coastal Charm",
      activities: [
        {
          id: "d1-a1",
          time: "09:30 AM",
          title: "Private Transfer to Positano",
          type: "transportation",
          description:
            "Meet your driver at Naples International Airport for a scenic ride across the coast.",
          duration: "1.5h",
          meta: "EUR 120",
          actionLabel: "View Booking",
        },
      ],
      food: [
        {
          id: "d1-f1",
          time: "01:00 PM",
          title: "Lunch at La Sponda",
          type: "dining",
          description:
            "Authentic Neapolitan cuisine in one of Positano's most iconic terrace restaurants.",
          duration: "Fine Dining",
          meta: "4.8 Rating",
          actionLabel: "Reserve Table",
        },
      ],
      notes: [
        "Keep the first evening light to recover from travel.",
        "Sunset viewpoint walk around 6:15 PM for better crowd flow.",
      ],
    },
    {
      day: 2,
      title: "Capri by Sea",
      activities: [
        {
          id: "d2-a1",
          time: "10:00 AM",
          title: "Private Boat Tour to Capri",
          type: "experience",
          description:
            "A full-day excursion around Capri with marina stops and flexible time windows.",
          duration: "6h",
          meta: "Max 6",
          actionLabel: "View Details",
        },
      ],
      food: [
        {
          id: "d2-f1",
          time: "02:30 PM",
          title: "Seafood Tasting in Marina Grande",
          type: "dining",
          description:
            "Fresh catch tasting menu with local citrus pairings by the harbor.",
          duration: "Casual Dining",
          meta: "4.6 Rating",
          actionLabel: "Modify Booking",
        },
      ],
      notes: [
        "Regenerate weather-safe alternatives for rough sea conditions.",
        "Add one flexible slot for shopping or extra island walk.",
      ],
    },
  ],
};

const chipStyles: Record<ActivityType, string> = {
  transportation: "bg-[var(--secondary-container)]/30 text-[var(--on-secondary-container)]",
  experience: "bg-[var(--primary-fixed)] text-[var(--primary)]",
  dining: "bg-orange-100 text-orange-700",
};

function SurfaceCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <article
      className={`rounded-2xl border border-[var(--outline-variant)] bg-white p-4 shadow-[0_10px_28px_-22px_rgba(53,37,205,0.38)] ${className}`}
    >
      {children}
    </article>
  );
}

function ActionButton({
  label,
  variant = "primary",
  onClick,
}: {
  label: string;
  variant?: "primary" | "ghost";
  onClick?: () => void;
}) {
  const style =
    variant === "primary"
      ? "bg-[var(--primary)] text-white hover:bg-[var(--primary-container)]"
      : "border border-[var(--outline-variant)] bg-white text-[var(--on-surface)] hover:bg-[var(--surface-container-low)]";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${style}`}
    >
      {label}
    </button>
  );
}

function ScenicBlock({ type }: { type: ActivityType }) {
  const gradient =
    type === "transportation"
      ? "linear-gradient(135deg,#90cdf8,#2f6fd8)"
      : type === "experience"
        ? "linear-gradient(135deg,#7cc7c3,#1f7e85)"
        : "linear-gradient(135deg,#f3cf7a,#e58f3f)";

  return (
    <div className="relative h-30 w-full overflow-hidden rounded-xl" style={{ background: gradient }}>
      <div className="absolute -left-6 -top-6 h-16 w-16 rounded-full bg-white/22" />
      <div className="absolute -bottom-8 right-4 h-20 w-20 rounded-full bg-black/8" />
      <div className="absolute bottom-3 left-3 h-2 w-20 rounded-full bg-white/65" />
    </div>
  );
}

function ItineraryCard({ activity }: { activity: ItineraryActivity }) {
  return (
    <SurfaceCard className="grid gap-3 sm:grid-cols-[170px_1fr] sm:items-start">
      <ScenicBlock type={activity.type} />

      <div>
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-[var(--primary)] px-2.5 py-1 text-[11px] font-bold text-white">
            {activity.time}
          </span>
          <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase ${chipStyles[activity.type]}`}>
            {activity.type}
          </span>
        </div>

        <h3 className="text-xl font-bold text-[var(--on-surface)]">{activity.title}</h3>
        <p className="mt-1 text-sm text-[var(--on-surface-variant)]">{activity.description}</p>

        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-xs text-[var(--on-surface-variant)]">
          <p>
            {activity.duration} | {activity.meta}
          </p>
          <button type="button" className="font-semibold text-[var(--primary)] hover:underline">
            {activity.actionLabel}
          </button>
        </div>
      </div>
    </SurfaceCard>
  );
}

export default function ItineraryPage() {
  const [data, setData] = useState<ItineraryPayload>(itineraryJson);
  const [modifyMode, setModifyMode] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  const totalItems = useMemo(
    () => data.days.reduce((acc, day) => acc + day.activities.length + day.food.length, 0),
    [data.days],
  );

  function handleSave() {
    setSavedAt(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
  }

  function handleRegenerate() {
    setData((prev) => {
      const next = structuredClone(prev);
      if (next.days[0]?.activities[0]) {
        next.days[0].activities[0].description =
          "Meet your driver at Naples International Airport with an optimized scenic route and faster check-in timing.";
      }
      next.days = next.days.map((day) => ({
        ...day,
        notes: day.notes.map((note, idx) => (idx === 0 ? `${note} (AI refined)` : note)),
      }));
      return next;
    });
  }

  function updateNote(dayIndex: number, noteIndex: number, value: string) {
    setData((prev) => ({
      ...prev,
      days: prev.days.map((day, dIdx) =>
        dIdx !== dayIndex
          ? day
          : {
              ...day,
              notes: day.notes.map((note, nIdx) => (nIdx === noteIndex ? value : note)),
            },
      ),
    }));
  }

  return (
    <div className="mx-auto grid w-full max-w-7xl gap-6 xl:grid-cols-[1fr_290px]">
      <section>
        <header className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="font-display text-5xl text-[var(--on-surface)]">{data.tripName}</h1>
            <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
              {data.dates} | {data.travelers}
            </p>
            <p className="mt-1 text-xs text-[var(--on-surface-variant)]">{totalItems} planned items</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <ActionButton label="Save" onClick={handleSave} />
            <ActionButton label="Regenerate" variant="ghost" onClick={handleRegenerate} />
            <ActionButton
              label={modifyMode ? "Finish Modifying" : "Modify"}
              variant="ghost"
              onClick={() => setModifyMode((prev) => !prev)}
            />
          </div>
        </header>

        {savedAt && (
          <p className="mb-5 text-xs font-semibold text-[var(--primary)]">Saved at {savedAt}</p>
        )}

        <div className="space-y-8">
          {data.days.map((day, dayIndex) => (
            <section key={day.day} className="relative pl-5 sm:pl-8">
              <div className="absolute left-2 top-0 h-full w-px bg-[var(--outline-variant)]/70 sm:left-3" />
              <div className="absolute left-0 top-1 inline-flex h-6 w-6 items-center justify-center rounded-full bg-[var(--primary)] text-xs font-bold text-white sm:left-[1px]">
                {day.day}
              </div>

              <h2 className="mb-4 text-3xl font-bold text-[var(--on-surface)]">Day {day.day}: {day.title}</h2>

              <div className="space-y-3">
                {day.activities.map((item) => (
                  <ItineraryCard key={item.id} activity={item} />
                ))}

                {day.food.map((item) => (
                  <ItineraryCard key={item.id} activity={item} />
                ))}
              </div>

              <SurfaceCard className="mt-3">
                <p className="text-xs font-bold tracking-[0.14em] text-[var(--on-surface-variant)] uppercase">Notes</p>
                <div className="mt-2 space-y-2">
                  {day.notes.map((note, noteIndex) =>
                    modifyMode ? (
                      <input
                        key={`${day.day}-note-${noteIndex}`}
                        value={note}
                        onChange={(event) => updateNote(dayIndex, noteIndex, event.target.value)}
                        className="h-10 w-full rounded-lg border border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-3 text-sm outline-none focus:border-[var(--primary)]"
                      />
                    ) : (
                      <p
                        key={`${day.day}-note-${noteIndex}`}
                        className="rounded-lg bg-[var(--surface-container-low)] px-3 py-2 text-sm text-[var(--on-surface-variant)]"
                      >
                        {note}
                      </p>
                    ),
                  )}
                </div>
              </SurfaceCard>
            </section>
          ))}
        </div>
      </section>

      <aside className="space-y-4">
        <SurfaceCard>
          <div className="mb-3 h-22 rounded-xl bg-[linear-gradient(135deg,#5ea2b2,#2b6e82)]" />
          <p className="text-sm font-bold text-[var(--on-surface)]">Amalfi Coast, Italy</p>
          <p className="mt-1 text-xs text-[var(--on-surface-variant)]">{data.dates}</p>
          <div className="mt-3 rounded-xl bg-[var(--surface-container-low)] px-3 py-2 text-sm">
            <p className="text-xs text-[var(--on-surface-variant)]">Budget Spent</p>
            <p className="font-semibold text-[var(--on-surface)]">EUR {data.budgetSpent} / EUR {data.budgetTotal}</p>
          </div>
          <div className="mt-3 rounded-xl border border-[var(--outline-variant)] px-3 py-2 text-xs text-[var(--on-surface-variant)]">
            {data.weather} | {data.weatherMeta}
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <p className="text-xs font-bold tracking-[0.14em] text-[var(--on-surface-variant)] uppercase">Itinerary Tools</p>
          <div className="mt-3 space-y-2">
            <ActionButton label="Regenerate Day" variant="ghost" onClick={handleRegenerate} />
            <ActionButton label="Modify" variant="ghost" onClick={() => setModifyMode((prev) => !prev)} />
            <ActionButton label="Save" onClick={handleSave} />
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <div className="h-30 rounded-xl bg-[linear-gradient(140deg,#5daec1,#236f84)]" />
          <button
            type="button"
            className="mt-3 h-10 w-full rounded-lg bg-[var(--on-surface)] text-sm font-semibold text-white"
          >
            Open Interactive Map
          </button>
        </SurfaceCard>
      </aside>
    </div>
  );
}
