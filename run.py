"""Execution entrypoint for ComicCraft."""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting ComicCraft on http://{settings.HOST}:{settings.PORT}")
    print(f"Interactive API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"MOCK_AI Mode: {settings.MOCK_AI}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
