# JobTrax design system

This document describes the visual language and CSS variables used by the **JobTrax** Flask app, the **395 course hub**, and **Labs 8-11**. The system adapts the Apple-like reference in `docs/new-design.md` to the existing server-rendered Flask/Jinja stack: plain HTML templates, CSS files, no frontend build step, and no new component library.

The design goal is a quiet product workspace: near-invisible navigation, generous off-white surfaces, white utility cards, one blue action color, pill-shaped calls to action, SF/system typography, hairline borders, and almost no decorative chrome.

## Implementation map

| Surface | Stylesheet | Loaded from |
|--------|------------|-------------|
| Course hub | `static/css/hub.css` | `url_for('static', filename='css/hub.css')` |
| Labs 8-11 | `static/css/lab.css` | `url_for('static', filename='css/lab.css')` |
| JobTrax app | `jobtrax/static/css/app.css` | `url_for('jobtrax.static', filename='css/app.css')` |

The Apple-inspired system is implemented across all app surfaces. The hub, labs, and JobTrax keep separate stylesheets and token prefixes (`--hub-*`, `--lab-*`, and JobTrax app tokens) so each surface can evolve independently while sharing the same visual language.

---

## Foundations

### Typography

| Token / usage | Value |
|---------------|-------|
| `--font-display` | `SF Pro Display`, `SF Pro Text`, `system-ui`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, sans-serif |
| `--font-text` | `SF Pro Text`, `system-ui`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, sans-serif |
| `--font-mono` | `ui-monospace`, `SFMono-Regular`, `Consolas`, monospace |
| Body | 17px / 1.47 / weight 400 |
| Page title | clamp 34-40px / 1.1 / weight 600 |
| Section title | 21px / 1.19 / weight 600 |
| Utility text | 14px / 1.43 / weight 400 |
| Fine print | 12px / 1.3 / weight 400 |

Use 600 for headings and labels, 400 for body copy, and avoid weight 500. Display text should feel confident but not heavy.

### Color

| Token | Purpose |
|-------|---------|
| `--canvas` | Pure white `#ffffff` |
| `--canvas-parchment` | Page canvas `#f5f5f7` |
| `--surface-pearl` | Secondary button/input fill `#fafafc` |
| `--surface-black` | Global navigation `#000000` |
| `--surface-tile-1` | Optional dark panel `#272729` |
| `--surface-tile-2` | Dark panel variant `#2a2a2c` |
| `--ink` | Primary text `#1d1d1f` |
| `--ink-muted` | Secondary text `#333333` |
| `--ink-soft` | Muted text `#7a7a7a` |
| `--on-dark` | Text on black/dark surfaces `#ffffff` |
| `--on-dark-muted` | Muted text on dark surfaces `#cccccc` |
| `--primary` | Action Blue `#0066cc` |
| `--primary-focus` | Focus Blue `#0071e3` |
| `--primary-on-dark` | Link blue on dark surfaces `#2997ff` |
| `--hairline` | Utility card border `#e0e0e0` |
| `--divider-soft` | Soft divider `rgba(0, 0, 0, 0.04)` |

There is one interactive accent: `--primary`. Links, primary buttons, focus rings, and selected states use this blue. Semantic flash colors remain available for success, warning, info, and destructive states.

### Spacing

| Token | Value | Use |
|-------|-------|-----|
| `--space-xxs` | 4px | Fine alignment |
| `--space-xs` | 8px | Tight controls |
| `--space-sm` | 12px | Compact groups |
| `--space-md` | 17px | Body rhythm |
| `--space-lg` | 24px | Card padding |
| `--space-xl` | 32px | Page groups |
| `--space-xxl` | 48px | Page top/bottom |
| `--space-section` | 80px | Large sections |

Structural layout snaps to the 8px rhythm. Dense operational areas may use 12px and 17px to align with the body text rhythm.

### Shape

| Token | Value | Use |
|-------|-------|-----|
| `--radius-none` | 0 | Full-width bands and nav |
| `--radius-sm` | 8px | Utility buttons and compact inputs |
| `--radius-md` | 11px | Secondary capsules |
| `--radius-lg` | 18px | Cards and larger panels |
| `--radius-pill` | 9999px | Primary actions, nav chips, selects |

Pills are the action grammar. Cards use 18px radius, but page sections and the global nav stay square.

---

## Components

### Global Navigation

JobTrax keeps the existing `aside.sidebar` markup but styles it as a thin global navigation bar.

- Height: 44px minimum.
- Background: `--surface-black`.
- Brand: 17px / 600, white.
- Links: 12px / 400, muted white by default, white on hover.
- Active/focus state: blue focus outline, no heavy background.
- Mobile: wraps into a compact black navigation tray.

Labs use the same black navigation treatment in `templates/lab_base.html`, with a compact "Course hub" back link and the author label.

### Page Canvas

The page background is parchment/off-white. JobTrax and lab content are centered at roughly 980px wide. The course hub uses a wider 1440px outer container with a centered hero and a 980px navigation grid.

### Cards

JobTrax `.card`, `details.card`, top-level forms, lab forms, lab list rows, lab tables, and hub navigation tiles are white utility cards:

- Background `--canvas`.
- 1px `--hairline` border.
- 18px radius.
- 24px padding.
- No box-shadow by default.

### Buttons

| Class | Treatment |
|-------|-----------|
| `.btn.primary`, `button.primary` | Blue filled pill, white text, 11px x 22px padding |
| `.btn`, `button` | Pearl secondary capsule, soft ring, near-black text |
| `.btn.danger` | Pearl capsule with red text and red hairline |

Pressed state uses `transform: scale(0.95)`. Focus-visible uses a 2px `--primary-focus` outline.

### Forms

Inputs, selects, and textareas are white or pearl controls with hairline borders and 11px radius. Selects and search-like inputs use the pill shape when they are compact filter controls. Focus states use a blue hairline plus a soft focus ring.

### Tables

Tables sit inside white cards. Header rows use the parchment surface, 12px uppercase utility text, and hairline separators. Body rows use quiet hover washes and preserve readable 17px body rhythm where space allows.

### Course Hub

The root route (`/`) is a product-style selector:

- Centered hero with `395 hub`, author, and one-line lead.
- Two-column utility grid on desktop, single column on mobile.
- JobTrax tile uses the black surface variant to create a clear product entry point.
- No gradients, grain, or decorative shadows.

### Flash Messages

Flash messages are rounded white cards with semantic colored text and soft semantic borders. They should not introduce a second brand accent for normal actions.

---

## Accessibility

- Focus-visible outlines use `--primary-focus`.
- Body copy defaults to 17px for readability.
- Touch targets should be at least 44px tall for buttons and primary links.
- Reduced-motion disables transitions and active scale transforms.
- Muted text is reserved for secondary or supporting copy, not long paragraphs.

---

## Contributor conventions

1. Prefer CSS variables from `app.css` before adding new values.
2. Use `--primary` for every normal interactive affordance.
3. Do not add decorative gradients, blobs, grain textures, or card shadows.
4. Keep cards white, bordered, and rounded at `--radius-lg`.
5. Keep page structure server-rendered and template-friendly; no new frontend stack unless the project requirements change.
6. Use SVG/icon libraries only if an icon set is already introduced deliberately.
7. Update this file and `jobtrax/static/css/app.css` together when tokens change.

---

## Changelog

| Date | Notes |
|------|-------|
| 2026-05 | Reworked JobTrax design system toward the Apple-inspired reference: white/parchment surfaces, black global nav, blue pill actions, SF/system type, hairline borders, no decorative gradients. |
| 2026-05 | Extended the same design system to the course hub and Labs 8-11. |
