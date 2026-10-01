"""Gemini Pro integration for expanding comic panel outlines into detailed story, narration, and dialogue."""

import logging
from typing import Any, Dict, List
from app.config import settings

logger = logging.getLogger("comiccraft.gemini_pro")


def _get_mock_story(
    outline: List[Dict[str, Any]],
    character_name: str = "The Hero",
    tone: str = "Adventure",
) -> str:
    """Generate realistic, cohesive comic narration, caption, and dialogue for mock/offline testing."""
    char = character_name.strip() or "The Hero"
    story_blocks = []

    mock_scripts = [
        {
            "caption": "Whispers carried on the wind, tales of ancient magic and long-lost prophecies.",
            "narration": f"{char}, known for curiosity and bravery, stood at the frontier of the unknown realm. Shadows stretched long across the terrain.",
            "dialogue": f'{char}: "Whatever lies ahead, there is no turning back now."',
        },
        {
            "caption": "A faint, rhythmic hum emanated from beneath the ancient stones.",
            "narration": f"Guided by an inexplicable instinct, {char} knelt before the mystical crystal. Its radiant pulse illuminated the surroundings.",
            "dialogue": f'{char}: "Incredible... It has been waiting for centuries."',
        },
        {
            "caption": "CRACKLE! The ambient air ionized, turning cold and sharp.",
            "narration": f"Awakened by the artifact's light, spectral guardians materialized from the shadows, blocking every escape route.",
            "dialogue": f'{char}: "Guardians of the crystal! Stand back, I mean no harm!"',
        },
        {
            "caption": "BOOM! Pure celestial light erupted across the clearing.",
            "narration": f"Refusing to yield, {char} channeled courage into the crystal. A brilliant shockwave shattered the darkness.",
            "dialogue": f'{char}: "Light always conquers the dark!"',
        },
        {
            "caption": "Golden dusk enveloped the tranquil expanse.",
            "narration": f"With the guardians pacified and the path illuminated, {char} took the first step toward the next chapter of the saga.",
            "dialogue": f'{char}: "The realm is safe. Today, our true adventure begins."',
        },
    ]

    for idx, panel in enumerate(outline[:5], 1):
        title = panel.get("title", f"Panel {idx}")
        script = mock_scripts[idx - 1] if idx <= len(mock_scripts) else mock_scripts[-1]

        block = (
            f"**Panel {idx}: {title}**\n"
            f"**CAPTION:** {script['caption']}\n"
            f"**NARRATION:** {script['narration']}\n"
            f"**DIALOGUE:** {script['dialogue']}"
        )
        story_blocks.append(block)

    return "\n\n".join(story_blocks)


def generate_story(
    outline: List[Dict[str, Any]],
    character_name: str = "",
    tone: str = "",
) -> str:
    """Expand the 5-panel comic outline into detailed narration, dialogue, and atmospheric captions.

    Args:
        outline: List of 5 panel dictionaries (from generate_outline)
        character_name: Name of the main protagonist
        tone: Desired emotional tone (Dramatic, Funny, etc.)

    Returns:
        Formatted multi-panel comic story string.
    """
    if settings.MOCK_AI or not settings.GEMINI_API_KEY:
        logger.info("Running generate_story in MOCK mode (MOCK_AI=%s)", settings.MOCK_AI)
        return _get_mock_story(
            outline=outline,
            character_name=character_name or "The Hero",
            tone=tone or "Adventure",
        )

    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        model_name = settings.GEMINI_STORY_MODEL or "gemini-1.5-pro"

        # Build formatted list of outline panels for Gemini
        formatted_outline = "\n".join(
            [
                f"Panel {p.get('panel', idx + 1)}: {p.get('title', '')}\n"
                f"  Scene: {p.get('scene_description', '')}"
                for idx, p in enumerate(outline[:5])
            ]
        )

        prompt = f"""You are a professional comic book writer.
Given the following 5-panel breakdown for a comic starring '{character_name or "our protagonist"}', write an engaging comic story with rich narration, atmospheric captions, and character dialogue for each panel.

Tone: {tone or 'Dramatic comic tone'}

Panel Outline:
{formatted_outline}

Guidelines:
1. Maintain consistent character personality and tone across all five panels.
2. For EACH of the 5 panels, you MUST strictly use the following header and fields:
**Panel X: Title**
**CAPTION:** Short environmental/ambient atmosphere description
**NARRATION:** 1-2 sentences of storytelling narrative
**DIALOGUE:** Character speech line(s) in quotation marks, e.g. Character: "Words here"

Keep the panels clearly separated by two newlines.
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        text = response.text.strip() if hasattr(response, "text") and response.text else ""

        if not text or len(text) < 50:
            logger.warning("Gemini Pro returned empty or brief response. Using mock fallback.")
            return _get_mock_story(outline, character_name, tone)

        logger.info("Raw Gemini Pro story received (%d characters)", len(text))
        return text

    except Exception as exc:
        logger.error("Error generating story via Gemini Pro: %s. Falling back to mock story.", exc)
        return _get_mock_story(outline, character_name, tone)
