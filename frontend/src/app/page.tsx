import Link from "next/link";

const featureCards = [
  {
    title: "AI Smart Itinerary",
    body: "Real-time route adjustments based on pace, weather, and local context.",
  },
  {
    title: "Smart Planning",
    body: "Optimize multi-city routing and reduce transfer friction across days.",
  },
  {
    title: "Personalization",
    body: "From vegan cafes to brutalist architecture, your profile steers every plan.",
  },
  {
    title: "Budget Sync",
    body: "Track spend and swap activities without sacrificing the overall experience.",
  },
];

export default function Home() {
  return (
    <div className="relative overflow-hidden bg-[var(--surface)] text-[var(--on-surface)]">
      <header className="sticky top-0 z-20 border-b border-[var(--outline-variant)]/60 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 sm:px-8">
          <div className="flex items-center gap-8">
            <p className="font-display text-3xl font-bold text-[var(--primary)]">TripVerse AI</p>
            <nav className="hidden gap-6 text-sm font-semibold text-[var(--on-surface-variant)] md:flex">
              <a href="#" className="text-[var(--primary)]">
                Explore
              </a>
              <a href="#">Planner</a>
              <a href="#">Community</a>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <button className="rounded-full bg-[var(--surface-container-low)] px-3 py-1 text-xs font-semibold text-[var(--on-surface-variant)]">
              Alerts
            </button>
            <button className="rounded-full bg-[var(--primary)] px-5 py-2 text-sm font-bold text-white">
              Sign in
            </button>
          </div>
        </div>
      </header>

      <section className="relative isolate px-4 pb-24 pt-14 sm:px-8 sm:pt-20">
        <div className="absolute -right-24 -top-28 h-72 w-72 rounded-full bg-[var(--secondary-container)]/35 blur-3xl" />
        <div className="absolute -bottom-24 -left-20 h-72 w-72 rounded-full bg-[var(--primary-fixed)] blur-3xl" />

        <div className="mx-auto grid w-full max-w-7xl gap-10 lg:grid-cols-[1fr_1.05fr] lg:items-center">
          <div>
            <p className="inline-flex rounded-full bg-[var(--secondary-container)]/30 px-4 py-2 text-sm font-semibold text-[var(--on-secondary-container)]">
              Experience Intelligent Serenity
            </p>
            <h1 className="mt-6 font-display text-5xl leading-[1.05] sm:text-7xl">
              Plan your perfect trip with AI.
            </h1>
            <p className="mt-5 max-w-xl text-base text-[var(--on-surface-variant)] sm:text-lg">
              TripVerse crafts personalized itineraries in seconds so you can stop
              spreadsheet juggling and start anticipating the trip.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/planner"
                className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-bold text-white transition hover:bg-[var(--primary-container)]"
              >
                Start Planning
              </Link>
              <Link
                href="/dashboard"
                className="rounded-xl border border-[var(--outline-variant)] bg-white px-6 py-3 text-sm font-bold text-[var(--on-surface)]"
              >
                View Example App
              </Link>
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/70 bg-white/70 p-4 shadow-[0_30px_70px_-34px_rgba(53,37,205,0.55)] backdrop-blur-xl">
           <div
              className="h-[360px] rounded-[1.4rem] bg-cover bg-center p-6 text-white sm:h-[430px]"
              style={{
                backgroundImage: "url('/landing/sunset.jpg')",
              }}
            >
              <div className="flex justify-end">
                <span className="rounded-full bg-white/30 px-3 py-1 text-xs font-semibold uppercase tracking-wide">
                  AI Recommended
                </span>
              </div>
              <div className="mt-44 rounded-2xl bg-white/90 p-4 text-[var(--on-surface)] sm:mt-56">
                <p className="text-sm font-bold">Amalfi Coast Express</p>
                <p className="mt-1 text-xs text-[var(--on-surface-variant)]">
                  7 days | 3 stops | AI optimized
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-[var(--surface-container-low)] px-4 py-20 sm:px-8">
        <div className="mx-auto w-full max-w-7xl">
          <div className="text-center">
            <h2 className="font-display text-5xl">Travel Smarter, Not Harder</h2>
            <p className="mx-auto mt-3 max-w-2xl text-sm text-[var(--on-surface-variant)] sm:text-base">
              Our AI engine handles complexity while your plan remains clear, editable,
              and grounded in your preferences.
            </p>
          </div>

          <div className="mt-10 grid gap-5 md:grid-cols-12">
            <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 md:col-span-8">
              <div className="grid gap-4 sm:grid-cols-[1fr_240px] sm:items-center">
                <div>
                  <p className="text-sm font-bold text-[var(--primary)]">AI Smart Itinerary</p>
                  <p className="mt-2 text-sm text-[var(--on-surface-variant)]">{featureCards[0].body}</p>
                </div>
                <div className="h-48 rounded-2xl" 
                  style={{
                    backgroundImage: "url('/landing/hiking.jpg')",
                    backgroundPosition: "center",
                    backgroundSize: "cover"
                  }}/>
              </div>
            </article>

            <article className="rounded-3xl bg-[var(--primary-container)] p-6 text-white md:col-span-4">
              <p className="text-sm font-bold">{featureCards[1].title}</p>
              <p className="mt-3 text-sm text-white/85">{featureCards[1].body}</p>
              <div className="mt-6 h-20 w-20 rounded-full bg-white/20" />
            </article>

            <article className="rounded-3xl border border-[var(--outline-variant)] bg-[var(--secondary-container)]/18 p-6 md:col-span-4">
              <p className="text-sm font-bold text-[var(--on-secondary-container)]">{featureCards[2].title}</p>
              <p className="mt-3 text-sm text-[var(--on-surface-variant)]">{featureCards[2].body}</p>
            </article>

            <article className="rounded-3xl border border-[var(--outline-variant)] bg-white p-6 md:col-span-8">
              <p className="text-sm font-bold">{featureCards[3].title}</p>
              <p className="mt-3 max-w-2xl text-sm text-[var(--on-surface-variant)]">{featureCards[3].body}</p>
              <div className="mt-6 flex h-24 w-24 items-center justify-center rounded-full border-8 border-[var(--primary-fixed)] border-t-[var(--primary)] text-sm font-black text-[var(--primary)]">
                85%
              </div>
            </article>
          </div>
        </div>
      </section>

      <section className="px-4 py-24 sm:px-8">
        <div className="mx-auto w-full max-w-4xl rounded-[2rem] border border-white/70 bg-white/80 p-10 text-center shadow-[0_24px_60px_-40px_rgba(53,37,205,0.65)] backdrop-blur-xl">
          <h3 className="font-display text-4xl">Ready to find your serenity?</h3>
          <p className="mx-auto mt-3 max-w-xl text-sm text-[var(--on-surface-variant)] sm:text-base">
            Join 50,000+ travelers using AI-powered planning instead of manual travel spreadsheets.
          </p>
          <div className="mx-auto mt-8 flex max-w-md flex-col gap-3 sm:flex-row">
            <input
              className="h-12 flex-1 rounded-xl border border-[var(--outline-variant)] bg-white px-4 text-sm outline-none focus:border-[var(--primary)]"
              placeholder="Enter your email"
            />
            <button className="h-12 rounded-xl bg-[var(--primary)] px-6 text-sm font-bold text-white">
              Get Started
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
