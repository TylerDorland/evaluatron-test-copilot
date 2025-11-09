from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, companies, topics, queries, evaluations, scheduled_tests

app = FastAPI(
    title="Evaluatron - LLM Response Tracking",
    description="Multi-tenant LLM response tracking and evaluation platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(queries.router, prefix="/api/queries", tags=["queries"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["evaluations"])
app.include_router(scheduled_tests.router, prefix="/api/scheduled-tests", tags=["scheduled-tests"])


@app.get("/")
def root():
    return {
        "message": "Welcome to Evaluatron API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
