const tripHistory = [
  {
    month: "July 2024",
    title: "Amalfi Getaway",
    location: "Italy",
    duration: "7 Days",
    budget: "$4,200",
    tag: "Luxury",
  },
  {
    month: "May 2024",
    title: "Tokyo Neon",
    location: "Japan",
    duration: "10 Days",
    budget: "$2,850",
    tag: "Solo",
  },
  {
    month: "Oct 2023",
    title: "Yosemite Trails",
    location: "USA",
    duration: "4 Days",
    budget: "$1,100",
    tag: "Nature",
  },
];

export default function HistoryPage() {
  return (
    <div className="mx-auto w-full max-w-7xl">
      <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="font-display text-5xl text-[var(--on-surface)]">Trip History</h1>
          <p className="mt-2 text-base text-[var(--on-surface-variant)]">
            Relive your past adventures curated by AI.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="rounded-lg border border-[var(--outline-variant)] bg-white px-4 py-2 text-sm font-medium">
            Filter
          </button>
          <button className="rounded-lg border border-[var(--outline-variant)] bg-white px-4 py-2 text-sm font-medium">
            Sort by Date
          </button>
        </div>
      </header>

      <section className="grid gap-5 md:grid-cols-3">
        {tripHistory.map((trip, index) => (
          <article
            key={trip.title}
            className="rounded-3xl border border-[var(--outline-variant)] bg-white p-4 shadow-[0_15px_35px_-28px_rgba(53,37,205,0.4)]"
          >
            <div
              className="h-32 rounded-2xl"
              style={{
                background:
                  index === 0
                    ? "linear-gradient(135deg,#6ac5f6,#1f8dd6)"
                    : index === 1
                      ? "linear-gradient(135deg,#1e2b55,#3c4de0)"
                      : "linear-gradient(135deg,#245a4a,#6fbfa2)",
              }}
            />
            <p className="mt-4 inline-flex rounded-full bg-[var(--primary-fixed)] px-3 py-1 text-xs font-semibold text-[var(--primary)]">
              {trip.month}
            </p>
            <h2 className="mt-3 text-2xl font-bold">{trip.title}</h2>
            <p className="text-sm text-[var(--on-surface-variant)]">{trip.location}</p>

            <div className="mt-5 grid grid-cols-2 gap-2 text-sm">
              <div className="rounded-xl bg-[var(--surface-container-low)] p-3">
                <p className="text-[11px] text-[var(--on-surface-variant)] uppercase">Duration</p>
                <p className="font-semibold text-[var(--primary)]">{trip.duration}</p>
              </div>
              <div className="rounded-xl bg-[var(--surface-container-low)] p-3">
                <p className="text-[11px] text-[var(--on-surface-variant)] uppercase">Budget</p>
                <p className="font-semibold text-[var(--primary)]">{trip.budget}</p>
              </div>
            </div>

            <button className="mt-5 w-full rounded-xl border border-[var(--outline-variant)] bg-white py-2 text-sm font-bold text-[var(--primary)]">
              View Itinerary
            </button>
          </article>
        ))}
      </section>

      <section className="mt-10 rounded-3xl border border-dashed border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-6 py-16 text-center">
        <p className="font-display text-3xl text-[var(--primary)]">Ready for a new adventure?</p>
        <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
          Your completed trip history appears here as you plan more with your AI assistant.
        </p>
        <button className="mt-6 rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-bold text-white">
          Create AI Itinerary
        </button>
      </section>
    </div>
  );
}
