# JobTrax & course hub — design system

This document describes the visual language and CSS variables used by the **395 course hub** (`/`) and the **JobTrax** Flask app (`/jobtrax`). The UI is **Linear-inspired**: dark surfaces, indigo accent, Inter typography, and subtle borders. It is **not** an official Linear product or asset package.

## Implementation map

| Surface | Stylesheet | Loaded from |
|--------|------------|-------------|
| Course hub (`templates/index.html`, `templates/home.html`) | `static/css/hub.css` | `url_for('static', filename='css/hub.css')` |
| JobTrax (all templates extending `jobtrax/templates/base.html`) | `jobtrax/static/css/app.css` | `url_for('jobtrax.static', filename='css/app.css')` |

The hub and app share the same aesthetic but **separate token prefixes** (`--hub-*` vs app `--*`) so the course landing page can evolve independently of the app shell.

---

## Foundations

### Typography

| Token / usage | Value |
|----------------|-------|
| Font family | **Inter**, with `system-ui`, `-apple-system`, `Segoe UI`, sans-serif fallbacks |
| Load | Google Fonts: `Inter` weights **400, 500, 600, 700** (both CSS files `@import`) |
| Hub body | `15px`, line-height **1.55** |
| JobTrax body | `14px`, line-height **1.5** |
| Page titles (`h1`) | JobTrax: ~**1.35rem**, weight **700**, letter-spacing **-0.02em** |

Use **600–700** for headings and nav labels; **400–500** for supporting text.

### Color philosophy

- **Background**: Near-black (`#08090a`) avoids harsh contrast with white text.
- **Surfaces**: Step up lightness in layers (`#0f1012`, `#141517`) instead of heavy shadows.
- **Borders**: Low-opacity white (`rgba(255,255,255,0.08)` — **0.12** when stronger).
- **Accent**: Indigo **`#5e6ad2`**; hover **`#6f76d9`**. Use for links, primary buttons, focus rings.

Semantic colors (JobTrax app only): success, danger, warning, info pairs include a soft background tint for flash messages and destructive actions.

### Radius

| Context | Hub | JobTrax |
|---------|-----|---------|
| Default | `--hub-radius`: **8px** | `--radius`: **8px** |
| Cards / larger panels | `--hub-radius-lg`: **12px** | `--radius-lg`: **10px** |
| Pills / badges | **999px** (hub badge) | — |

### Motion

- Short transitions (**~150–200ms**) on borders, backgrounds, and color.
- Respect **`prefers-reduced-motion`**: transitions disabled when the user requests reduced motion.

---

## Design tokens

### Course hub (`hub.css` — `:root`)

| Token | Purpose |
|-------|---------|
| `--hub-bg` | Page background `#08090a` |
| `--hub-surface` | List row / panel background `#0f1012` |
| `--hub-elevated` | Hover surface `#141517` |
| `--hub-border` | Default border `rgba(255,255,255,0.08)` |
| `--hub-border-hover` | Hover border `rgba(255,255,255,0.14)` |
| `--hub-text` | Primary text `#edeef0` |
| `--hub-muted` | Secondary text `#8a8f98` |
| `--hub-accent` | Accent `#5e6ad2` |
| `--hub-accent-dim` | Badge / glow tint `rgba(94,106,210,0.15)` |

Background **gradients** on `body` use soft purple ellipses for depth (see `hub.css`).

### JobTrax app (`app.css` — `:root`)

| Token | Purpose |
|-------|---------|
| `--bg-root` | Page background `#08090a` |
| `--bg-surface` | Cards, sidebar `#0f1012` |
| `--bg-elevated` | Table headers, secondary buttons `#141517` |
| `--bg-hover` | Interactive hover wash `rgba(255,255,255,0.06)` |
| `--border` / `--border-strong` | Default / stronger hairlines |
| `--text` | Primary `#edeef0` |
| `--text-secondary` | `#9ca3af` |
| `--text-muted` | `#6b7280` |
| `--accent` / `--accent-hover` | Primary actions |
| `--accent-muted` | Focus ring glow `rgba(94,106,210,0.2)` |
| `--danger` (+ `--danger-bg`) | Errors, destructive actions |
| `--success` (+ `--success-bg`) | Success flashes |
| `--warning` (+ `--warning-bg`) | Warning flashes |
| `--info` (+ `--info-bg`) | Info flashes |
| `--sidebar-w` | Sidebar width **240px** |

---

## Layout

### Course hub

- Centered column **max-width ~42rem**, generous vertical padding.
- **`.hub-list`**: vertical stack of linked panels; entire row is clickable with hover elevation.

### JobTrax app shell

- **`.layout`**: flex row; **`aside.sidebar`** is **sticky** on desktop (`min-height: 100vh`).
- **`.main-column`**: scrollable content column with **`.main-inner`** constraining width (**max-width 56rem**) and padding.
- **Breakpoint**: below **768px**, sidebar stacks above content; nav becomes horizontal wrap.

---

## Components (JobTrax)

Class names below live in `app.css` unless noted.

| Pattern | Classes / elements | Notes |
|---------|-------------------|--------|
| Sidebar brand | `.sidebar-brand`, `.sidebar-meta` | Product name + author line |
| Navigation | `.sidebar-nav a` | Full-width hit targets; hover uses `--bg-hover` |
| Footer link | `.sidebar-footer` | Includes “Course hub” back to `/` |
| User / logout | `.sidebar-user`, `.inline-form` | Logout uses ghost button styling |
| Flash | `.flash`, `.success`, `.danger`, `.warning`, `.info` | Bordered, tinted backgrounds |
| Card | `.card` | Default panel for filters and content blocks |
| Tables | `th`, `td` | Header row uses `--bg-elevated`; definition tables use `tbody th` for labels |
| Forms | `.form-row`, labels, inputs | Dark inputs on `--bg-root`; focus: border `--accent` + `--accent-muted` shadow |
| Buttons | `.btn`, `.btn.primary`, `.btn.danger`, `button` | Primary filled accent; default ghost/elevated |
| Actions row | `.actions` | Flex wrap for toolbars |
| Filters | `.filters` | Form controls aligned with labels |

Course hub equivalents: **`.hub-wrap`**, **`.hub-header`**, **`.hub-badge`**, **`.hub-title`**, **`.hub-list`**, **`.hub-footer`**.

---

## Accessibility

- **Focus**: `:focus-visible` outlines use the accent color (sidebar links, buttons, text links).
- **Contrast**: Primary text on dark backgrounds targets readable combinations; muted text is for secondary content only—not long body copy at small sizes.
- **Semantics**: JobTrax sidebar uses `aria-label="Primary"` on `<aside>`.
- **Motion**: Reduced-motion query disables transitions.

---

## Conventions for contributors

1. **Prefer tokens** — Add new UI using existing CSS variables before introducing one-off hex values.
2. **One accent** — Use `--accent` for interactive emphasis; avoid extra brand colors unless necessary.
3. **No emoji as icons** — Use SVG icon sets if icons are added later.
4. **Interactive feedback** — Clickable rows and controls should show hover and focus states (`cursor: pointer` on buttons and `.btn`).
5. **Hub vs app** — Marketing/course changes go to `hub.css`; product UI goes to `app.css`.

---

## Changelog

| Date | Notes |
|------|--------|
| 2026-05 | Initial doc: Linear-inspired dark theme, Inter, split hub/app tokens. |

When tokens change, update **`hub.css` / `app.css`** and this file together.
