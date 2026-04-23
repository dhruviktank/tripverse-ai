"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";

type ShellProps = {
  children: ReactNode;
};

type NavItem = {
  href: string;
  label: string;
  icon: string;
};

const navItems: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: "DS" },
  { href: "/trips", label: "My Trips", icon: "MT" },
  { href: "/planner", label: "AI Planner", icon: "AI" },
  { href: "/history", label: "History", icon: "HS" },
  { href: "/itinerary", label: "Itinerary", icon: "IT" },
];

function isActivePath(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function WorkspaceShell({ children }: ShellProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((w) => w[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "??";

  return (
    <div className="min-h-screen bg-[var(--surface)] text-[var(--on-surface)] md:grid md:grid-cols-[248px_1fr]">
      <aside className="hidden border-r border-[var(--outline-variant)]/60 bg-white/85 backdrop-blur-xl md:flex md:flex-col">
        <div className="px-6 pb-6 pt-7">
          <Link href="/" className="block">
            <p className="font-display text-3xl font-bold text-[var(--primary)]">
              TripVerse
            </p>
            <p className="mt-1 text-[11px] font-semibold tracking-[0.2em] text-[var(--on-surface-variant)] uppercase">
              AI Assistant
            </p>
          </Link>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => {
            const active = isActivePath(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition ${
                  active
                    ? "bg-[var(--primary-fixed)] text-[var(--primary)]"
                    : "text-[var(--on-surface-variant)] hover:bg-[var(--surface-container-low)]"
                }`}
              >
                <span
                  className={`inline-flex h-7 w-7 items-center justify-center rounded-lg text-[10px] tracking-wide ${
                    active
                      ? "bg-[var(--primary)] text-white"
                      : "bg-[var(--surface-container)] text-[var(--on-surface-variant)]"
                  }`}
                >
                  {item.icon}
                </span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-[var(--outline-variant)]/60 p-3">
          <Link
            href="/planner"
            className="flex w-full items-center justify-center rounded-xl bg-[var(--primary)] px-4 py-3 text-sm font-bold text-white transition hover:bg-[var(--primary-container)]"
          >
            Plan New Trip
          </Link>
        </div>
      </aside>

      <div className="flex min-h-screen flex-col">
        <header className="sticky top-0 z-20 border-b border-[var(--outline-variant)]/60 bg-white/80 backdrop-blur-xl">
          <div className="flex h-16 items-center justify-between gap-4 px-4 sm:px-7">
            <div className="relative hidden w-full max-w-md sm:block">
              <input
                className="h-10 w-full rounded-full border border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-4 text-sm outline-none transition focus:border-[var(--primary)]"
                placeholder="Search itineraries or destinations"
              />
            </div>
            <div className="flex items-center gap-3 sm:ml-auto">
              <div className="hidden items-center gap-2 sm:flex">
                <div className="text-right">
                  <p className="text-sm font-semibold text-[var(--on-surface)]">
                    {user?.full_name || "Traveler"}
                  </p>
                  <p className="text-xs text-[var(--on-surface-variant)]">
                    {user?.email}
                  </p>
                </div>
              </div>
              <button
                onClick={logout}
                className="rounded-full bg-red-50 px-3 py-2 text-xs font-semibold text-red-600 transition hover:bg-red-100"
              >
                Logout
              </button>
              <div
                className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[var(--secondary-fixed)] text-xs font-bold text-[var(--on-secondary-fixed)]"
                title={user?.full_name || "User"}
              >
                {initials}
              </div>
            </div>
          </div>

          <div className="scrollbar-none flex items-center gap-2 overflow-x-auto border-t border-[var(--outline-variant)]/40 px-3 py-2 md:hidden">
            {navItems.map((item) => {
              const active = isActivePath(pathname, item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-full px-3 py-1 text-xs font-semibold whitespace-nowrap ${
                    active
                      ? "bg-[var(--primary)] text-white"
                      : "bg-[var(--surface-container-low)] text-[var(--on-surface-variant)]"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </header>

        <main className="flex-1 px-4 py-6 sm:px-7 sm:py-8">{children}</main>

        <footer className="border-t border-[var(--outline-variant)]/50 px-4 py-4 text-xs text-[var(--on-surface-variant)] sm:px-7">
          TripVerse AI | Intelligent serenity in travel
        </footer>
      </div>
    </div>
  );
}
