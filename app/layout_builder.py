"""Layout builder module for ComicCraft: binds outline, text, and images into structured panel data."""

import logging
import re
from typing import Any, Dict, List, Union
from app.utils import parse_story_blocks

logger = logging.getLogger("comiccraft.layout_builder")


def build_comic_layout(
    image_paths: List[str],
    full_story: Union[str, List[Dict[str, Any]]],
    outline: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Assemble panel outline, full story narration/dialogue, and generated images into structured layout.

    Follows the PDF specification while providing defensive parsing for web & PDF export.

    Args:
        image_paths: List of file/web paths to generated images for each panel
        full_story: Story text string or pre-parsed list of panel stories
        outline: List of outline dictionaries (from generate_outline)

    Returns:
        Structured list of 5 panel dictionaries ready for Jinja2 templates, PDF exporter, and API responses.
    """
    layout = []

    # 1. Parse full_story into panel segments
    if isinstance(full_story, str):
        story_panels_raw = full_story.split("**Panel")
        story_panels = [f"**Panel{panel}" for panel in story_panels_raw if panel.strip()]
        parsed_blocks = parse_story_blocks(full_story)
    else:
        story_panels = [str(item) for item in full_story]
        parsed_blocks = full_story if isinstance(full_story, list) else []

    total_panels = max(len(image_paths), len(outline), len(story_panels), 5)
    # Target exactly 5 panels as per ComicCraft spec
    target_count = 5

    for idx in range(1, target_count + 1):
        # Extract outline info
        panel_info = outline[idx - 1] if idx - 1 < len(outline) else {}
        title = panel_info.get("title", f"Panel {idx}")
        scene_desc = panel_info.get("scene_description", "")
        img_prompt = panel_info.get("image_prompt", "")

        # Extract image path
        img_path = image_paths[idx - 1] if idx - 1 < len(image_paths) else ""
        web_img_path = img_path if img_path.startswith("/") or img_path.startswith("http") else f"/{img_path}"

        # Extract text segment
        raw_text_segment = story_panels[idx - 1] if idx - 1 < len(story_panels) else ""
        lines = [ln for ln in raw_text_segment.strip().splitlines() if ln.strip()]

        # Clean text by removing panel title line if present
        if lines and lines[0].lower().startswith("**panel"):
            cleaned_text = "\n".join(lines[1:]).strip()
        else:
            cleaned_text = "\n".join(lines).strip()

        # Extract caption, narration, and dialogue from parsed blocks or regex
        caption = ""
        narration = ""
        dialogue = ""

        if idx - 1 < len(parsed_blocks) and isinstance(parsed_blocks[idx - 1], dict):
            block = parsed_blocks[idx - 1]
            caption = block.get("caption", "")
            narration = block.get("narration", "")
            dialogue = block.get("dialogue", "")

        # Fallback regex extraction from cleaned_text if needed
        if not caption:
            c_match = re.search(r"\*\*CAPTION[:\*]*\s*(.*?)(?=\*\*(?:NARRATION|DIALOGUE)|$)", cleaned_text, re.DOTALL | re.IGNORECASE)
            if c_match:
                caption = c_match.group(1).strip()

        if not narration:
            n_match = re.search(r"\*\*NARRATION[:\*]*\s*(.*?)(?=\*\*(?:CAPTION|DIALOGUE)|$)", cleaned_text, re.DOTALL | re.IGNORECASE)
            if n_match:
                narration = n_match.group(1).strip()
            elif not caption and not dialogue:
                narration = cleaned_text

        if not dialogue:
            d_match = re.search(r"\*\*DIALOGUE[:\*]*\s*(.*?)(?=\*\*(?:CAPTION|NARRATION)|$)", cleaned_text, re.DOTALL | re.IGNORECASE)
            if d_match:
                dialogue = d_match.group(1).strip()

        panel_dict = {
            "panel": idx,
            "panel_number": idx,
            "title": title,
            "image_path": img_path,
            "web_image_path": web_img_path,
            "text": cleaned_text or narration or scene_desc,
            "scene_description": scene_desc,
            "image_prompt": img_prompt,
            "caption": caption,
            "narration": narration or cleaned_text,
            "dialogue": dialogue,
        }
        layout.append(panel_dict)

    logger.info("Successfully built comic layout with %d panels", len(layout))
    return layout
