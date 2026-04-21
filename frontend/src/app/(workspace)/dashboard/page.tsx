import Link from "next/link";

const quickStats = [
  { label: "Total Adventures", value: "12", note: "Since joining TripVerse" },
  { label: "Eco Score", value: "84%", note: "Estimated sustainability impact" },
];

const recentTrips = [
  { title: "Venice Getaway", date: "Oct 12 - Oct 18", tag: "Active" },
  { title: "Parisian Spring", date: "May 4 - May 10", tag: "City" },
  { title: "Kyoto Temples", date: "Nov 15 - Nov 22", tag: "Culture" },
];

export default function DashboardPage() {
  return (
    <div className="mx-auto w-full max-w-7xl space-y-8">
      <section className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold text-[var(--on-surface-variant)]">Hello, Alex</p>
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
            href="/trips"
            className="rounded-xl border border-[var(--outline-variant)] bg-white px-5 py-3 text-sm font-bold text-[var(--primary)]"
          >
            View Trips
          </Link>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-12">
        <article className="relative overflow-hidden rounded-3xl border border-indigo-200/40 bg-[linear-gradient(145deg,#4f46e5,#2f23bd)] p-7 text-white shadow-[0_24px_60px_-35px_rgba(53,37,205,0.7)] md:col-span-8">
          <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-cyan-300/20 blur-3xl" />
          <p className="inline-flex rounded-full bg-white/20 px-3 py-1 text-[11px] font-semibold tracking-wide uppercase">
            AI Recommendation
          </p>
          <h2 className="mt-4 max-w-2xl font-display text-4xl">A serene escape to the Amalfi Coast</h2>
          <p className="mt-3 max-w-xl text-sm text-white/90">
            Based on your saved preferences, this 7-day route balances coastal views,
            local food walks, and relaxed transit windows.
          </p>
          <div className="mt-6 flex gap-3">
            <button className="rounded-xl bg-white px-4 py-2 text-sm font-bold text-[var(--primary)]">Start Planning</button>
            <button className="rounded-xl border border-white/50 px-4 py-2 text-sm font-semibold">Estimated 4h setup</button>
          </div>
        </article>

        <div className="space-y-4 md:col-span-4">
          {quickStats.map((item) => (
            <article
              key={item.label}
              className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 shadow-[0_14px_35px_-28px_rgba(53,37,205,0.35)]"
            >
              <p className="text-4xl font-black text-[var(--primary)]">{item.value}</p>
              <p className="mt-2 text-base font-semibold text-[var(--on-surface)]">{item.label}</p>
              <p className="mt-1 text-sm text-[var(--on-surface-variant)]">{item.note}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-display text-3xl">Recent Trips</h3>
          <Link href="/history" className="text-sm font-bold text-[var(--primary)]">
            View all
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {recentTrips.map((trip, idx) => (
            <article
              key={trip.title}
              className="rounded-3xl border border-[var(--outline-variant)] bg-white p-4 shadow-[0_12px_30px_-22px_rgba(77,68,227,0.35)]"
            >
              <div
                className="mb-4 h-36 rounded-2xl"
                style={{
                  background:
                    idx === 0
                      ? "linear-gradient(135deg,#7cc0ff,#2f77e6)"
                      : idx === 1
                        ? "linear-gradient(135deg,#1a1f4d,#3f63d8)"
                        : "linear-gradient(135deg,#253955,#3a77b4)",
                }}
              />
              <p className="inline-flex rounded-full bg-[var(--secondary-container)]/40 px-3 py-1 text-xs font-semibold text-[var(--on-secondary-container)]">
                {trip.tag}
              </p>
              <h4 className="mt-3 text-xl font-bold text-[var(--on-surface)]">{trip.title}</h4>
              <p className="mt-1 text-sm text-[var(--on-surface-variant)]">{trip.date}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
