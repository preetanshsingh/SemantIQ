# SemantIQ — Frontend

React + Vite prototype of the SemantIQ content optimization workspace.
Currently running entirely on mock data (`src/data/mockData.js`) — no backend required yet.

## Setup

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. A dev proxy is already configured in `vite.config.js`
to forward `/api/*` calls to `http://localhost:8000` once the FastAPI backend exists.

## Structure

```
src/
  components/       UI building blocks (ScoreRing, WordRecommendations, PAAPanel, etc.)
  data/mockData.js  Mock fixtures shaped exactly like future API responses
  utils/scoring.js  Score color / tier helper functions
  styles/           Design tokens (tokens.css) + global resets + app.css
  App.jsx           Top-level state + layout
  main.jsx          React entry point
```

## Connecting to the real backend (next step)

Each export in `src/data/mockData.js` has a comment showing which endpoint will
eventually replace it, e.g.:

```js
// Replace with: GET /api/recommendations?keyword=...
export const MOCK_RECOMMENDATIONS = [...]
```

When the FastAPI endpoints are live, swap these constants for `fetch()` calls
(or React Query / SWR) inside `App.jsx`, keeping the same data shape so the
components don't need to change.

## Design system

Colors, fonts, and radii are defined as CSS custom properties in
`src/styles/tokens.css` — change the palette/typography there and it propagates
everywhere. Dark mode is automatic via `prefers-color-scheme`.

The signature UI element is the **Information Gain bar** on each word
recommendation card (`WordRecommendations.jsx`) — it's the one piece of UI
that makes Phase 1's NLP theory directly visible to the user, which no
competitor SEO tool currently does.
