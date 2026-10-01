"""Integration tests for ComicCraft FastAPI routes."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home_page():
    """Verify that homepage loads with 200 OK and contains core form elements."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text
    assert "story_prompt" in response.text
    assert "character_name" in response.text
    assert "btn-generate-comic" in response.text


def test_health_endpoint():
    """Verify health endpoint returns proper operational status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "ComicCraft"
    assert "mock_ai" in data
    assert "image_provider" in data


def test_generate_comic_form():
    """Verify form submission generates comic preview page with 5 panels and PDF link."""
    payload = {
        "story_prompt": "A brave explorer discovers a mystical hidden valley guarded by ancient stone golems.",
        "character_name": "Rusty the Adventurer",
        "setting": "Enchanted Forest",
        "tone": "Adventure",
        "art_style": "Comic Book",
    }
    response = client.post("/generate", data=payload)
    assert response.status_code == 200
    assert "ComicCraft Preview" in response.text
    assert "PANEL 1" in response.text
    assert "PANEL 5" in response.text
    assert "download-pdf-btn" in response.text


def test_generate_comic_form_validation():
    """Verify form validation rejects missing required fields."""
    payload = {
        "story_prompt": "",
        "character_name": "",
        "setting": "",
    }
    response = client.post("/generate", data=payload)
    assert response.status_code in (400, 422)


def test_generate_comic_json_api():
    """Verify JSON API generates comic and returns structured JSON with 5 panels."""
    payload = {
        "story_prompt": "A rogue astronaut uncovers an alien beacon transmitting mysterious signals.",
        "character_name": "Commander Stella",
        "setting": "Space",
        "tone": "Dramatic",
        "art_style": "Anime",
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["panels"]) == 5
    assert data["character_name"] == "Commander Stella"
    assert data["pdf_path"].endswith(".pdf")
    assert "download_url" in data


def test_test_image_get():
    """Verify test-image GET endpoint generates test comic illustration."""
    response = client.get("/test-image?prompt=A+cyberpunk+street+in+neon+rain")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "web_image_path" in data
    assert data["web_image_path"].endswith(".png")


def test_test_image_post():
    """Verify test-image POST endpoint generates test comic illustration."""
    payload = {"prompt": "A magical library with floating books"}
    response = client.post("/test-image", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "image_path" in data


def test_export_success_page():
    """Verify export-success page renders with download link."""
    response = client.get("/export-success?pdf_path=static/exports/comic_test.pdf")
    assert response.status_code == 200
    assert "Comic Exported Successfully!" in response.text
    assert "comic_test.pdf" in response.text
