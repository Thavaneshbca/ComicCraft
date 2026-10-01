"""Image generation module for ComicCraft supporting Hugging Face, local Diffusers, and Mock generation."""

import hashlib
import io
import logging
import math
from pathlib import Path
from typing import Optional
import requests
from PIL import Image, ImageDraw, ImageFont

from app.config import settings
from app.utils import sanitize_filename

logger = logging.getLogger("comiccraft.image_generator")

# Cached pipeline instance for local diffusers to avoid reloading weights repeatedly
_LOCAL_DIFFUSER_PIPE = None


def _create_mock_comic_image(prompt: str, target_path: Path, panel_idx: int = 1) -> Path:
    """Generate a stylized, comic-book aesthetic placeholder image using Pillow.

    Creates dynamic colors, action rays, comic border, and styled typographic banners.
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 768, 640

    # Color palettes for comic panels
    palettes = [
        {"bg_top": (24, 38, 72), "bg_bot": (48, 86, 144), "accent": (255, 204, 0), "theme": "DAWN EXPEDITION"},
        {"bg_top": (16, 52, 42), "bg_bot": (34, 112, 94), "accent": (80, 240, 180), "theme": "MYSTIC DISCOVERY"},
        {"bg_top": (54, 16, 32), "bg_bot": (120, 32, 64), "accent": (255, 90, 95), "theme": "RISING TENSION"},
        {"bg_top": (44, 20, 68), "bg_bot": (102, 44, 145), "accent": (255, 180, 50), "theme": "CLIMACTIC CLASH"},
        {"bg_top": (64, 40, 16), "bg_bot": (148, 92, 36), "accent": (255, 230, 110), "theme": "TRIUMPHANT DAWN"},
    ]
    palette = palettes[(panel_idx - 1) % len(palettes)]

    img = Image.new("RGB", (width, height), palette["bg_top"])
    draw = ImageDraw.Draw(img)

    # 1. Render vertical gradient
    for y in range(height):
        ratio = y / height
        r = int(palette["bg_top"][0] * (1 - ratio) + palette["bg_bot"][0] * ratio)
        g = int(palette["bg_top"][1] * (1 - ratio) + palette["bg_bot"][1] * ratio)
        b = int(palette["bg_top"][2] * (1 - ratio) + palette["bg_bot"][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Render dynamic comic action rays from center
    center_x, center_y = width // 2, int(height * 0.45)
    ray_count = 24
    max_radius = int(math.hypot(width, height))
    for i in range(0, ray_count, 2):
        angle1 = (2 * math.pi / ray_count) * i
        angle2 = (2 * math.pi / ray_count) * (i + 0.6)
        x1 = center_x + max_radius * math.cos(angle1)
        y1 = center_y + max_radius * math.sin(angle1)
        x2 = center_x + max_radius * math.cos(angle2)
        y2 = center_y + max_radius * math.sin(angle2)
        ray_overlay = (
            min(255, palette["accent"][0] + 50),
            min(255, palette["accent"][1] + 50),
            min(255, palette["accent"][2] + 50),
        )
        draw.polygon([(center_x, center_y), (x1, y1), (x2, y2)], fill=(*palette["bg_bot"], 40))

    # 3. Outer Comic Panel Border
    border_thickness = 10
    draw.rectangle(
        [(border_thickness // 2, border_thickness // 2),
         (width - border_thickness // 2, height - border_thickness // 2)],
        outline=(20, 20, 25),
        width=border_thickness,
    )
    # Inner border line
    draw.rectangle(
        [(border_thickness + 6, border_thickness + 6),
         (width - border_thickness - 6, height - border_thickness - 6)],
        outline=(240, 240, 245),
        width=2,
    )

    # 4. Stylized Graphic Center Elements (Comic emblem)
    emblem_radius = 110
    draw.ellipse(
        [
            (center_x - emblem_radius - 6, center_y - emblem_radius - 6),
            (center_x + emblem_radius + 6, center_y + emblem_radius + 6),
        ],
        fill=(15, 18, 25),
        outline=palette["accent"],
        width=5,
    )
    draw.ellipse(
        [
            (center_x - emblem_radius + 10, center_y - emblem_radius + 10),
            (center_x + emblem_radius - 10, center_y + emblem_radius - 10),
        ],
        fill=(*palette["bg_top"], 255),
        outline=(255, 255, 255),
        width=2,
    )

    # 5. Panel Number Badge (Top-left comic callout)
    badge_w, badge_h = 160, 48
    draw.rectangle([(24, 24), (24 + badge_w, 24 + badge_h)], fill=(15, 18, 25), outline=palette["accent"], width=3)
    draw.rectangle([(20, 20), (20 + badge_w, 20 + badge_h)], fill=palette["accent"], outline=(10, 10, 10), width=2)

    # Text rendering with fallback font
    font_large = ImageFont.load_default()
    draw.text((36, 32), f"PANEL #{panel_idx}", fill=(10, 10, 15), font=font_large)

    # 6. Central Emblem Icon / Star
    draw.text((center_x - 30, center_y - 25), "[AI COMIC]", fill=palette["accent"], font=font_large)
    draw.text((center_x - 45, center_y + 5), palette["theme"], fill=(255, 255, 255), font=font_large)

    # 7. Bottom Caption Box for Scene Summary
    banner_y = height - 120
    draw.rectangle([(20, banner_y), (width - 20, height - 20)], fill=(12, 14, 20), outline=(220, 220, 220), width=2)

    # Clean and truncate prompt for display on comic panel
    clean_p = prompt.replace("\n", " ").strip()
    if len(clean_p) > 130:
        clean_p = clean_p[:127] + "..."
    draw.text((35, banner_y + 16), "SCENE VISUALIZATION:", fill=palette["accent"], font=font_large)
    draw.text((35, banner_y + 42), clean_p, fill=(230, 235, 245), font=font_large)

    img.save(target_path, "PNG", quality=95)
    logger.info("Generated mock comic panel illustration: %s", target_path)
    return target_path


def _generate_via_huggingface(prompt: str, target_path: Path) -> Path:
    """Generate image via Hugging Face Inference API using InferenceClient."""
    if not settings.HF_API_KEY:
        raise ValueError("HF_API_KEY is not configured in .env")

    from huggingface_hub import InferenceClient

    model_id = settings.HF_IMAGE_MODEL or "runwayml/stable-diffusion-v1-5"
    client = InferenceClient(token=settings.HF_API_KEY)

    logger.info("Calling Hugging Face Inference API for model: %s", model_id)
    image = client.text_to_image(
        prompt=prompt,
        model=model_id,
        negative_prompt="blurry, low quality, distorted, extra limbs, ugly, bad anatomy, text, watermark",
        num_inference_steps=25,
        guidance_scale=7.5,
    )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(target_path, "PNG")
    logger.info("Saved Hugging Face generated image to: %s", target_path)
    return target_path


def _generate_via_local_diffusers(prompt: str, target_path: Path) -> Path:
    """Generate image using local PyTorch + Diffusers pipeline."""
    global _LOCAL_DIFFUSER_PIPE

    try:
        import importlib
        torch = importlib.import_module("torch")
        diffusers = importlib.import_module("diffusers")
        StableDiffusionPipeline = getattr(diffusers, "StableDiffusionPipeline")
    except (ImportError, ModuleNotFoundError) as err:
        raise RuntimeError(f"Local diffusers requires 'torch' and 'diffusers' packages: {err}")

    if _LOCAL_DIFFUSER_PIPE is None:
        model_id = settings.HF_IMAGE_MODEL or "runwayml/stable-diffusion-v1-5"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        logger.info("Loading local Stable Diffusion model '%s' on %s (%s)...", model_id, device, dtype)
        _LOCAL_DIFFUSER_PIPE = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
        )
        _LOCAL_DIFFUSER_PIPE = _LOCAL_DIFFUSER_PIPE.to(device)

    # Set inference steps based on hardware
    device = getattr(_LOCAL_DIFFUSER_PIPE, "device", "cpu")
    num_steps = 25 if str(device) == "cuda" else 15

    logger.info("Running local Stable Diffusion inference (%d steps)...", num_steps)
    image = _LOCAL_DIFFUSER_PIPE(prompt=prompt, num_inference_steps=num_steps).images[0]
    target_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(target_path, "PNG")
    logger.info("Saved locally generated image to: %s", target_path)
    return target_path


def generate_image(prompt: str, filename: Optional[str] = None) -> str:
    """Generate an illustration for a comic panel based on the image prompt.

    Args:
        prompt: Artistic description for diffusion generation
        filename: Optional explicit file name (without path)

    Returns:
        Web-accessible relative path to the image, e.g. 'static/panels/panel_xxx.png'
    """
    settings.PANELS_DIR.mkdir(parents=True, exist_ok=True)

    if not filename:
        slug = sanitize_filename(prompt, max_length=28)
        prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8]
        filename = f"{slug}_{prompt_hash}.png"

    if not filename.endswith(".png"):
        filename += ".png"

    target_path = settings.PANELS_DIR / filename

    # Return cached image if it already exists
    if target_path.exists() and target_path.stat().st_size > 0:
        logger.info("Using cached panel image at: %s", target_path)
        return f"static/panels/{filename}".replace("\\", "/")

    # Extract panel index heuristic if present in filename or prompt
    panel_idx = 1
    for digit in ("1", "2", "3", "4", "5"):
        if f"panel_{digit}" in filename.lower() or f"panel {digit}" in prompt.lower():
            panel_idx = int(digit)
            break

    # Check execution mode
    if settings.MOCK_AI or settings.IMAGE_PROVIDER == "mock":
        _create_mock_comic_image(prompt, target_path, panel_idx=panel_idx)
        return f"static/panels/{filename}".replace("\\", "/")

    # Real Providers
    if settings.IMAGE_PROVIDER == "local":
        try:
            _generate_via_local_diffusers(prompt, target_path)
            return f"static/panels/{filename}".replace("\\", "/")
        except Exception as exc:
            logger.error("Local Diffusers generation failed (%s). Falling back to mock comic panel.", exc)
            _create_mock_comic_image(prompt, target_path, panel_idx=panel_idx)
            return f"static/panels/{filename}".replace("\\", "/")

    elif settings.IMAGE_PROVIDER == "huggingface":
        try:
            _generate_via_huggingface(prompt, target_path)
            return f"static/panels/{filename}".replace("\\", "/")
        except Exception as exc:
            logger.error("Hugging Face API generation failed (%s). Falling back to mock comic panel.", exc)
            _create_mock_comic_image(prompt, target_path, panel_idx=panel_idx)
            return f"static/panels/{filename}".replace("\\", "/")

    # Default fallback
    _create_mock_comic_image(prompt, target_path, panel_idx=panel_idx)
    return f"static/panels/{filename}".replace("\\", "/")
