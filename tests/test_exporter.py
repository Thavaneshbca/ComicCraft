"""Unit tests for ComicCraft PDF exporter."""

from app.config import settings
from app.exporters import save_pdf
from app.image_generator import generate_image


def test_save_pdf_generates_valid_file():
    """Verify that save_pdf creates a non-empty, valid PDF file with standard panels."""
    # Generate a sample image to test embedding
    img_path = generate_image("Test comic scene with hero", filename="test_panel_pdf.png")

    mock_layout = [
        {
            "panel": 1,
            "title": "The First Dawn",
            "scene_description": "A sunny clearing where our hero stands ready.",
            "image_path": img_path,
            "caption": "The birds sang a tranquil melody.",
            "narration": "Free gazed across the emerald valley.",
            "dialogue": 'Free: "Adventure awaits!"',
            "text": "The story begins in peaceful serenity.",
        },
        {
            "panel": 2,
            "title": "A Mystery in the Shadows",
            "scene_description": "Dark stone ruins overgrown with glowing ivy.",
            "image_path": img_path,
            "caption": "A sudden gust of wind.",
            "narration": "Curiosity pulled him deeper into the labyrinth.",
            "dialogue": 'Free: "What is this ancient glow?"',
            "text": "Mysterious symbols adorned the stone.",
        },
    ]

    pdf_rel_path = save_pdf(mock_layout, comic_title="Test Adventure Comic")
    assert pdf_rel_path.endswith(".pdf")

    full_path = settings.BASE_DIR / pdf_rel_path.lstrip("/\\")
    assert full_path.exists(), f"PDF was not created at {full_path}"
    assert full_path.stat().st_size > 1000, "PDF file is too small or empty"

    # Verify PDF magic bytes
    with open(full_path, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-", "File does not start with valid PDF signature"


def test_save_pdf_handles_unicode_and_quotes():
    """Verify that unicode characters and smart quotes do not raise encoding exceptions."""
    mock_layout = [
        {
            "panel": 1,
            "title": "Smart Quotes “Testing” & Em—Dash",
            "scene_description": "Testing characters: ‘single quotes’, … ellipsis, • bullet.",
            "image_path": "",
            "caption": "“Listen closely…” whispered the wind.",
            "narration": "He realized — with utmost clarity — it worked.",
            "dialogue": 'Hero: “Onward!”',
        }
    ]

    pdf_rel_path = save_pdf(mock_layout, comic_title="Unicode Test Comic")
    full_path = settings.BASE_DIR / pdf_rel_path.lstrip("/\\")
    assert full_path.exists()
    assert full_path.stat().st_size > 500
