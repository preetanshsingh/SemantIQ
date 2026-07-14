# SemantIQ — Backend (Skeleton)

FastAPI backend stub for SemantIQ. Every endpoint currently returns mock
data shaped exactly like `src/data/mockData.js` on the frontend — no real
NLP, SERP, or LLM calls have been wired in yet. This exists so the
frontend↔backend wiring can be proven out before the NLP engine is built.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Server runs at `http://localhost:8000`. Interactive API docs (auto-generated
by FastAPI) are at `http://localhost:8000/docs` — open that in a browser to
test every endpoint without writing any code.

CORS is already configured to accept requests from `http://localhost:5173`
(the Vite frontend's default dev port).

## Endpoints

| Method | Path                 | Returns                                  | Status |
|--------|----------------------|-------------------------------------------|--------|
| POST   | `/api/analyze`       | Kicks off analysis for a keyword          | Stub   |
| POST   | `/api/score`         | Overall score + factor breakdown          | Stub (word-count heuristic) |
| GET    | `/api/recommendations` | IG-ranked word recommendations          | Stub   |
| GET    | `/api/paa`           | People Also Ask coverage                  | Stub   |
| POST   | `/api/entities`      | NER + Knowledge Graph entity linking      | Stub   |
| POST   | `/api/readability`   | Readability + AI-detection metrics        | Stub   |
| GET    | `/api/brief`         | RAG content brief (H1 + H2 structure)     | Stub   |
| POST   | `/api/links`         | Internal/external link suggestions        | Stub   |

## Structure

```
app/
  main.py            FastAPI app, CORS config, router registration
  models.py           Pydantic schemas (request/response shapes)
  mock_data.py        Fixture data, mirrors frontend's mockData.js
  routers/
    analyze.py
    score.py
    recommendations.py
    paa.py
    entities.py
    readability.py
    brief.py
    links.py
```

Each router file has a `TODO` docstring describing exactly what real
implementation needs to replace the stub — see those before starting
Milestone 1's NLP work.

## Next steps (in order)

1. **`/score` + `/recommendations`** — wire in SBERT embeddings + cosine
   similarity against real SERP top-3 content, and the Information Gain
   ranking calculation. This is the core engine; everything else depends
   on it being real.
2. **`/readability`** — fastest win, mostly a drop-in `textstat` call.
3. **`/entities`** — spaCy NER + Google Knowledge Graph Search API.
4. **`/paa`** — SerpAPI integration for real PAA extraction.
5. **`/brief`** — RAG pipeline once `/recommendations` and `/entities`
   are real, since the brief synthesizes signal from both.
6. **`/links`** — GNN or embedding-based link relevancy (Milestone 3).

## Connecting the frontend

In the frontend's `App.jsx`, replace the imports from `mockData.js` with
`fetch()` calls to these endpoints, e.g.:

```js
const res = await fetch(`/api/recommendations?keyword=${encodeURIComponent(keyword)}`)
const recommendations = await res.json()
```

The Vite dev server's proxy config (`vite.config.js`) already forwards
`/api/*` to `http://localhost:8000`, so no CORS headaches during local dev.
