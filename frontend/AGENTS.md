# TripVerse AI Frontend - Routes & UI Agents

## Application Architecture

TripVerse AI frontend is a **Next.js 16.2.3** application with **React 19.2.4** and **Tailwind CSS 4**, built using **App Router** with a workspace-authenticated middleware pattern. The frontend is organized as a content delivery and state management layer that orchestrates backend API calls and presents intelligent trip planning UI.

---

## Directory Structure

```
src/
├── app/
│   ├── layout.tsx              # Root layout + font configuration
│   ├── page.tsx                # Landing page (/) - Public
│   ├── globals.css             # Design tokens + global styles
│   ├── (workspace)/
│   │   ├── layout.tsx          # Workspace shell wrapper
│   │   ├── dashboard/
│   │   │   └── page.tsx        # /dashboard - Authenticated
│   │   ├── planner/
│   │   │   └── page.tsx        # /planner - Trip form + backend call
│   │   ├── trips/
│   │   │   └── page.tsx        # /trips - Day timeline (mock)
│   │   ├── history/
│   │   │   └── page.tsx        # /history - Trip cards grid
│   │   └── itinerary/
│   │       └── page.tsx        # /itinerary - Functional itinerary UI
│   └── ...
├── components/
│   └── workspace-shell.tsx     # Shared navigation + layout
└── types/
    └── (implicit in pages)     # TypeScript interfaces per page
```

---

## Design System

### Color Tokens (`globals.css`)
```css
--primary:           #3525cd  /* Indigo - Primary actions, headers */
--secondary:         #00687a  /* Teal - Accents, badges */
--primary-light:     #eae5ff  /* 10% opacity over surface */
--primary-dark:      #2414a0  /* Hover state */
--surface:           #fcf8ff  /* Background card highlight */
--bg:                #ffffff  /* Page background */
--text-primary:      #1f2937  /* Headlines, body text */
--text-secondary:    #6b7280  /* Metadata, labels */
--outline:           #e5e7eb  /* Borders, dividers */
--success:           #10b981  /* Confirmations */
--error:             #ef4444  /* Warnings, errors */
--info:              #3b82f6  /* Information badges */
```

### Typography
- **Headings** (h1, h2, h3): Plus Jakarta Sans (700 weight)
- **Body text**: Inter (400 weight)
- **Labels/small**: Inter (500 weight)
- **Font sizing**: Scale of 12px → 14px → 16px → 18px → 20px → 24px → 32px → 48px

### Spacing Grid
- Base unit: **8px**
- Common spacing: 8, 12, 16, 24, 32, 40, 48, 64px
- Implemented via Tailwind: `gap-2` (8px), `gap-3` (12px), `gap-4` (16px), etc.

---

## Route Map

### 1. **Landing Page** (`src/app/page.tsx`)
**Route**: `/` (public)  
**Purpose**: Onboarding and value proposition

**Sections:**
- **Hero**: CTA "Plan Your Dream Trip" button → links to `/planner`
- **Feature Grid**: 4-6 features (e.g., "AI-Powered Recommendations", "Real-time Budget Tracking", "Community Reviews")
- **Social Proof**: User testimonials (optional placeholder)
- **Footer CTA**: Sign up or get started

**Data**: Static (no API calls)

**State**: None (presentational)

---

### 2. **Dashboard Page** (`src/app/(workspace)/dashboard/page.tsx`)
**Route**: `/dashboard` (authenticated via workspace group)  
**Purpose**: Post-authentication homepage with trip overview

**Components:**
- **Welcome Card**: Greeting (e.g., "Welcome back, Traveler!")
- **AI Recommendation Widget**: 
  - Shows suggested destination of the day
  - Brief description + CTA "Plan This Trip"
  - Mock data or future backend API call
- **Quick Stats Panel**:
  - Total trips planned
  - Total travel days
  - Average trip budget
  - Next upcoming trip (if exists)
- **Recent Trips Grid**: 
  - Thumbnail + title + dates + "View Itinerary" button
  - Links to `/itinerary/[tripId]`
  - Mock data currently

**State Management**:
```typescript
const [recommendedDestination, setRecommendedDestination] = useState<Destination | null>(null);
const [recentTrips, setRecentTrips] = useState<Trip[]>(mockTrips);
const [stats, setStats] = useState<DashboardStats>({...});
```

**API Integration**: (Future) `GET /api/dashboard/stats`, `GET /api/trips/recent`

---

### 3. **Planner Page** (`src/app/(workspace)/planner/page.tsx`)
**Route**: `/planner` (authenticated)  
**Purpose**: Main trip planning form and result display

**User Journey**:
```
Fill Form → Submit → Backend Call → Parse Response → Display Itinerary
```

**Form Fields**:
```typescript
interface TripPlanRequest {
  trip_description: string;    // "7 days Japan food tour"
  budget: "Value" | "Balanced" | "Luxury";
  pace: "Relaxed" | "Balanced" | "High-energy";
  starting_from: string;       // "New York City"
  preferences?: string;        // Optional: "outdoor, cultural, museums"
}
```

**Form Component**:
- Text input: Trip description (placeholder: "What trip are you planning?")
- Select: Budget level (3 options with icons)
- Select: Travel pace (3 options)
- Text input: Starting location (with autocomplete future enhancement)
- Textarea: Special preferences (optional)
- Button: "Generate Itinerary" (disabled while loading)

**Submission Flow**:
```typescript
const handleSubmit = async (data: TripPlanRequest) => {
  setLoading(true);
  
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/plan`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }
  );
  
  const result = await response.json();
  
  if (result.success) {
    setPlanResult(result.plan);
    setError(null);
  } else {
    setError(result.errors || ["Failed to generate plan"]);
  }
  
  setLoading(false);
};
```

**Result Display**:
- Shows generated itinerary text
- Buttons: "Save Trip" → dashboard, "View Full Itinerary" → itinerary page
- Error state: Shows error messages with retry button
- Loading state: Spinner + "Generating your trip..."

**State**:
```typescript
const [formData, setFormData] = useState<TripPlanRequest>({ ... });
const [loading, setLoading] = useState(false);
const [planResult, setPlanResult] = useState<Plan | null>(null);
const [error, setError] = useState<string[] | null>(null);
```

**API Endpoint**: `POST ${NEXT_PUBLIC_BACKEND_URL}/api/trips/plan`

---

### 4. **Trips Page** (`src/app/(workspace)/trips/page.tsx`)
**Route**: `/trips` (authenticated)  
**Purpose**: Day-by-day timeline view of current/upcoming trip

**Layout**:
- Left sidebar: Day selector (Days 1-7, etc.)
- Main area: Activities for selected day
  - Time-based activity cards
  - Activity title, location, duration
  - Action buttons: "Mark Complete", "Get Directions"

**Activity Card**:
```typescript
interface TimelineActivity {
  time: "09:00";
  title: "Breakfast at Cafe";
  location: "Rome";
  duration: "1h";
  type: "food";
  notes?: string;
}
```

**Mock Data**:
```typescript
const mockItinerary = {
  tripName: "7 Days Rome Food Tour",
  days: [
    {
      day: 1,
      title: "Arrival & Exploration",
      activities: [
        { time: "14:00", title: "Arrive at FCO", ... },
        { time: "16:00", title: "Check into hotel", ... },
        { time: "18:00", title: "Sunset walk at Trevi Fountain", ... },
      ]
    }
  ]
};
```

**State**: Mock data only (no external API)

---

### 5. **History Page** (`src/app/(workspace)/history/page.tsx`)
**Route**: `/history` (authenticated)  
**Purpose**: View all past and current trips with search/filter

**Layout**:
- Header with "Filter by:" (dropdown) and "Sort by:" (dropdown)
  - Filters: All Trips, Upcoming, Past, Favorites
  - Sort: Newest, Budget (high to low), Duration (longest)
- Trip cards grid (responsive: 1-3 columns)

**Trip Card**:
```typescript
interface TripCard {
  id: string;
  title: string;
  dates: string;              // "March 15-22, 2024"
  duration: number;           // days
  budget: string;             // "$2,500"
  pace: string;
  thumbnail?: string;
  status: "upcoming" | "past" | "saving";
}
```

**Card Actions**:
- Click card → navigate to `/itinerary/[tripId]`
- Heart icon → toggle favorite (local state, future: API)
- Three-dot menu → Share, Duplicate, Delete

**State**:
```typescript
const [trips, setTrips] = useState<TripCard[]>(mockTripCards);
const [filter, setFilter] = useState("all");
const [sortBy, setSortBy] = useState("newest");
```

**Computed**:
```typescript
const filteredTrips = trips
  .filter(t => {
    if (filter === "all") return true;
    if (filter === "upcoming") return t.status === "upcoming";
    if (filter === "past") return t.status === "past";
    return true;
  })
  .sort((a, b) => {
    // Sort logic...
  });
```

**Mock Data**: Currently 3-4 sample trips in state

---

### 6. **Itinerary Page** (`src/app/(workspace)/itinerary/page.tsx`)
**Route**: `/itinerary` or `/itinerary/[tripId]` (authenticated)  
**Purpose**: Full day-by-day itinerary with interactive planning tools

**Data Model**:
```typescript
interface ItineraryActivity {
  id: string;
  time: string;
  title: string;
  type: "activity" | "food" | "rest" | "travel";
  description: string;
  duration: string;
  meta?: { location?: string; cost?: string; };
  actionLabel?: string;
}

interface ItineraryDay {
  day: number;
  title: string;
  activities: ItineraryActivity[];
  food: string[];          // Meal highlights
  notes: string[];         // Traveler notes / tips
}

interface ItineraryPayload {
  tripName: string;
  dates: string;
  travelers: number;
  budgetSpent: number;
  budgetTotal: number;
  weather?: string;
  weatherMeta?: string;
  days: ItineraryDay[];
}
```

**Page Sections**:

#### **Sidebar (Desktop, 290px)**
- Trip title
- Stats: Dates, travelers, budget
- Weather forecast summary
- Action buttons (stacked): Save, Regenerate, Modify
- Notes section (collapsible)

#### **Main Content**
- Day selector tabs (Day 1, Day 2, ..., Day N)
- For selected day, render:
  - **Activities Timeline**: Vertical stack of activity cards
  - **Food Highlights**: Horizontal cards (e.g., "Authentic pasta at...")
  - **Daily Notes**: Editable text area (in modify mode)

**Reusable Components**:

```typescript
// SurfaceCard - Container with Indigo background
interface SurfaceCardProps {
  children: ReactNode;
  className?: string;
}

// ActionButton - Primary/Secondary action buttons
interface ActionButtonProps {
  label: string;
  onClick: () => void;
  variant: "primary" | "secondary";
  loading?: boolean;
}

// ItineraryCard - Individual activity card
interface ItineraryCardProps {
  activity: ItineraryActivity;
  editable?: boolean;
  onUpdate?: (updated: ItineraryActivity) => void;
}

// ScenicBlock - Scenic/food highlight box with gradient background
interface ScenicBlockProps {
  title: string;
  description?: string;
  gradient: string;  // e.g., "from-indigo-400 to-cyan-400"
}
```

**State Management**:
```typescript
const [data, setData] = useState<ItineraryPayload>(initialData);
const [modifyMode, setModifyMode] = useState(false);
const [selectedDay, setSelectedDay] = useState(1);
const [savedAt, setSavedAt] = useState<Date | null>(null);

// Actions
const handleSave = () => {
  // 1. POST to backend (future: /api/itinerary/save)
  // 2. Store locally in browser
  // 3. Show toast: "Itinerary saved"
  setSavedAt(new Date());
};

const handleRegenerate = () => {
  // 1. Show confirmation modal
  // 2. POST to backend with current settings
  // 3. Replace data with new plan
  // 4. Show toast: "Plan regenerated"
};

const updateNote = (dayIndex: number, noteIndex: number, value: string) => {
  setData(prev => ({
    ...prev,
    days: prev.days.map((d, i) => 
      i === dayIndex 
        ? { ...d, notes: d.notes.map((n, j) => j === noteIndex ? value : n) }
        : d
    )
  }));
};
```

**Action Flows**:

- **Save**:
  - Records `savedAt` timestamp
  - (Future) Persists to backend via `POST /api/trips/save`
  - (Future) Enables "Load from saved" on dashboard
  
- **Regenerate**:
  - Confirms "This will replace the current plan"
  - Calls backend with same trip parameters
  - Replaces `data` with new plan
  - Resets `modifyMode` to false
  
- **Modify**:
  - Toggles `modifyMode` boolean
  - When true: Shows edit icons on daily notes
  - Days and activities readonly (future: make them editable)

**Styling**:
- Day tabs: Primary color on active, outline on inactive
- Activity cards: White background, shadow, smooth hover
- Food blocks: Gradient backgrounds (Indigo→Cyan, Cyan→Green, etc.)
- Modify mode: Subtle background highlight on editable sections

---

### 7. **Workspace Shell** (`src/components/workspace-shell.tsx`)
**Purpose**: Shared layout container for all `/workspace/*` routes

**Components**:

#### **Desktop Navigation**
- Sidebar (250px fixed):
  - Logo/App name
  - Navigation items: Dashboard, Planner, Trips, History
  - Icons + labels
  - Active state highlighting (Primary color underline)
  
- Header:
  - Search bar: "Search destinations..." (placeholder, future enhancement)
  - User profile: Avatar + name dropdown
  - Notifications bell (placeholder)

#### **Mobile Navigation**
- Hamburger menu (collapsible sidebar)
- Bottom nav bar (4 main items)
- Responsive breakpoints: `sm < 640px`, `md >= 768px`, `lg >= 1024px`

**Layout Structure**:
```jsx
<div className="flex">
  {/* Desktop Sidebar */}
  <nav className="hidden lg:flex w-64 bg-bg flex-col">
    {/* Nav items */}
  </nav>
  
  {/* Mobile Header */}
  <header className="lg:hidden w-full bg-bg border-b">
    {/* Hamburger + Search + Profile */}
  </header>
  
  {/* Main Content */}
  <main className="flex-1 bg-white">
    {children}
  </main>
</div>
```

**State**:
```typescript
const [sidebarOpen, setSidebarOpen] = useState(false);  // Mobile
const [userMenuOpen, setUserMenuOpen] = useState(false);
```

---

## Environment Configuration

### Required Environment Variables
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Optional (for future features)
```
NEXT_PUBLIC_APP_NAME=TripVerse AI
NEXT_PUBLIC_GA_ID=<Google Analytics ID>
```

---

## State Management Strategy

**Principle**: Use **React Hooks only** (no Redux, Zustand, etc.)

### Per-Page State:
```typescript
// Planner: Form state
const [formData, setFormData] = useState<TripPlanRequest>({ ... });

// Itinerary: Data + editing
const [data, setData] = useState<ItineraryPayload>(initialData);
const [modifyMode, setModifyMode] = useState(false);

// History: Filter + sort
const [trips, setTrips] = useState<TripCard[]>([]);
const [filter, setFilter] = useState("all");
```

### Global patterns (if needed):
- Context API for theme (light/dark, future)
- LocalStorage for user preferences
- URL params for navigation state (e.g., `/itinerary?tripId=123&day=3`)

---

## API Integration Patterns

### Fetch Wrapper (Recommended future utility):
```typescript
// utils/api.ts
const apiCall = async <T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> => {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}${endpoint}`,
    {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    }
  );
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
};

// Usage:
const result = await apiCall<TripPlan>('/api/trips/plan', {
  method: 'POST',
  body: JSON.stringify(formData),
});
```

### Current Planner Integration:
```typescript
// Direct fetch in page.tsx
const response = await fetch(
  `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/plan`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }
);
```

### Expected Backend Response:
```json
{
  "success": true,
  "plan": {
    "trip_description": "7 days Italy food tour",
    "budget": "Balanced",
    "pace": "Relaxed",
    "itinerary": "Complete itinerary text..."
  },
  "errors": []
}
```

---

## Data Flow: User Perspective

```
┌────────────────────────────────────┐
│ User lands on /                    │
│ (Landing page with pitch + CTA)    │
└────────────────┬────────────────┬──┘
                 │                │
                 ↓ Click CTA      ↓
          /planner           Sign up flow
                │
                ↓
  ┌─────────────────────────┐
  │ /planner form           │
  │ Destination, budget,    │
  │ pace, preferences       │
  └─────────────┬───────────┘
                │
                ↓ Submit
        ┌───────────────────┐
        │ POST /api/trips   │
        │ Backend generates │
        │ itinerary        │
        └───────────┬───────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
    Success    Loading       Error
         │          │          │
         ↓         ↓           ↓
    Show plan  Spinner    Error msg
         │                      │
         └────────┬─────────────┘
                  │
        ┌─────────┴──────────┐
        │ Click "View Full"  │
        │ or continue        │
        └─────────┬──────────┘
                  │
                  ↓
    /itinerary (day timeline)
         │
    ┌────┴────────────┐
    │ Interactive     │
    │ Save/Regen/Mod  │
    │ Edit notes      │
    └────────────────┘
```

---

## Component Reusability

### Shared Primitives (Extractable to `src/components/ui/`):

1. **SurfaceCard**: Used in itinerary
   - Can be used in dashboard for recommendation widget
   - Can be used in history for trip cards

2. **ActionButton**: Used in itinerary (Save, Regenerate, Modify)
   - Can be standardized across all pages
   - Variants: Primary (Indigo), Secondary (outline)

3. **ItineraryCard**: Activity display
   - Can be reused in trips timeline
   - Accepts `editable` prop for modify mode

4. **ScenicBlock**: Food/scenic highlights
   - Can be used in planner results
   - Gradient customizable

---

## Performance & Optimization

### Techniques:
1. **Lazy Loading**: Use `next/dynamic` for route components:
   ```typescript
   const Planner = dynamic(() => import('./planner'), { loading: () => <Spinner /> });
   ```

2. **Image Optimization**: Next.js `Image` component for future trip thumbnails
   ```typescript
   <Image src={thumbnail} alt={title} width={300} height={200} />
   ```

3. **Memoization**: Prevent re-renders of expensive components
   ```typescript
   const DaySelector = React.memo(({ days, selected, onChange }) => { ... });
   ```

4. **State Batching**: Use callback refs instead of multiple updates
   ```typescript
   const updateMultiple = (updates: Partial<ItineraryPayload>) => {
     setData(prev => ({ ...prev, ...updates }));
   };
   ```

---

## Testing & Development

### Local Development:
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### Linting:
```bash
npm run lint
```

### Building:
```bash
npm run build
npm start  # Production
```

---

## Future Enhancements

1. **Authentication**: Add NextAuth.js for real user sessions
2. **Backend integration**: Real trip persistence and retrieval
3. **Image uploads**: Trip photos in itinerary
4. **Sharing**: Generate shareable trip links
5. **Collaborative editing**: Multiple users edit same itinerary
6. **Mobile app**: React Native version
7. **Voice assistant**: "Add restaurant recommendation" via speech
8. **Real-time sync**: WebSockets for multi-device sync
9. **Offline support**: Service Worker + local cache
10. **Payments**: Trip booking integration (flights, hotels)

---

## Key Decision Log

| Decision | Rationale |
|----------|-----------|
| React hooks only | Simpler mental model, less boilerplate |
| Tailwind CSS | Utility-first, faster styling, responsive tokens |
| (workspace) group | Authenticated pages separated cleanly from public |
| Single LLM call on backend | Reduced latency, clearer UX on frontend |
| JSON-driven itinerary | Flexibility for future modifications |
| Reusable components | Consistency, code reuse, scalability |
| CSS variables for tokens | Design system flexibility, DX consistency |
| Next.js App Router | Modern, file-based routing, server components prep |
