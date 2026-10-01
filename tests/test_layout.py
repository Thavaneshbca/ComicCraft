"""Unit tests for ComicCraft layout builder."""

from app.layout_builder import build_comic_layout


def test_build_comic_layout_structure():
    """Verify layout builder produces 5 structured panel dictionaries."""
    mock_outline = [
        {"panel": 1, "title": "The Awakening", "scene_description": "Hero wakes up.", "image_prompt": "Hero in bedroom"},
        {"panel": 2, "title": "The Call", "scene_description": "A letter arrives.", "image_prompt": "Letter on table"},
        {"panel": 3, "title": "The Shadow", "scene_description": "A storm gathers.", "image_prompt": "Stormy sky"},
        {"panel": 4, "title": "The Battle", "scene_description": "Hero confronts enemy.", "image_prompt": "Hero sword duel"},
        {"panel": 5, "title": "The Dawn", "scene_description": "Peace returns.", "image_prompt": "Sunrise horizon"},
    ]
    mock_story = (
        "**Panel 1: The Awakening**\n"
        "**CAPTION:** Dawn breaks.\n"
        "**NARRATION:** The hero stirred.\n"
        '**DIALOGUE:** Hero: "Time to move."\n\n'
        "**Panel 2: The Call**\n"
        "**CAPTION:** The mail carrier arrives.\n"
        "**NARRATION:** An urgent missive.\n"
        '**DIALOGUE:** Hero: "A royal summons!"\n\n'
        "**Panel 3: The Shadow**\n"
        "**CAPTION:** Thunder rumbled.\n"
        "**NARRATION:** Darkness fell.\n"
        '**DIALOGUE:** Hero: "Trouble comes."\n\n'
        "**Panel 4: The Battle**\n"
        "**CAPTION:** Clashing steel.\n"
        "**NARRATION:** The hero struck.\n"
        '**DIALOGUE:** Hero: "For the realm!"\n\n'
        "**Panel 5: The Dawn**\n"
        "**CAPTION:** Calm restored.\n"
        "**NARRATION:** Victory achieved.\n"
        '**DIALOGUE:** Hero: "We prevailed."'
    )
    mock_images = [
        "static/panels/p1.png",
        "static/panels/p2.png",
        "static/panels/p3.png",
        "static/panels/p4.png",
        "static/panels/p5.png",
    ]

    layout = build_comic_layout(mock_images, mock_story, mock_outline)

    assert len(layout) == 5
    for idx, panel in enumerate(layout, 1):
        assert panel["panel"] == idx
        assert panel["image_path"] == f"static/panels/p{idx}.png"
        assert panel["web_image_path"] == f"/static/panels/p{idx}.png"
        assert panel["title"] is not None
        assert "caption" in panel
        assert "narration" in panel
        assert "dialogue" in panel


def test_build_comic_layout_handles_missing_elements():
    """Verify layout builder handles short or partial lists gracefully."""
    layout = build_comic_layout([], "", [])
    assert len(layout) == 5
    for p in layout:
        assert p["panel"] >= 1
        assert "title" in p
