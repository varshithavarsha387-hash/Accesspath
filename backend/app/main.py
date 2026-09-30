from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .database.db import init_db, seed_initial_barriers_if_empty
from .routes import users, routes, barriers, navigation, dashboard, geocoding

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and seed barriers
    init_db()
    seed_initial_barriers_if_empty()
    yield
    # Shutdown

app = FastAPI(
    title="AccessPath API",
    description="Real-Time Accessibility Navigation Backend & AI Barrier Classification Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration to allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(users.router)
app.include_router(routes.router)
app.include_router(barriers.router)
app.include_router(navigation.router)
app.include_router(dashboard.router)
app.include_router(geocoding.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "AccessPath",
        "version": "1.0.0",
        "ai_engine": "Active (Vision & NLP)"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
