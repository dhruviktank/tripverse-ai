---
name: Effortless Exploration
colors:
  surface: '#fcf8ff'
  surface-dim: '#dcd8e5'
  surface-bright: '#fcf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f2ff'
  surface-container: '#f0ecf9'
  surface-container-high: '#eae6f4'
  surface-container-highest: '#e4e1ee'
  on-surface: '#1b1b24'
  on-surface-variant: '#464555'
  inverse-surface: '#302f39'
  inverse-on-surface: '#f3effc'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#00687a'
  on-secondary: '#ffffff'
  secondary-container: '#57dffe'
  on-secondary-container: '#006172'
  tertiary: '#7e3000'
  on-tertiary: '#ffffff'
  tertiary-container: '#a44100'
  on-tertiary-container: '#ffd2be'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb695'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#7b2f00'
  background: '#fcf8ff'
  on-background: '#1b1b24'
  surface-variant: '#e4e1ee'
typography:
  h1:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h2:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  h3:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.01em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.2'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 24px
  margin: 32px
---

## Brand & Style
This design system is built upon the concept of "Intelligent Serenity." It merges high-utility SaaS functionalism with the aspirational lightness of modern travel. The style is a hybrid of **Minimalism** and **Glassmorphism**, emphasizing clarity through generous whitespace and depth through translucent layers. 

The brand personality is professional yet visionary, aiming to reduce the cognitive load of trip planning. By using a light neumorphic approach for subtle tactile feedback and glassmorphism for secondary overlays, the UI feels both cutting-edge (GenAI) and reliably grounded. The atmosphere should evoke the feeling of a premium airport lounge: calm, organized, and anticipatory.

## Colors
The palette is anchored by a high-energy **Indigo** primary, symbolizing intelligence and trust, and a **Cyan** secondary that mirrors tropical waters and clear skies. 

The background uses a cool Light Gray to allow white cards to pop with minimal effort. Accent colors should be used sparingly: Indigo for primary actions and brand presence, and Cyan for AI-driven highlights or successful state indicators. Neutral tones are strictly pulled from the Slate/Gray scale to maintain a professional SaaS aesthetic without introducing clashing warmth.

## Typography
This design system utilizes a dual-font strategy. **Plus Jakarta Sans** is employed for headings to inject a friendly, contemporary, and optimistic travel vibe. Its softer curves balance the precision of the interface. 

For all functional text, including body copy, inputs, and labels, **Inter** provides maximum legibility and a systematic, utilitarian feel. Letter spacing is slightly tightened on large headings to maintain a premium "editorial" look, while UI labels use a slight positive tracking to ensure readability at small scales.

## Layout & Spacing
The layout is governed by a strict **8px grid system**, ensuring all elements align with mathematical harmony. This design system uses a 12-column fluid grid for dashboard views, with a maximum content width of 1440px for desktop to prevent line lengths from becoming unreadable.

Spacing is used to create a clear visual hierarchy; larger gaps (40px+) are used to separate major logical sections (e.g., Search from Results), while tighter spacing (12-16px) is reserved for internal card elements. Generous margins (32px+) at the screen edges reinforce the "uncluttered" brand promise.

## Elevation & Depth
Depth is created through a combination of **Ambient Shadows** and **Glassmorphism**. Shadows should be highly diffused, using a low-opacity Indigo tint (e.g., `rgba(79, 70, 229, 0.08)`) rather than pure black, to keep the UI feeling airy.

- **Level 1 (Default):** Flat surfaces with a subtle 1px border in Neutral 200.
- **Level 2 (Cards):** Soft shadows with a 12px blur, 0px offset, used for travel itinerary cards.
- **Level 3 (Modals/Overlays):** Glassmorphic surfaces using a `backdrop-filter: blur(12px)` and 80% opacity white fill. This is the "AI layer"—used for chat interfaces and floating map controls to suggest they exist above the physical itinerary.

## Shapes
The shape language is consistently **Rounded**, avoiding sharp corners to maintain a friendly and safe atmosphere. 

Standard components like input fields and small buttons use a 12px radius. Content containers and primary cards use a 16px radius. The 24px radius is reserved for large sections or featured promotional units. Pill shapes are used exclusively for tags, chips, and the primary "Generate" AI button to make them stand out as interactive, tactile elements.

## Components
- **Buttons:** Primary buttons use a solid Indigo fill with white text. Secondary buttons use a light neumorphic style—white background with a subtle inner glow and a soft drop shadow to appear "pressable."
- **Input Fields:** Search bars should be oversized (height: 56px) with a 12px radius, featuring a soft "glass" effect when focused to highlight the AI entry point.
- **Cards:** Itinerary cards must be white with a 16px radius and a Level 2 shadow. Use high-quality imagery with a top-only corner radius.
- **Chips:** Travel tags (e.g., "Budget," "Beach," "3-Day") should use a Pill-shape with a subtle Cyan background (`#06B6D4` at 10% opacity) and Cyan text.
- **AI Chat Interface:** Use a translucent glassmorphic panel that docks to the side or bottom, distinguishing the "planner" (AI) from the "plan" (The Grid).
- **Progress Indicators:** Use thin, Cyan-to-Indigo gradient lines to represent AI processing, maintaining a sense of motion and high-tech capability.