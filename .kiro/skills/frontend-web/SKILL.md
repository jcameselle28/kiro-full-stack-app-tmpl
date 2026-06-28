---
name: frontend-web
description: This skill provides frontend engineering patterns for full-stack web apps on AWS — Next.js + React + TypeScript, component structure, state management, data fetching, forms, accessibility, performance, and serving via S3/CloudFront or SSR on EC2. Visual design lives in the design system (style guide), not here. Triggers on requests about frontend, UI, React, Next.js, components, pages, or client-side code.
---

# Frontend Web Skill

Engineering patterns for the frontend of web applications. This skill is about **how to build the UI** — structure, state, data, accessibility, performance. It does **not** define visual design (colors, type, spacing); that is the design system's job — see `docs/style-guide.html` and the `design-system` steering rule.

## Activation Keywords
- frontend, front-end, UI, client, browser
- React, Next.js, component, page, route, hook
- state, data fetching, query, form, validation
- accessibility, a11y, responsive

## Default Stack

| Concern | Choice |
|---|---|
| Framework | Next.js (App Router) + React |
| Language | TypeScript only (strict) |
| Server state | TanStack Query |
| Local/UI state | React state + Context (reach for a store only when justified) |
| Styling | CSS Modules consuming design-token CSS variables |
| Forms | React Hook Form + Zod (shared schemas with the API where possible) |
| Testing | Vitest + React Testing Library; Playwright for E2E |

### Hosting modes
- **Static export** (`next export` / static output) → served from **S3 + CloudFront**. Default for content/SPA-style apps.
- **SSR / server components** → run the Next.js server on **EC2** behind the ALB, with CloudFront in front for caching/edge. Use when you need server rendering, per-request data, or streaming.

Pick one per project and record it in `project-config.md`.

## Project Structure
```
apps/web/
├── app/                   # Next.js App Router (routes, layouts, server components)
│   ├── (routes)/
│   ├── layout.tsx
│   └── error.tsx
├── components/            # Reusable presentational + container components
│   └── ui/                # Primitives that map design tokens → elements
├── features/             # Feature-scoped components, hooks, and logic
├── hooks/                 # Shared custom hooks
├── lib/                   # API client, query setup, utilities
├── styles/                # Global CSS + design-token variables
├── types/                 # Shared TS types (prefer generating from API schema)
└── test/
```
Group by **feature**, not by file type, once a feature grows beyond a couple of files.

## Component Conventions
- Prefer **server components** for data-heavy, non-interactive UI; mark interactive leaves with `"use client"`
- Keep components small and single-purpose; lift shared logic into hooks
- Split **presentational** (props in, markup out) from **container** (data/state) components
- Type every prop interface; no `any`
- `ui/` primitives (Button, Input, Card) are the only place that reads design tokens directly — feature components compose primitives, never raw colors/spacing
- Co-locate component, styles, and test: `Button.tsx`, `Button.module.css`, `Button.test.tsx`

## State Management
- **Server state** (anything fetched from the API) → TanStack Query: caching, retries, invalidation, optimistic updates. Don't duplicate it into local state
- **URL state** (filters, pagination, tabs) → the router/search params, so it's shareable and back-button friendly
- **Local UI state** → `useState`/`useReducer`
- **Cross-cutting app state** (theme, current user) → Context. Reach for a dedicated store only when Context causes real re-render pain

## Data Fetching
- One typed **API client** in `lib/` wrapping `fetch`; never scatter raw `fetch` calls
- Centralize base URL, auth header injection, and error normalization there
- Server components fetch directly; client components use TanStack Query hooks
- Define query keys consistently (`['accounts', { page }]`) for predictable invalidation
- Generate request/response types from the API's OpenAPI/schema to stay in sync with the backend
- Handle the full lifecycle in the UI: loading, empty, error, and success states

## Forms & Validation
- React Hook Form for state; **Zod** for schema validation
- Share Zod schemas between client and server when both are TypeScript — validate on the client for UX, **always re-validate on the server** for safety
- Show inline, accessible error messages tied to inputs via `aria-describedby`
- Disable submit while pending; prevent double-submit

## Accessibility (implementation)
- Use semantic HTML first; reach for ARIA only to fill gaps
- All interactive elements are keyboard reachable and have visible focus
- Label every input; associate errors and hints programmatically
- Manage focus on route changes, dialog open/close, and async updates
- Respect `prefers-reduced-motion`; don't convey meaning by color alone
- Meet WCAG AA contrast — the design system tokens are chosen to support this; verify when combining them
- Test with keyboard and a screen reader; note that full WCAG conformance needs manual review with assistive tech

## Performance
- Code-split by route; lazy-load heavy, below-the-fold, or rarely-used components
- Use `next/image` (or equivalent) for responsive, optimized images served via CloudFront
- Memoize expensive renders deliberately (`memo`, `useMemo`) — measure first, don't pre-optimize
- Keep client bundles lean; prefer server components to ship less JS
- Set sensible CloudFront cache headers for static assets; bust caches with content hashes on deploy
- Watch Core Web Vitals (LCP, CLS, INP)

## Integration With the Design System
- The style guide (`docs/style-guide.html`) is the **single source of truth** for visual decisions
- Expose its tokens as CSS variables in `styles/`; components reference `var(--token)`, never literal hex/px for themable values
- When the brand changes, only the token values change — components stay put
- See the `design-system` steering rule for the enforced contract

For deeper patterns (App Router data flow, TanStack Query recipes, a11y checklists, testing strategy), see `references/patterns.md`.
