from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, Base
from app.models import *  # noqa: F401,F403 — ensures models are registered

from app.routers import babies, feeding, sleep, diaper, tummy_time, growth, medication, milestone, dashboard

app = FastAPI(
    title="BabyTracker API",
    description="API para seguimiento de cuidado de bebés",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(babies.router)
app.include_router(feeding.router)
app.include_router(sleep.router)
app.include_router(diaper.router)
app.include_router(tummy_time.router)
app.include_router(growth.router)
app.include_router(medication.router)
app.include_router(milestone.router)
app.include_router(dashboard.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


@app.get("/health")
def health():
    return {"status": "ok"}
