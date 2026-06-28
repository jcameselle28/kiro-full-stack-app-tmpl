# Frontend Patterns — Deep Dive

Supporting reference for the `frontend-web` skill. Next.js App Router + React + TypeScript.

## App Router Data Flow

- **Server components** (default) run on the server, can fetch directly, and ship zero JS for that subtree. Use for pages, layouts, and read-only data display.
- **Client components** (`"use client"`) run in the browser. Use only where you need interactivity, browser APIs, or React state/effects. Keep them as small leaves.
- Pass server-fetched data down as props; don't make a whole page a client component just to add one button.
- Use `loading.tsx` and `error.tsx` per route segment for built-in suspense and error boundaries.
- Mutations: use Server Actions or route handlers; revalidate affected data after a write.

```tsx
// app/accounts/page.tsx  (server component)
import { AccountsTable } from "@/features/accounts/AccountsTable";
import { getAccounts } from "@/lib/api/accounts";

export default async function AccountsPage() {
  const accounts = await getAccounts({ page: 1 });
  return <AccountsTable initialData={accounts} />;
}
```

## TanStack Query Recipes

### Query keys
Structure keys as `[entity, params]` so you can invalidate broadly or narrowly:
```ts
useQuery({ queryKey: ['accounts', { page }], queryFn: () => api.listAccounts({ page }) });
queryClient.invalidateQueries({ queryKey: ['accounts'] }); // all account lists
```

### Optimistic updates
```ts
useMutation({
  mutationFn: api.updateAccount,
  onMutate: async (next) => {
    await queryClient.cancelQueries({ queryKey: ['accounts'] });
    const prev = queryClient.getQueryData(['accounts']);
    queryClient.setQueryData(['accounts'], (old) => applyUpdate(old, next));
    return { prev };
  },
  onError: (_e, _next, ctx) => queryClient.setQueryData(['accounts'], ctx?.prev),
  onSettled: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
});
```

### Hydration with server components
Prefetch on the server, dehydrate, and hydrate on the client so the first render has data and the client takes over caching.

## Typed API Client

```ts
// lib/api/client.ts
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { 'content-type': 'application/json', ...authHeader(), ...init?.headers },
  });
  if (!res.ok) throw await toApiError(res); // normalize to a typed error
  return res.json() as Promise<T>;
}
```
- Generate `T` types from the backend's OpenAPI schema (e.g., `openapi-typescript`) so client and server never drift.
- Normalize errors into a single shape the UI can switch on (validation vs auth vs server).

## Accessibility Checklist
- [ ] Page has one `<h1>`; headings are hierarchical
- [ ] All images have meaningful `alt` (or empty `alt` if decorative)
- [ ] Forms: every control has a label; errors linked via `aria-describedby`; `aria-invalid` on bad fields
- [ ] Keyboard: tab order is logical; focus is visible; no keyboard traps
- [ ] Dialogs/menus: focus moves in, is trapped, and returns to the trigger on close
- [ ] Live regions announce async updates (`aria-live`)
- [ ] Color contrast meets WCAG AA; state isn't conveyed by color alone
- [ ] `prefers-reduced-motion` respected
- [ ] Verified with keyboard-only and a screen reader (full conformance needs manual expert review)

## Testing Strategy
- **Unit/component** (Vitest + React Testing Library): test behavior through the DOM the user sees — query by role/label, not test IDs. Assert on accessible output.
- **Hooks**: test custom hooks in isolation with `renderHook`.
- **Integration**: render a feature with a mocked API client; cover loading/empty/error/success paths.
- **E2E** (Playwright): a handful of critical user journeys against a deployed/preview build.
- Mock the network at the boundary (MSW) rather than stubbing internal modules.
- Don't test framework internals or visual pixels; test behavior and accessibility.

## Styling With Design Tokens
- Global `styles/tokens.css` mirrors the style guide's CSS variables (`--orange`, `--ink`, `--r-card`, ...).
- Components use `var(--token)` in CSS Modules:
```css
/* Button.module.css */
.cta { background: var(--red); color: #fff; border-radius: var(--r-pill); }
```
- No literal hex/px for themable values inside components.
- A rebrand changes only `tokens.css`; component CSS is untouched.
- If using Tailwind instead, map the tokens into `theme.extend` so utilities resolve to the same variables.

## Common Pitfalls
- Making everything a client component (ships needless JS) — default to server components.
- Duplicating server data into `useState` — let TanStack Query own it.
- Storing filter/pagination in component state instead of the URL — breaks sharing and back button.
- Hardcoding colors/spacing in feature components — breaks the design-system contract.
- Skipping loading/error/empty states — they are part of the feature, not extras.
