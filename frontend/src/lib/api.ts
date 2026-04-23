'use client';

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL?.trim() || 'http://localhost:8000';

/**
 * Authenticated API fetch wrapper.
 * Automatically attaches JWT Bearer token from localStorage.
 */
export async function apiFetch<T = unknown>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 — token expired/invalid
  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `API error: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ---- Trip API helpers ----

export type TripData = {
  id: string;
  user_id: string;
  title: string;
  trip_description: string;
  budget: string;
  pace: string;
  starting_from: string;
  preferences: string | null;
  status: string;
  is_favorite: boolean;
  itinerary_data: Record<string, unknown> | null;
  itinerary_text: string | null;
  budget_spent: number | null;
  budget_total: number | null;
  travelers: number;
  dates: string | null;
  thumbnail_url: string | null;
  created_at: string;
  updated_at: string;
};

export type DashboardStats = {
  total_trips: number;
  upcoming_trips: number;
  average_budget: number;
  recent_trips: TripData[];
  next_trip: TripData | null;
};

export const tripApi = {
  /** Save a new trip */
  save: (data: Partial<TripData>) =>
    apiFetch<{ success: boolean; trip: TripData; message: string }>('/api/trips/save', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /** List all trips for current user */
  list: (filter?: string, sortBy?: string) => {
    const params = new URLSearchParams();
    if (filter) params.set('filter', filter);
    if (sortBy) params.set('sort_by', sortBy);
    const qs = params.toString();
    return apiFetch<{ success: boolean; trips: TripData[]; total: number }>(
      `/api/trips${qs ? `?${qs}` : ''}`,
    );
  },

  /** Get single trip by ID */
  get: (id: string) =>
    apiFetch<{ success: boolean; trip: TripData }>(`/api/trips/${id}`),

  /** Update a trip */
  update: (id: string, data: Partial<TripData>) =>
    apiFetch<{ success: boolean; trip: TripData; message: string }>(`/api/trips/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  /** Delete a trip */
  delete: (id: string) =>
    apiFetch<{ success: boolean; message: string }>(`/api/trips/${id}`, {
      method: 'DELETE',
    }),

  /** Toggle favorite */
  toggleFavorite: (id: string) =>
    apiFetch<{ success: boolean; trip: TripData; message: string }>(`/api/trips/${id}/favorite`, {
      method: 'PATCH',
    }),

  /** Duplicate a trip */
  duplicate: (id: string) =>
    apiFetch<{ success: boolean; trip: TripData; message: string }>(`/api/trips/${id}/duplicate`, {
      method: 'POST',
    }),

  /** Regenerate itinerary */
  regenerate: (id: string) =>
    apiFetch<{ success: boolean; trip: TripData; message: string }>(`/api/trips/${id}/regenerate`, {
      method: 'POST',
    }),

  /** Dashboard stats */
  dashboardStats: () =>
    apiFetch<{ success: boolean; stats: DashboardStats }>('/api/dashboard/stats'),

  /** Generate a trip plan (existing endpoint, no auth required but we send it anyway) */
  plan: (data: { trip_description: string; budget: string; pace: string; starting_from: string }) =>
    apiFetch<{ success: boolean; plan?: Record<string, unknown>; error?: string; errors?: string[] }>(
      '/api/trips/plan',
      { method: 'POST', body: JSON.stringify(data) },
    ),
};
