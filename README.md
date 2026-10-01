# ComicCraft - AI Comic Story Creator

ComicCraft is a full-stack Generative AI web application that automatically creates personalized 5-panel comic strips, illustrations, and downloadable multi-page PDF comic books from user prompts.

Built with **FastAPI**, **Google Gemini Models** (`Gemini Flash` and `Gemini Pro`), **Stable Diffusion** (via Hugging Face Diffusers or Inference API), and **FPDF2**.

---

## 📖 Table of Contents
- [Architecture & Workflow](#architecture--workflow)
- [Project Directory Structure](#project-directory-structure)
- [Key Features](#key-features)
- [Requirements & Tech Stack](#requirements--tech-stack)
- [Quick Start Guide (Windows / PowerShell)](#quick-start-guide-windows--powershell)
- [Environment Configuration (.env)](#environment-configuration-env)
- [Running Modes: MOCK vs LIVE](#running-modes-mock-vs-live)
  - [1. Development / Mock Mode (`MOCK_AI=true`)](#1-development--mock-mode-mock_aitrue)
  - [2. Live AI Mode (`MOCK_AI=false`)](#2-live-ai-mode-mock_aifalse)
- [Image Generation Providers](#image-generation-providers)
- [API Endpoints & Swagger Documentation](#api-endpoints--swagger-documentation)
- [Running Automated Tests](#running-automated-tests)
- [Troubleshooting & Common Questions](#troubleshooting--common-questions)

---

## 🏗️ Architecture & Workflow

```
[ User (Browser) / API Client ]
             │
             ▼
     FastAPI Backend (app/main.py & app/routes.py)
             │
   ┌─────────┴────────────────────────────────────────┐
   ▼                                                  ▼
[ Gemini Flash (app/gemini_flash.py) ]       [ HTML UI / Templates (Jinja2) ]
   └── Generates structured 5-panel outline             │
             │                                         │
             ▼                                         │
[ Gemini Pro (app/gemini_pro.py) ]                     │
   └── Writes dialogue, narration & captions           │
             │                                         │
             ▼                                         │
[ Image Generator (app/image_generator.py) ]           │
   └── Illustrates each panel (HF / Diffusers / Mock)  │
             │                                         │
             ▼                                         │
[ Layout Builder (app/layout_builder.py) ]             │
   └── Binds panels, images, speech bubbles & captions │
             │                                         │
             ▼                                         │
[ PDF Exporter (app/exporters.py) ]                    │
   └── Compiles multi-page styled PDF via FPDF2        │
             │                                         │
             ▼                                         │
[ Preview & Export Confirmation ] ◄────────────────────┘
```

1. **User Input Form (`index.html`)**: Collects Story Prompt, Main Character Name, Setting, Story Tone, and Art Style (with one-click presets).
2. **Gemini Flash (`app/gemini_flash.py`)**: Plans a structured 5-beat story outline (Beginning, Discovery, Conflict, Climax, Resolution).
3. **Gemini Pro (`app/gemini_pro.py`)**: Expands each panel outline into detailed storyteller narration, character speech lines, and ambient captions.
4. **Image Generator (`app/image_generator.py`)**: Creates comic-style illustrations for all 5 panels using Stable Diffusion or stylized Pillow mock panels.
5. **Layout Builder (`app/layout_builder.py`)**: Organizes visual assets, panel titles, narration, and dialogues into a unified structure.
6. **PDF Exporter (`app/exporters.py`)**: Generates an A4 multi-page comic book PDF with headers, footers, bordered images, and styled dialogue boxes.
7. **Preview & Download (`comic_preview.html` & `export_success.html`)**: Renders the complete comic strip in the browser with offline PDF export.

---

## 📂 Project Directory Structure

```
comicrift/
│
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI entrypoint, lifespan, static mount & error handlers
│   ├── routes.py             # Route handlers for web UI and JSON endpoints
│   ├── gemini_flash.py       # Gemini Flash structured 5-panel outline planner
│   ├── gemini_pro.py         # Gemini Pro detailed narration & dialogue generator
│   ├── image_generator.py    # Diffusion image generator (HF, local Diffusers, & Mock)
│   ├── layout_builder.py     # Assembles outline, stories, and image paths
│   ├── exporters.py          # Multi-page PDF compiler using FPDF2 and Pillow
│   ├── schemas.py            # Pydantic v2 data models for validation & docs
│   ├── config.py             # Application settings & environment loader
│   └── utils.py              # String sanitizers, JSON cleaners, & path helpers
│
├── templates/
│   ├── index.html            # Studio landing page with form & story presets
│   ├── comic_preview.html    # Sequential 5-panel comic viewer with PDF download
│   └── export_success.html   # Download confirmation and success page
│
├── static/
│   ├── css/
│   │   └── style.css         # Modern comic-inspired responsive stylesheet
│   ├── js/
│   │   └── script.js         # Interactive presets, progress overlay, & download redirect
│   ├── panels/               # Generated panel PNG illustrations (.gitkeep)
│   └── exports/              # Generated comic book PDF files (.gitkeep)
│
├── tests/
│   ├── __init__.py
│   ├── test_routes.py        # Web form, JSON API, and health endpoint tests
│   ├── test_layout.py        # Layout builder unit tests
│   ├── test_exporter.py      # PDF generation and unicode handling tests
│   └── verify_live.py        # End-to-end verification script for live server
│
├── .env                      # Active environment settings
├── .env.example              # Example environment template
├── .gitignore                # Git exclusions (venv, generated assets, .env)
├── requirements.txt          # Python dependencies
├── README.md                 # Complete documentation
└── run.py                    # Root runner script
```

---

## ⚙️ Requirements & Tech Stack

- **Python**: 3.10, 3.11, or 3.12 (Python 3.11 recommended on Windows)
- **FastAPI**: 0.110+ high-performance async API framework
- **Uvicorn**: ASGI web server
- **Pydantic**: v2 data validation and schema definitions
- **Jinja2**: HTML templating engine
- **Google Generative AI SDK**: Official Python client for Gemini models
- **FPDF2**: PDF document generation engine
- **Pillow (PIL)**: Image processing and stylized mock illustration generator
- **Pytest & HTTPX**: Automated test suite

---

## 🚀 Quick Start Guide (Windows / PowerShell)

### 1. Clone or Open Workspace
Open the project directory in VS Code or Windows Terminal:
```powershell
cd c:\Users\acer\comicrift
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
```
*(If you have multiple Python versions installed, use `py -3.11 -m venv .venv`)*

### 3. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Launch ComicCraft Application
```powershell
python run.py
```
*Or directly via Uvicorn:*
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Open in Browser
- **Studio Interface**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🔧 Environment Configuration (.env)

A default `.env` is created for you. You can configure it as follows:

```env
# Application Mode (Set to true for offline testing without API keys)
MOCK_AI=true

# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_OUTLINE_MODEL=gemini-1.5-flash
GEMINI_STORY_MODEL=gemini-1.5-pro

# Image Generation Configuration
# Providers: "huggingface", "local" (diffusers), or "mock"
IMAGE_PROVIDER=huggingface
HF_API_KEY=your_huggingface_api_token_here
HF_IMAGE_MODEL=runwayml/stable-diffusion-v1-5

# Directory Paths
OUTPUT_DIR=static
PANELS_DIR=static/panels
EXPORTS_DIR=static/exports

# Server Port & Host
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

---

## 🎭 Running Modes: MOCK vs LIVE

### 1. Development / Mock Mode (`MOCK_AI=true`)
- **No external API keys or GPU required.**
- Instant generation of rich 5-panel comic storylines customized to your input character, setting, tone, and prompt.
- High-quality stylized comic placeholder illustrations are generated on-the-fly using Pillow with action rays, color gradients, and comic book typography.
- Multi-page PDF generation functions completely and produces authentic PDF files in `static/exports/`.
- Perfect for demonstrations, classroom evaluations, UI styling, and integration testing.

### 2. Live AI Mode (`MOCK_AI=false`)
To activate live AI models:
1. In `.env`, set:
   ```env
   MOCK_AI=false
   GEMINI_API_KEY=AIzaSy...your_real_key_here
   ```
2. Obtain a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).
3. Choose your image generation provider (Hugging Face API or Local Diffusers).

---

## 🎨 Image Generation Providers

### Option A: Hugging Face Inference API (Recommended for Cloud / Low-Spec Machines)
- Does **not** require a local GPU or heavy PyTorch downloads.
- In `.env`:
  ```env
  IMAGE_PROVIDER=huggingface
  HF_API_KEY=hf_...your_token_here
  HF_IMAGE_MODEL=runwayml/stable-diffusion-v1-5
  ```
- Obtain a free User Access Token from [Hugging Face Settings](https://huggingface.co/settings/tokens).

### Option B: Local Diffusers Pipeline
- Runs locally on your machine with CUDA acceleration.
- Requires PyTorch with CUDA support and Diffusers:
  ```powershell
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
  pip install diffusers transformers accelerate
  ```
- In `.env`:
  ```env
  IMAGE_PROVIDER=local
  HF_IMAGE_MODEL=runwayml/stable-diffusion-v1-5
  ```
- **Hardware Requirement**: NVIDIA GPU with 6GB+ VRAM (or CPU fallback, which takes ~30-60s per panel).

---

## 📡 API Endpoints & Swagger Documentation

ComicCraft provides both HTML form endpoints and REST JSON APIs:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web homepage with comic generator studio form |
| `POST` | `/generate` | Handles form submission and renders `comic_preview.html` |
| `POST` | `/generate-comic/json` | REST API accepting JSON payload, returns 5 panels + PDF link |
| `GET` | `/export-success` | Confirmation page after downloading PDF |
| `GET` | `/test-image` | Quick image test via GET query parameter `?prompt=...` |
| `POST` | `/test-image` | Quick image test via POST JSON body `{"prompt": "..."}` |
| `GET` | `/health` | Health check returning status and active models |
| `GET` | `/docs` | Interactive Swagger API documentation |
| `GET` | `/redoc` | ReDoc API specification |

### Example JSON API Request
```bash
curl -X POST "http://127.0.0.1:8000/generate-comic/json" \
     -H "Content-Type: application/json" \
     -d '{
       "story_prompt": "A cybernetic samurai defends a neon pagoda from rogue androids.",
       "character_name": "Kaelen the Ronin",
       "setting": "Cyberpunk Metropolis",
       "tone": "Adventure",
       "art_style": "Anime"
     }'
```

---

## 🧪 Running Automated Tests

All tests are completely decoupled from external network dependencies and mock external AI services:

```powershell
.\.venv\Scripts\pytest -v
```

### Test Coverage Highlights:
- `test_routes.py`: Verifies homepage loading, health check, form submissions, JSON API generation, image testing, and export success page.
- `test_layout.py`: Verifies outline, story, and image binding into exactly 5 panels with speech bubbles and ambient captions.
- `test_exporter.py`: Verifies A4 multi-page PDF compilation, image embedding, header/footer layout, and safe unicode character handling.

To run the live server verification script against an already running server:
```powershell
.\.venv\Scripts\python tests/verify_live.py
```

---

## ❓ Troubleshooting & Common Questions

**Q: Where are generated files saved?**
- Panel illustrations: `static/panels/`
- Exported comic PDFs: `static/exports/`

**Q: Can I change the Gemini model versions?**
- Yes! Models are fully configurable via `.env`:
  ```env
  GEMINI_OUTLINE_MODEL=gemini-1.5-flash
  GEMINI_STORY_MODEL=gemini-1.5-pro
  ```
  *(You can also use `gemini-2.0-flash` or any newer model supported by Google AI).*

**Q: What if Hugging Face rate limits or fails?**
- ComicCraft includes defensive fallback: if Hugging Face or local GPU encounters an error, it logs the issue and generates a stylized comic placeholder image so the comic creation workflow never crashes.

**Q: Can I use custom fonts in the PDF?**
- FPDF2 handles standard typography cleanly. ComicCraft cleans smart quotes, em-dashes, and special symbols automatically to ensure reliable rendering on Windows, macOS, and Linux.
