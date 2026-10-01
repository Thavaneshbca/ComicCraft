"""Live verification script for ComicCraft running server."""

import requests

base = "http://127.0.0.1:8000"

print("--- 1. Testing GET / ---")
r = requests.get(f"{base}/")
print("Status:", r.status_code, "Length:", len(r.text))
assert r.status_code == 200
assert "ComicCraft" in r.text
assert "story_prompt" in r.text

print("--- 2. Testing GET /health ---")
r = requests.get(f"{base}/health")
print("Status:", r.status_code, "JSON:", r.json())
assert r.status_code == 200

print("--- 3. Testing GET /docs ---")
r = requests.get(f"{base}/docs")
print("Status:", r.status_code)
assert r.status_code == 200

print("--- 4. Testing POST /generate (Form Submission) ---")
form_data = {
    "story_prompt": "A brave fox exploring an enchanted forest uncovers an ancient glowing relic.",
    "character_name": "Free the Red Fox",
    "setting": "Enchanted Forest",
    "tone": "Dramatic",
    "art_style": "Comic Book",
}
r = requests.post(f"{base}/generate", data=form_data)
print("Status:", r.status_code, "Length:", len(r.text))
assert r.status_code == 200
assert "PANEL 1" in r.text
assert "PANEL 5" in r.text
assert "download-pdf-btn" in r.text

print("--- 5. Testing POST /generate-comic/json ---")
json_payload = {
    "story_prompt": "A cybernetic samurai defends a neon pagoda from rogue androids.",
    "character_name": "Kaelen the Ronin",
    "setting": "Cyberpunk Metropolis",
    "tone": "Adventure",
    "art_style": "Anime",
}
r = requests.post(f"{base}/generate-comic/json", json=json_payload)
print("Status:", r.status_code)
assert r.status_code == 200
res = r.json()
print("Panels returned:", len(res["panels"]))
print("PDF path:", res["pdf_path"])
assert len(res["panels"]) == 5
assert res["pdf_path"].endswith(".pdf")

print("--- 6. Testing GET /test-image ---")
r = requests.get(f"{base}/test-image?prompt=A+serene+crystal+lake+at+twilight")
print("Status:", r.status_code, "Image path:", r.json()["web_image_path"])
assert r.status_code == 200

print("--- 7. Testing GET /export-success ---")
pdf_path = res["pdf_path"]
r = requests.get(f"{base}/export-success?pdf_path={pdf_path}")
print("Status:", r.status_code)
assert r.status_code == 200
assert "Comic Exported Successfully!" in r.text

print("\n>>> ALL VERIFICATION CHECKS PASSED PERFECTLY! <<<")
