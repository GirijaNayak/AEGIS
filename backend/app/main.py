"""
AEGIS - AI-Based Infrastructure Failure and Recovery Simulator
Main FastAPI Application Entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    infrastructure,
    simulation,
    failures,
    ai,
    recovery,
    experiments,
    reports,
)

app = FastAPI(
    title="AEGIS API — Infrastructure Failure & AI Recovery Simulator",
    description="Academic AI infrastructure simulation platform featuring Fuzzy Logic Risk Assessment, A* Pathfinding, and Genetic Algorithm Recovery Optimization.",
    version="1.0.0",
)

# Enable CORS for local Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register sub-routers
app.include_router(infrastructure.router)
app.include_router(simulation.router)
app.include_router(failures.router)
app.include_router(ai.router)
app.include_router(recovery.router)
app.include_router(experiments.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "system": "AEGIS AI Simulation Platform",
        "status": "online",
        "version": "1.0.0",
        "ai_modules": ["Fuzzy Logic (Mamdani)", "A* Search Algorithm", "Genetic Algorithm"],
        "docs_url": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
