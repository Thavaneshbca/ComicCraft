"""PDF exporter module for ComicCraft using fpdf2."""

import datetime
import logging
import re
from pathlib import Path
from typing import Any, Dict, List
from fpdf import FPDF
from PIL import Image

from app.config import settings

logger = logging.getLogger("comiccraft.exporters")


def _sanitize_pdf_text(text: str) -> str:
    """Sanitize text to be safe for PDF standard font encoding without crashing."""
    if not text:
        return ""
    # Map common smart quotes, dashes, and unicode symbols to safe ASCII/Latin-1
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2014": " -- ",
        "\u2013": " - ",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "*",
        "\u2714": "[OK]",
        "\u2713": "[OK]",
        "\u2728": "*",
        "\u200b": "",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Encode to latin-1 with replacement fallback
    return text.encode("latin-1", "replace").decode("latin-1")


class ComicPDF(FPDF):
    """Custom FPDF class with comic book styling, headers, and footers."""

    def __init__(self, title: str = "ComicCraft AI Comic", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comic_title = _sanitize_pdf_text(title)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """Top banner on each page."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 120, 130)
        self.cell(0, 8, self.comic_title.upper(), border=0, align="L")
        self.cell(0, 8, "COMICCRAFT", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(220, 220, 230)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        """Bottom page footer."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 160)
        self.cell(0, 10, f"ComicCraft AI - Page {self.page_no()}", border=0, align="C")


def save_pdf(layout: List[Dict[str, Any]], comic_title: str = "ComicCraft Comic") -> str:
    """Compile the comic layout into a multi-page PDF document.

    Args:
        layout: List of panel dictionaries containing title, image_path, scene_description, narration, dialogue
        comic_title: Overall title for the comic strip

    Returns:
        Web-accessible relative path to the generated PDF (e.g., 'static/exports/comic_20260928_120000.pdf')
    """
    settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_dest_path = settings.EXPORTS_DIR / filename

    pdf = ComicPDF(title=comic_title, orientation="P", unit="mm", format="A4")

    # Optional: Title / Cover Card on First Page or Panel Pages
    for idx, panel in enumerate(layout, start=1):
        pdf.add_page()

        panel_num = panel.get("panel", panel.get("panel_number", idx))
        title_text = panel.get("title", f"Panel {panel_num}")
        image_path_str = panel.get("image_path", "")
        scene_desc = panel.get("scene_description", "")
        caption = panel.get("caption", "")
        narration = panel.get("narration", "")
        dialogue = panel.get("dialogue", "")
        raw_text = panel.get("text", "")

        # 1. Panel Header Badge & Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(20, 30, 50)
        safe_title = _sanitize_pdf_text(f"PANEL {panel_num}: {title_text}")
        pdf.cell(0, 10, safe_title, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # 2. Render Panel Illustration
        img_resolved_path = None
        if image_path_str:
            # Check relative to base dir or absolute
            candidate1 = Path(image_path_str)
            candidate2 = settings.BASE_DIR / image_path_str.lstrip("/\\")
            if candidate1.is_file():
                img_resolved_path = candidate1
            elif candidate2.is_file():
                img_resolved_path = candidate2

        # Page usable width is 190mm (210 - 20 margin)
        content_width = 190
        img_x = 10
        img_y = pdf.get_y()
        max_img_h = 105

        if img_resolved_path and img_resolved_path.exists():
            try:
                # Open with Pillow to get aspect ratio
                with Image.open(img_resolved_path) as pil_img:
                    orig_w, orig_h = pil_img.size
                aspect = orig_w / orig_h
                render_w = content_width
                render_h = render_w / aspect

                if render_h > max_img_h:
                    render_h = max_img_h
                    render_w = render_h * aspect

                # Center image horizontally
                centered_x = 10 + (content_width - render_w) / 2
                pdf.image(str(img_resolved_path), x=centered_x, y=img_y, w=render_w, h=render_h)
                pdf.set_y(img_y + render_h + 4)
            except Exception as img_err:
                logger.error("Could not embed image %s in PDF: %s", img_resolved_path, img_err)
                pdf.set_font("Helvetica", "I", 10)
                pdf.set_text_color(180, 50, 50)
                pdf.cell(0, 10, _sanitize_pdf_text(f"[Image placeholder: {title_text}]"), align="C", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 12, _sanitize_pdf_text(f"[Panel #{panel_num} Illustration: {title_text}]"), border=1, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

        # 3. Scene Description (Italics)
        if scene_desc:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(90, 100, 115)
            safe_desc = _sanitize_pdf_text(f"Scene: {scene_desc}")
            pdf.multi_cell(content_width, 6, safe_desc, align="L")
            pdf.ln(2)

        # 4. Ambient Caption Box
        if caption:
            pdf.set_fill_color(245, 245, 250)
            pdf.set_draw_color(200, 205, 220)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(60, 70, 90)
            safe_caption = _sanitize_pdf_text(f"CAPTION: {caption}")
            pdf.multi_cell(content_width, 6, safe_caption, border=1, fill=True, align="L")
            pdf.ln(2)

        # 5. Narration
        if narration and narration != caption:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 35, 45)
            # Remove redundant headers if already present in narration
            clean_narr = re.sub(r"^\*\*NARRATION[:\*]*\s*", "", narration, flags=re.IGNORECASE).strip()
            safe_narr = _sanitize_pdf_text(clean_narr)
            pdf.multi_cell(content_width, 6, safe_narr, align="L")
            pdf.ln(2)
        elif raw_text and not narration and not caption and not dialogue:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 35, 45)
            safe_raw = _sanitize_pdf_text(raw_text)
            pdf.multi_cell(content_width, 6, safe_raw, align="L")
            pdf.ln(2)

        # 6. Dialogue Bubble Box
        if dialogue:
            pdf.set_fill_color(255, 253, 235)
            pdf.set_draw_color(230, 200, 120)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(140, 90, 10)
            # Remove redundant prefix
            clean_dia = re.sub(r"^\*\*DIALOGUE[:\*]*\s*", "", dialogue, flags=re.IGNORECASE).strip()
            safe_dia = _sanitize_pdf_text(clean_dia)
            pdf.multi_cell(content_width, 6, safe_dia, border=1, fill=True, align="L")

    # Output to disk
    pdf.output(str(pdf_dest_path))
    logger.info("Successfully compiled comic PDF at: %s", pdf_dest_path)

    # Return web relative path
    web_pdf_path = f"static/exports/{filename}".replace("\\", "/")
    return web_pdf_path
