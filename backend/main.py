#!/usr/bin/env python3
"""
Website Documentation Scraper - Backend API
===========================================

FastAPI backend service for intelligent web scraping with LLM guidance.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from routes.analysis import router as analysis_router
from routes.scraping import router as scraping_router
from routes.results import router as results_router
from routes.prompts import router as prompts_router
from services.job_manager import JobManager
from services.storage_service import StorageService

# Global service instances
job_manager = None
storage_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    global job_manager, storage_service
    
    # Startup
    print("🚀 Starting Website Documentation Scraper Backend...")
    
    # Initialize services
    storage_service = StorageService()
    job_manager = JobManager(storage_service)
    
    # Set service instances for routes
    app.state.job_manager = job_manager
    app.state.storage_service = storage_service
    
    print("✅ Backend services initialized")
    yield
    
    # Shutdown
    print("🛑 Shutting down backend services...")
    await job_manager.shutdown()
    print("✅ Backend shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Website Documentation Scraper API",
    description="Intelligent web scraping with LLM guidance",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(scraping_router, prefix="/api/v1/scraping", tags=["scraping"])
app.include_router(results_router, prefix="/api/v1/results", tags=["results"])
app.include_router(prompts_router, prefix="/api/v1/prompts", tags=["prompts"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Website Documentation Scraper API",
        "version": "1.0.0",
        "description": "Intelligent web scraping with LLM guidance",
        "docs_url": "/docs",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "job_manager": job_manager.is_healthy() if job_manager else False,
            "storage_service": storage_service.is_healthy() if storage_service else False,
            "gemini_api": bool(os.environ.get("GOOGLE_APIKEY"))
        }
    }

if __name__ == "__main__":
    # Check required environment variables
    if not os.environ.get("GOOGLE_APIKEY"):
        print("❌ Error: GOOGLE_APIKEY environment variable is not set")
        sys.exit(1)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
