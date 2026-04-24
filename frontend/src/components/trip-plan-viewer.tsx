"use client";

import React from "react";

export type TripPlanActivity = {
  title?: string;
  details?: string;
  time?: string;
  type?: string;
};

export type TripPlanDay = {
  day?: number | string;
  title?: string;
  morning?: TripPlanActivity[];
  afternoon?: TripPlanActivity[];
  evening?: TripPlanActivity[];
  notes?: string[];
};

export type TripPlanSection = {
  title?: string;
  details?: string;
};

export type TripPlanData = {
  trip_title?: string;
  summary?: string;
  days?: TripPlanDay[];
  itinerary?: TripPlanData | TripPlanDay[];
  itinerary_only?: TripPlanData;
  food_and_culture?: TripPlanSection[];
  budget_breakdown?: TripPlanSection[] | Record<string, string | number>;
  safety_and_practical_tips?: TripPlanSection[];
  safety_tips?: string[];
  practical_tips?: string[];
  food_budget_tips?: Record<string, unknown>;
  context_sources?: number;
  trip_description?: string;
  budget?: string;
  pace?: string;
  starting_from?: string;
  legacy_text?: string;
};

type TripPlanInput = TripPlanData | string | null | undefined;

type TripPlanViewerProps = {
  plan: TripPlanInput;
  className?: string;
  compact?: boolean;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parsePlan(plan: TripPlanInput): TripPlanData | null {
  if (!plan) return null;
  if (typeof plan === "string") {
    try {
      return JSON.parse(plan) as TripPlanData;
    } catch {
      return { legacy_text: plan };
    }
  }
  return plan;
}

function normalizePlan(plan: TripPlanData | null): TripPlanData | null {
  if (!plan) return null;

  const embeddedItinerary =
    isRecord(plan.itinerary) && !Array.isArray(plan.itinerary)
      ? (plan.itinerary as TripPlanData)
      : null;

  return {
    ...plan,
    ...embeddedItinerary,
    days:
      plan.days ||
      (Array.isArray(plan.itinerary)
        ? (plan.itinerary as TripPlanDay[])
        : embeddedItinerary?.days) ||
      [],
  };
}

function formatLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function renderActivityGroup(title: string, activities?: TripPlanActivity[]) {
  if (!activities || activities.length === 0) return null;

  return (
    <div className="space-y-2">
      <p className="text-xs font-bold tracking-[0.14em] text-[var(--secondary)] uppercase">
        {title}
      </p>
      <div className="space-y-2">
        {activities.map((activity, index) => (
          <div
            key={`${title}-${index}-${activity.title || activity.details || "item"}`}
            className="rounded-2xl border border-[var(--outline-variant)] bg-white/80 p-4"
          >
            <p className="text-sm font-semibold text-[var(--on-surface)]">
              {activity.title || `${title} item ${index + 1}`}
            </p>
            {activity.details && (
              <p className="mt-1 text-sm text-[var(--on-surface-variant)]">
                {activity.details}
              </p>
            )}
            {(activity.time || activity.type) && (
              <p className="mt-2 text-[11px] font-semibold tracking-wide text-[var(--primary)] uppercase">
                {[activity.time, activity.type].filter(Boolean).join(" • ")}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function renderListSection(title: string, items?: string[]) {
  if (!items || items.length === 0) return null;
  return (
    <section className="space-y-3">
      <p className="text-xs font-bold tracking-[0.14em] text-[var(--secondary)] uppercase">
        {title}
      </p>
      <div className="grid gap-2 sm:grid-cols-2">
        {items.map((item, index) => (
          <div
            key={`${title}-${index}-${item}`}
            className="rounded-2xl border border-[var(--outline-variant)] bg-white px-4 py-3 text-sm text-[var(--on-surface-variant)]"
          >
            {item}
          </div>
        ))}
      </div>
    </section>
  );
}

function renderTitledSection(title: string, items?: TripPlanSection[]) {
  if (!items || items.length === 0) return null;
  return (
    <section className="space-y-3">
      <h3 className="text-xl font-bold text-[var(--on-surface)]">
        {title}
      </h3>
      <div className="grid gap-3 md:grid-cols-2">
        {items.map((item, index) => (
          <article
            key={`${title}-${item.title || "item"}-${index}`}
            className="rounded-2xl border border-[var(--outline-variant)] bg-white p-4"
          >
            <p className="text-sm font-semibold text-[var(--on-surface)]">
              {item.title || `${title} ${index + 1}`}
            </p>
            <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
              {item.details || ""}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default function TripPlanViewer({
  plan,
  className,
  compact = false,
}: TripPlanViewerProps) {
  const normalized = normalizePlan(parsePlan(plan));

  if (!normalized) {
    return (
      <div className={className || ""}>
        <p className="text-sm text-[var(--on-surface-variant)]">
          No trip plan available.
        </p>
      </div>
    );
  }

  const itinerary = normalized.itinerary_only || normalized;
  const days = itinerary.days || normalized.days || [];
  const foodSections = normalized.food_and_culture || [];
  const budgetBreakdownRaw = normalized.budget_breakdown;
  const budgetSections = Array.isArray(budgetBreakdownRaw)
    ? budgetBreakdownRaw
    : Object.entries(budgetBreakdownRaw || {}).map(([key, value]) => ({
        title: formatLabel(key),
        details: typeof value === "number" ? `$${value}` : String(value),
      }));
  const safetyPracticalSections = normalized.safety_and_practical_tips || [];
  const safetyTips = normalized.safety_tips || [];
  const practicalTips = normalized.practical_tips || [];

  if (normalized.legacy_text && days.length === 0 && foodSections.length === 0 && budgetSections.length === 0 && safetyPracticalSections.length === 0 && safetyTips.length === 0 && practicalTips.length === 0) {
    return (
      <div className={className || ""}>
        <div className="rounded-3xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] p-6">
          <p className="text-sm font-semibold text-[var(--on-surface)]">
            Legacy itinerary text
          </p>
          <pre className="mt-3 whitespace-pre-wrap text-sm leading-6 text-[var(--on-surface-variant)]">
            {normalized.legacy_text}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className={className || "space-y-6"}>
      <section className="space-y-4 rounded-3xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            {itinerary.trip_title && (
              <p className="text-xs font-bold tracking-[0.14em] text-[var(--primary)] uppercase">
                {itinerary.trip_title}
              </p>
            )}
            {itinerary.summary && (
              <p className="mt-2 text-sm text-[var(--on-surface-variant)]">
                {itinerary.summary}
              </p>
            )}
          </div>
          {normalized.context_sources !== undefined && (
            <div className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-[var(--on-surface-variant)]">
              {normalized.context_sources} context source{normalized.context_sources === 1 ? "" : "s"}
            </div>
          )}
        </div>
      </section>

      {days.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-[var(--on-surface)]">
              Day-by-Day Itinerary
            </h3>
            {compact && (
              <span className="text-xs font-semibold text-[var(--on-surface-variant)]">
                Compact view
              </span>
            )}
          </div>
          <div className="space-y-4">
            {days.map((day, index) => (
              <article
                key={`${day.day || index}-${day.title || "day"}`}
                className="overflow-hidden rounded-3xl border border-[var(--outline-variant)] bg-white shadow-[0_14px_35px_-26px_rgba(53,37,205,0.35)]"
              >
                <div className="flex items-center gap-4 border-b border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-5 py-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--primary)] text-lg font-bold text-white">
                    {day.day ?? index + 1}
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-[var(--on-surface)]">
                      {day.title || `Day ${day.day ?? index + 1}`}
                    </h4>
                    <p className="text-xs font-medium tracking-[0.14em] text-[var(--on-surface-variant)] uppercase">
                      Day {day.day ?? index + 1}
                    </p>
                  </div>
                </div>
                <div className="space-y-5 p-5">
                  <div className="grid gap-4 md:grid-cols-3">
                    {renderActivityGroup("Morning", day.morning)}
                    {renderActivityGroup("Afternoon", day.afternoon)}
                    {renderActivityGroup("Evening", day.evening)}
                  </div>
                  {day.notes && day.notes.length > 0 && (
                    <section className="space-y-2">
                      <p className="text-xs font-bold tracking-[0.14em] text-[var(--secondary)] uppercase">
                        Notes
                      </p>
                      <ul className="space-y-2">
                        {day.notes.map((note, noteIndex) => (
                          <li
                            key={`${day.day || index}-note-${noteIndex}`}
                            className="rounded-2xl border border-[var(--outline-variant)] bg-[var(--surface-container-low)] px-4 py-3 text-sm text-[var(--on-surface-variant)]"
                          >
                            {note}
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      {renderTitledSection("Food and Culture", foodSections)}
      {renderTitledSection("Budget Breakdown", budgetSections)}
      {renderTitledSection("Safety and Practical Tips", safetyPracticalSections)}
      {safetyTips.length > 0 && renderListSection("Safety Tips", safetyTips)}
      {practicalTips.length > 0 && renderListSection("Practical Tips", practicalTips)}
    </div>
  );
}
