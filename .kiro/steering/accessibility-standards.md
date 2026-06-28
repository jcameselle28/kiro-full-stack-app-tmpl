---
inclusion: fileMatch
fileMatchPattern: "**/*.tsx,**/*.jsx,**/*.css,**/*.scss,**/*.html"
---

# Accessibility Standards

Policy and acceptance criteria for the UI. The *how* lives in the `frontend-web` skill; this file defines the **target and the bar a feature must clear**.

## Target
- Conform to **WCAG 2.2 Level AA**
- Accessibility is a feature requirement, not a follow-up — a UI task isn't done until it meets this bar

## Non-Negotiables (Definition of Done for any UI work)
- **Keyboard**: every interactive element is reachable and operable by keyboard, in a logical order, with no traps
- **Visible focus**: a clear focus indicator on all focusable elements (never `outline: none` without a replacement)
- **Names & roles**: controls have accessible names; use semantic HTML first, ARIA only to fill gaps
- **Forms**: every input has a label; errors are programmatically associated and announced; invalid fields marked `aria-invalid`
- **Contrast**: text meets AA contrast (4.5:1 normal, 3:1 large); UI components and focus indicators meet 3:1
- **Color independence**: never use color as the only means of conveying information or state
- **Images/media**: meaningful images have `alt`; decorative images have empty `alt`; provide captions/transcripts for media
- **Headings/structure**: one `<h1>` per page; headings are hierarchical; landmarks (`main`, `nav`, `header`) present
- **Motion**: respect `prefers-reduced-motion`; no content flashes more than 3×/second
- **Zoom/reflow**: usable at 200% zoom and 320px width without loss of content or function
- **Dynamic updates**: async changes (toasts, validation, loading) are announced via live regions; focus is managed on route/dialog changes

## Verification
- **Automated** (catches ~30–40%): run axe / Lighthouse a11y checks in CI; treat new violations as build failures
- **Manual** (required): keyboard-only pass, screen-reader pass (VoiceOver / NVDA), 200% zoom, and contrast spot-checks
- Automated tools are necessary but **not sufficient** — full WCAG conformance requires manual testing with assistive technology and expert review

## Design-System Alignment
- The palette tokens in the design system are chosen to support AA contrast; still verify each foreground/background pairing in context
- Status colors must be paired with text/icon, not used alone (see `design-system.md`)

## When in Doubt
- Prefer native HTML elements over custom widgets
- If a custom widget is unavoidable, follow the WAI-ARIA Authoring Practices pattern for it and test with a screen reader
- Flag anything that can't meet AA so it's a conscious, documented decision — not an accident
