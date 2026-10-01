"""Gemini Flash integration for structured 5-panel comic outline generation."""

import json
import logging
from typing import Any, Dict, List
from app.config import settings
from app.utils import clean_json_response

logger = logging.getLogger("comiccraft.gemini_flash")


def _get_mock_outline(
    user_prompt: str,
    character_name: str = "Hero",
    setting: str = "Enchanted Forest",
    tone: str = "Adventure",
    art_style: str = "Comic Book",
) -> List[Dict[str, Any]]:
    """Generate a high-quality mock 5-panel comic outline for testing & offline mode."""
    char = character_name.strip() or "The Hero"
    loc = setting.strip() or "Enchanted Realm"
    style_desc = f"{art_style} style, vivid dynamic colors, comic inks, clean line art, high detail"

    return [
        {
            "panel": 1,
            "title": f"The Journey Begins in {loc}",
            "scene_description": f"{char} stands at the threshold of {loc}, gazing toward the unknown horizon with determined eyes. Golden dawn light cuts through the landscape.",
            "image_prompt": f"Establishing wide shot of {char} standing at the mysterious entrance of {loc}. Morning light filtering through trees and architecture, {style_desc}, cinematic composition, 8k resolution, comic illustration.",
        },
        {
            "panel": 2,
            "title": "A Curious Discovery",
            "scene_description": f"Deeper inside {loc}, {char} uncovers an ancient glowing artifact partially buried under crystalline stones and overgrown vines.",
            "image_prompt": f"Medium shot of {char} kneeling down, reaching out toward an ancient glowing crystalline relic emitting radiant azure light, {loc} in background, {style_desc}, dramatic lighting, expressive face.",
        },
        {
            "panel": 3,
            "title": "Sudden Danger",
            "scene_description": f"The ground trembles as mystical guardians emerge from the shadows of {loc}, surrounding {char} with crackling energy.",
            "image_prompt": f"Dynamic action panel, shadowy mystical energy creatures awakening around {char} in {loc}, high tension, glowing eyes, swirling dust, {style_desc}, dynamic perspective, comic action.",
        },
        {
            "panel": 4,
            "title": "The Decisive Spark",
            "scene_description": f"With a brave leap, {char} channels the ancient relic's power, unleashing a brilliant shield of luminescence that scatters the shadowy guardians.",
            "image_prompt": f"Climatic hero shot, {char} leaping upward raising the glowing relic which radiates a shockwave of golden light, illuminating {loc}, particles flying, {style_desc}, heroic pose, cinematic.",
        },
        {
            "panel": 5,
            "title": f"Triumph in {loc}",
            "scene_description": f"Peace returns to {loc}. Holding the energized relic, {char} smiles with newfound wisdom as the path forward opens.",
            "image_prompt": f"Warm concluding panel, {char} holding the peaceful humming relic, smiling confidently into the warm sunset over {loc}, calm atmosphere, {style_desc}, beautiful comic ending.",
        },
    ]


def generate_outline(
    user_prompt: str,
    character_name: str = "",
    setting: str = "",
    tone: str = "",
    art_style: str = "",
) -> List[Dict[str, Any]]:
    """Generate a structured 5-panel comic outline using Google Gemini Flash or mock mode.

    Returns:
        List of 5 panel dictionaries containing:
        - 'panel' (int: 1-5)
        - 'title' (str)
        - 'scene_description' (str)
        - 'image_prompt' (str)
    """
    # 1. Check if running in mock mode or API key is absent
    if settings.MOCK_AI or not settings.GEMINI_API_KEY:
        logger.info("Running generate_outline in MOCK mode (MOCK_AI=%s)", settings.MOCK_AI)
        return _get_mock_outline(
            user_prompt=user_prompt,
            character_name=character_name or "Hero",
            setting=setting or "The Realm",
            tone=tone or "Adventure",
            art_style=art_style or "Comic Book",
        )

    # 2. Real Gemini API Call
    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        model_name = settings.GEMINI_OUTLINE_MODEL or "gemini-1.5-flash"

        system_prompt = f"""You are a professional comic book creator and story planner.
Your task is to generate a strictly formatted JSON array containing exactly 5 comic panel descriptions for a cohesive, compelling 5-panel comic strip.

STORY PREMISE: {user_prompt}
MAIN CHARACTER: {character_name or 'Unspecified Hero'}
SETTING: {setting or 'Fantasy World'}
TONE: {tone or 'Dramatic'}
ART STYLE: {art_style or 'Comic Book'}

Guidelines:
1. Generate EXACTLY 5 panels following a 5-beat comic narrative:
   - Panel 1: Exposition / Hook
   - Panel 2: Inciting Incident / Discovery
   - Panel 3: Rising Tension / Conflict
   - Panel 4: Climax / Action
   - Panel 5: Resolution / Aftermath
2. Keep the main character '{character_name}' visually consistent across all panels.
3. Every 'image_prompt' must contain vivid visual details suitable for Stable Diffusion (character appearance, composition, lighting, camera angle, atmosphere, art style '{art_style}').
4. Do NOT include dialogue inside the image_prompt (dialogue will be rendered separately).
5. Output ONLY a valid JSON array of 5 objects with no extra text or commentary.

Each JSON object must have these exact keys:
- "panel": integer (1 to 5)
- "title": short catchy panel title string
- "scene_description": clear 1-2 sentence description of the action and atmosphere
- "image_prompt": detailed visual prompt for image generation incorporating '{art_style}' style

Example JSON output format:
[
  {{
    "panel": 1,
    "title": "Title Here",
    "scene_description": "Scene description here",
    "image_prompt": "Visual prompt for diffusion model here"
  }}
]
"""

        response = client.models.generate_content(
            model=model_name,
            contents=system_prompt,
        )
        output_text = response.text.strip() if hasattr(response, "text") and response.text else ""
        logger.info("Raw Gemini Flash response received (%d chars)", len(output_text))

        cleaned_text = clean_json_response(output_text)
        panel_data = json.loads(cleaned_text)

        if not isinstance(panel_data, list):
            raise ValueError(f"Gemini response is not a JSON list: {type(panel_data)}")

        # Normalize and validate panels
        validated_panels: List[Dict[str, Any]] = []
        for idx, item in enumerate(panel_data[:5], 1):
            if not isinstance(item, dict):
                continue
            validated_panels.append({
                "panel": int(item.get("panel", idx)),
                "title": str(item.get("title", f"Panel {idx}")),
                "scene_description": str(item.get("scene_description", "")),
                "image_prompt": str(item.get("image_prompt", "")),
            })

        # Ensure we have exactly 5 panels
        while len(validated_panels) < 5:
            missing_idx = len(validated_panels) + 1
            validated_panels.append({
                "panel": missing_idx,
                "title": f"Panel {missing_idx}: The Story Continues",
                "scene_description": f"The story develops further with {character_name or 'the character'}.",
                "image_prompt": f"Comic book panel depicting {character_name or 'the character'} in {setting or 'the scene'}, {art_style} style, dramatic lighting.",
            })

        return validated_panels[:5]

    except Exception as exc:
        logger.error("Error generating outline via Gemini Flash: %s. Falling back to structured mock outline.", exc)
        return _get_mock_outline(
            user_prompt=user_prompt,
            character_name=character_name or "Hero",
            setting=setting or "The Realm",
            tone=tone or "Adventure",
            art_style=art_style or "Comic Book",
        )
