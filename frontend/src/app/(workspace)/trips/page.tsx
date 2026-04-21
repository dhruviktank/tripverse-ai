const timeline = [
  {
    day: "01",
    title: "Arrival & Sunset Magic",
    subtitle: "Settling into the volcanic paradise",
    items: [
      {
        time: "14:00",
        type: "Check-in",
        name: "Celestial Suites Resort",
        details: "Luxury suite check-in with panoramic caldera views.",
      },
      {
        time: "17:30",
        type: "Experience",
        name: "Oia Castle Sunset Path",
        details: "Marble alley walk and sunset viewpoints over the caldera.",
      },
    ],
  },
  {
    day: "02",
    title: "Volcanic Odyssey",
    subtitle: "Exploring the caldera by sea",
    items: [
      {
        time: "10:00",
        type: "Activity",
        name: "Caldera Catamaran Cruise",
        details: "Swim stops, hot springs, and a relaxed island lunch route.",
      },
    ],
  },
];

export default function TripsPage() {
  return (
    <div className="mx-auto w-full max-w-7xl space-y-8">
      <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-bold tracking-[0.16em] text-[var(--secondary)] uppercase">
            Current Plan
          </p>
          <h1 className="mt-2 font-display text-5xl">Santorini Dream Escape</h1>
          <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
            Sept 12 - Sept 18, 2024 | Oia, Greece
          </p>
        </div>
        <div className="flex gap-2">
          <button className="rounded-xl border border-[var(--outline-variant)] bg-white px-5 py-3 text-sm font-semibold">
            Regenerate
          </button>
          <button className="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-bold text-white">
            Save Trip
          </button>
        </div>
      </header>

      <div className="space-y-8">
        {timeline.map((day, i) => (
          <section key={day.day} className="grid gap-5 lg:grid-cols-[1fr_280px]">
            <div>
              <div className="mb-4 flex items-center gap-3">
                <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--primary)] text-lg font-bold text-white">
                  {day.day}
                </span>
                <div>
                  <h2 className="text-3xl font-bold text-[var(--on-surface)]">{day.title}</h2>
                  <p className="text-sm text-[var(--on-surface-variant)]">{day.subtitle}</p>
                </div>
              </div>

              <article className="overflow-hidden rounded-3xl border border-[var(--outline-variant)] bg-white shadow-[0_15px_40px_-30px_rgba(53,37,205,0.45)]">
                <div
                  className="h-48"
                  style={{
                    background:
                      i === 0
                        ? "linear-gradient(135deg,#5fb3ff,#1f69cb)"
                        : "linear-gradient(135deg,#4999d3,#2f6aa8)",
                  }}
                />
                <div className="space-y-5 p-5">
                  {day.items.map((item) => (
                    <div key={`${item.time}-${item.name}`} className="border-l-2 border-[var(--primary-fixed)] pl-4">
                      <p className="text-xs font-bold tracking-wide text-[var(--primary)] uppercase">
                        {item.time} | {item.type}
                      </p>
                      <h3 className="mt-1 text-xl font-semibold">{item.name}</h3>
                      <p className="mt-1 text-sm text-[var(--on-surface-variant)]">{item.details}</p>
                    </div>
                  ))}
                </div>
              </article>
            </div>

            <aside className="space-y-4">
              <article className="rounded-2xl border border-[var(--outline-variant)] bg-white p-4">
                <p className="text-xs font-bold tracking-wide text-[var(--primary)] uppercase">
                  Culinary Picks
                </p>
                <h4 className="mt-2 text-lg font-bold">Sunset Ammoudi Tavern</h4>
                <p className="mt-1 text-sm text-[var(--on-surface-variant)]">
                  Fresh seafood after the water edge walk, ideal for sunset timing.
                </p>
              </article>

              <article className="rounded-2xl border border-[var(--outline-variant)] bg-white p-4">
                <p className="text-xs font-bold tracking-wide text-[var(--secondary)] uppercase">
                  Planner Notes
                </p>
                <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
                  Book table reservations two days in advance. Request a rail-side
                  seat for evening segments.
                </p>
              </article>

              <article className="h-44 rounded-2xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] p-4">
                <p className="text-xs font-bold tracking-wide text-[var(--primary)] uppercase">Route Preview</p>
                <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
                  Estimated travel time 45m by boat. Total route distance 12 nautical miles.
                </p>
              </article>
            </aside>
          </section>
        ))}
      </div>
    </div>
  );
}
