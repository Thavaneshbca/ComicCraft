"""Main FastAPI application entrypoint for ComicCraft."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router
from app.utils import ensure_directories

# Configure logging format
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("comiccraft")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: initialize storage directories and log startup parameters."""
    ensure_directories()
    logger.info("=" * 60)
    logger.info("Starting ComicCraft - AI Comic Story Creator")
    logger.info("Mock AI Mode: %s", settings.MOCK_AI)
    logger.info("Image Provider: %s", settings.IMAGE_PROVIDER)
    logger.info("Gemini Outline Model: %s", settings.GEMINI_OUTLINE_MODEL)
    logger.info("Gemini Story Model: %s", settings.GEMINI_STORY_MODEL)
    logger.info("Static Directory: %s", settings.STATIC_DIR)
    logger.info("=" * 60)
    yield
    logger.info("Shutting down ComicCraft application...")


app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Full-stack AI Comic Creation application utilizing Google Gemini Models and Stable Diffusion.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# Include main application routes
app.include_router(router)


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Friendly 404 handler for HTML requests and API calls."""
    if "text/html" in request.headers.get("accept", ""):
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>404 - Page Not Found | ComicCraft</title>
            <style>
              body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 100px 20px; }}
              h1 {{ font-size: 3rem; color: #f59e0b; margin-bottom: 10px; }}
              p {{ font-size: 1.2rem; color: #94a3b8; margin-bottom: 25px; }}
              a {{ display: inline-block; background: #3b82f6; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; }}
            </style>
            </head>
            <body>
              <h1>404: Lost in the Multiverse</h1>
              <p>The comic panel or page you are looking for does not exist.</p>
              <a href="/">Return to Comic Studio</a>
            </body>
            </html>
            """,
            status_code=404,
        )
    return JSONResponse(status_code=404, content={"error": "Not Found", "detail": str(exc)})


@app.exception_handler(500)
async def custom_500_handler(request: Request, exc):
    """User-friendly 500 handler without leaking sensitive internal credentials."""
    logger.error("Internal Server Error on %s: %s", request.url.path, exc)
    if "text/html" in request.headers.get("accept", ""):
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error | ComicCraft</title>
            <style>
              body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 100px 20px; }}
              h1 {{ font-size: 2.5rem; color: #ef4444; margin-bottom: 10px; }}
              p {{ font-size: 1.1rem; color: #94a3b8; margin-bottom: 25px; }}
              a {{ display: inline-block; background: #3b82f6; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; }}
            </style>
            </head>
            <body>
              <h1>Oops! Comic Engine Stumbled</h1>
              <p>An unexpected error occurred during generation. Please verify your settings or try again.</p>
              <a href="/">Try Again</a>
            </body>
            </html>
            """,
            status_code=500,
        )
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": "Comic generation encountered an issue."},
    )
