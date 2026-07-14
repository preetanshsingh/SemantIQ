from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analyze, score, recommendations, paa, entities, readability, brief, links, url_analyze

app = FastAPI(
    title="SemantIQ API",
    description="Backend for SemantIQ — semantic SEO and content optimization.",
    version="0.1.0",
)

# Allow the local Vite dev server (and the same origin in prod) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(score.router, prefix="/api", tags=["score"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])
app.include_router(paa.router, prefix="/api", tags=["paa"])
app.include_router(entities.router, prefix="/api", tags=["entities"])
app.include_router(readability.router, prefix="/api", tags=["readability"])
app.include_router(brief.router, prefix="/api", tags=["brief"])
app.include_router(links.router, prefix="/api", tags=["links"])
app.include_router(url_analyze.router, prefix="/api", tags=["url-analyze"])


@app.get("/")
def root():
    return {"status": "SemantIQ API is running", "docs": "/docs"}
