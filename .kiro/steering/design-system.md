---
inclusion: fileMatch
fileMatchPattern: "**/*.tsx,**/*.jsx,**/*.css,**/*.scss,**/*.module.css"
---

# Design System Contract

The project's visual identity lives in the design system, not in component code. When building or editing UI, treat the style guide as authoritative.

## Source of Truth
- `docs/style-guide.html` defines the visual language: color tokens, typography, spacing, radius, shadow, and component looks.
- Mirror those tokens as CSS variables in the frontend (e.g. `styles/tokens.css`) using the same names from the style guide (`--orange`, `--ink`, `--surface`, `--r-card`, `--sh-md`, `--font`, ...).

## Rules
- **Never hardcode themable values** (colors, font families, radii, shadows, core spacing) in components. Use `var(--token)`.
- Only design-system primitives (e.g. `components/ui/*`) reference tokens directly; feature components compose those primitives.
- If a needed token doesn't exist, add it to the design system first, then use it — don't invent one-off values inline.
- Keep typography on the defined scale; don't introduce arbitrary font sizes/weights.
- Use the defined status colors for state (success/warning/critical); don't convey meaning by color alone (accessibility).
- Meet WCAG AA contrast when combining tokens.

## Rebranding
A new project or rebrand should require changing **only the token values** (in the style guide and `tokens.css`). Component code must not need edits to adopt a new palette or type. If a visual change forces component edits, a token is missing — fix it at the design-system level.
