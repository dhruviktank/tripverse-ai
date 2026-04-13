export default function Home() {
  return (
    <div className="relative isolate overflow-hidden px-5 py-8 sm:px-10 sm:py-10 lg:px-14">
      <div className="mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded-3xl border border-white/40 bg-white/70 p-6 shadow-[0_20px_60px_-28px_rgba(5,46,37,0.45)] backdrop-blur-md sm:p-10">
          <p className="mb-4 inline-flex rounded-full bg-[var(--teal-soft)] px-4 py-1 text-xs font-semibold tracking-[0.22em] text-[var(--teal-deep)] uppercase">
            TravelVerse AI Planner
          </p>
          <h1 className="font-display text-4xl leading-tight text-[var(--ink)] sm:text-5xl lg:text-6xl">
            Plan smarter trips in minutes.
          </h1>
          <p className="mt-4 max-w-2xl text-base text-[var(--ink-muted)] sm:text-lg">
            Share a vibe, budget, and dates. Your AI co-pilot drafts routes,
            local food stops, and realistic daily pacing so you can just pack
            and go.
          </p>

          <form className="mt-8 grid gap-4 rounded-2xl border border-[var(--line)] bg-white/90 p-4 shadow-sm sm:grid-cols-2 sm:p-5">
            <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--ink)] sm:col-span-2">
              What kind of trip are you craving?
              <input
                placeholder="Example: 7 days in Japan with anime cafes and nature views"
                className="h-11 rounded-xl border border-[var(--line)] bg-[var(--paper)] px-3 text-sm font-medium text-[var(--ink)] outline-none transition focus:border-[var(--teal-deep)]"
              />
            </label>
            <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--ink)]">
              Budget Range
              <select className="h-11 rounded-xl border border-[var(--line)] bg-[var(--paper)] px-3 text-sm font-medium text-[var(--ink)] outline-none transition focus:border-[var(--teal-deep)]">
                <option>Value explorer</option>
                <option>Balanced</option>
                <option>Luxury moments</option>
              </select>
            </label>
            <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--ink)]">
              Pace
              <select className="h-11 rounded-xl border border-[var(--line)] bg-[var(--paper)] px-3 text-sm font-medium text-[var(--ink)] outline-none transition focus:border-[var(--teal-deep)]">
                <option>Relaxed</option>
                <option>Balanced</option>
                <option>High energy</option>
              </select>
            </label>
            <button
              type="button"
              className="sm:col-span-2 inline-flex h-12 items-center justify-center rounded-xl bg-[var(--teal-deep)] px-5 text-sm font-semibold tracking-wide text-white transition hover:-translate-y-0.5 hover:bg-[var(--teal-mid)]"
            >
              Generate My First Draft
            </button>
          </form>

          <div className="mt-8 grid gap-3 text-sm sm:grid-cols-3">
            {[
              "Adaptive itinerary + map",
              "Smart budget breakdown",
              "Food and culture recommendations",
            ].map((item) => (
              <div
                key={item}
                className="rounded-xl border border-[var(--line)] bg-[var(--paper)] px-4 py-3 text-[var(--ink-muted)]"
              >
                {item}
              </div>
            ))}
          </div>
        </section>

        <aside className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
          <article className="rounded-3xl bg-[var(--teal-deep)] p-6 text-white shadow-[0_20px_50px_-26px_rgba(7,72,71,0.65)]">
            <p className="text-xs tracking-[0.2em] uppercase text-white/70">
              Active Plan
            </p>
            <h2 className="mt-3 font-display text-3xl leading-tight">
              Lisbon + Porto
            </h2>
            <p className="mt-2 text-sm text-white/80">
              6 days, spring weather, food-first route with train connections.
            </p>
            <div className="mt-5 rounded-xl bg-white/14 p-4 text-sm">
              Day 3 highlights: Alfama walk, Time Out Market, sunset at Miradouro.
            </div>
          </article>

          <article className="rounded-3xl border border-white/40 bg-white/80 p-6 shadow-[0_16px_45px_-30px_rgba(3,31,45,0.45)] backdrop-blur-md">
            <p className="text-xs font-semibold tracking-[0.2em] text-[var(--ink-muted)] uppercase">
              Recent Searches
            </p>
            <ul className="mt-4 space-y-3 text-sm text-[var(--ink)]">
              <li className="rounded-xl border border-[var(--line)] bg-[var(--paper)] px-3 py-2">
                Solo culinary weekend in Bangkok
              </li>
              <li className="rounded-xl border border-[var(--line)] bg-[var(--paper)] px-3 py-2">
                Family-friendly Italy for 10 days
              </li>
              <li className="rounded-xl border border-[var(--line)] bg-[var(--paper)] px-3 py-2">
                Budget Europe rail route in June
              </li>
            </ul>
          </article>
        </aside>
      </div>
    </div>
  );
}
