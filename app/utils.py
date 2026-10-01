"""Utility functions for ComicCraft."""

import re
import unicodedata
from typing import Any, Dict, List
from app.config import settings


def sanitize_filename(text: str, max_length: int = 40) -> str:
    """Sanitize a text prompt or title into a safe Windows/cross-platform filename."""
    if not text:
        return "panel"
    # Normalize unicode characters
    cleaned = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # Replace non-alphanumeric characters with underscores
    cleaned = re.sub(r"[^\w\s-]", "", cleaned).strip().lower()
    cleaned = re.sub(r"[-\s]+", "_", cleaned)
    if not cleaned:
        cleaned = "comic_item"
    return cleaned[:max_length]


def ensure_directories() -> None:
    """Ensure all required runtime directories exist."""
    settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    settings.PANELS_DIR.mkdir(parents=True, exist_ok=True)
    settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def clean_json_response(raw_text: str) -> str:
    """Extract and sanitize JSON content from raw LLM responses.

    Handles markdown fences like ```json ... ``` and leading/trailing chatter.
    """
    text = raw_text.strip()

    # Remove markdown code block fences
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop the first line if it contains ```
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        # Drop the last line if it contains ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Find the bounds of JSON list or object
    first_bracket = text.find("[")
    first_brace = text.find("{")

    if first_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
        last_bracket = text.rfind("]")
        if last_bracket != -1:
            text = text[first_bracket : last_bracket + 1]
    elif first_brace != -1:
        last_brace = text.rfind("}")
        if last_brace != -1:
            text = text[first_brace : last_brace + 1]

    # Remove trailing commas before closing braces/brackets (common LLM JSON quirk)
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return text.strip()


def parse_story_blocks(full_story_text: str) -> List[Dict[str, str]]:
    """Parse formatted comic story text into structured narration, dialogue, and caption.

    Supports formats like:
    **Panel 1: Title**
    **CAPTION:** ...
    **NARRATION:** ...
    **DIALOGUE:** ...
    """
    panels = []
    # Split text into panel chunks
    chunks = re.split(r"\*\*Panel\s*(\d+)[:\s-]*([^\n]*)\*\*", full_story_text, flags=re.IGNORECASE)

    if len(chunks) > 1:
        # chunks format: [preamble, panel_num_1, panel_title_1, content_1, panel_num_2, ...]
        i = 1
        while i < len(chunks):
            panel_num = int(chunks[i].strip()) if chunks[i].strip().isdigit() else len(panels) + 1
            panel_title = chunks[i + 1].strip() if i + 1 < len(chunks) else f"Panel {panel_num}"
            content = chunks[i + 2].strip() if i + 2 < len(chunks) else ""

            caption = ""
            narration = ""
            dialogue = ""

            cap_match = re.search(r"\*\*CAPTION[:\*]*\s*(.*?)(?=\*\*(?:NARRATION|DIALOGUE)|$)", content, re.DOTALL | re.IGNORECASE)
            if cap_match:
                caption = cap_match.group(1).strip()

            narr_match = re.search(r"\*\*NARRATION[:\*]*\s*(.*?)(?=\*\*(?:CAPTION|DIALOGUE)|$)", content, re.DOTALL | re.IGNORECASE)
            if narr_match:
                narration = narr_match.group(1).strip()

            dia_match = re.search(r"\*\*DIALOGUE[:\*]*\s*(.*?)(?=\*\*(?:CAPTION|NARRATION)|$)", content, re.DOTALL | re.IGNORECASE)
            if dia_match:
                dialogue = dia_match.group(1).strip()

            # If markers were not used, use the whole chunk as narration
            if not caption and not narration and not dialogue:
                narration = content

            panels.append({
                "panel_number": panel_num,
                "title": panel_title,
                "caption": caption,
                "narration": narration,
                "dialogue": dialogue,
                "raw_content": content,
            })
            i += 3
    else:
        # Fallback split by lines or paragraphs
        sections = [s.strip() for s in full_story_text.split("\n\n") if s.strip()]
        for idx, sec in enumerate(sections, 1):
            panels.append({
                "panel_number": idx,
                "title": f"Panel {idx}",
                "caption": "",
                "narration": sec,
                "dialogue": "",
                "raw_content": sec,
            })

    return panels
