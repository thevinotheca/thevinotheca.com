#!/usr/bin/env python3
"""
build_atlas_pdf.py — Build The_Vineyard_Atlas.pdf from vineyards.json.

Pipeline:
- Reads vineyards.json (atlas metadata, introduction, chapters[], notes)
- Renders cover page, table of contents, chapter pages with intros + grouped
  site tables + footnotes, then the closing notes section
- Uses ReportLab + DejaVu Sans (system font at /usr/share/fonts/truetype/dejavu/)
- Wine-red accent (#7a1e2d), banded tables, ~46 pages expected output

This script is the canonical build for the Vineyard Atlas. To produce the PDF,
ensure vineyards.json is present in the same directory, then run:

    python3 build_atlas_pdf.py

Output: The_Vineyard_Atlas.pdf in the same directory.
"""

import json
import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import KeepTogether

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

HERE = Path(__file__).parent.resolve()
INPUT_JSON = HERE / "vineyards.json"
OUTPUT_PDF = HERE / "The_Vineyard_Atlas.pdf"

# Wine-red accent — matches the Maker Atlas family standard.
WINE_RED = colors.HexColor("#7a1e2d")
WINE_DARK = colors.HexColor("#5a1f1a")
INK = colors.HexColor("#1a1a1a")
INK_SOFT = colors.HexColor("#5a5048")
INK_MUTED = colors.HexColor("#8a7a6e")
BAND_LIGHT = colors.HexColor("#faf6f1")
BAND_ALT = colors.HexColor("#f3ede2")
RULE_LIGHT = colors.HexColor("#e8e2db")

# Page geometry
PAGE_W, PAGE_H = A4
MARGIN_L = 1.8 * cm
MARGIN_R = 1.8 * cm
MARGIN_T = 2.0 * cm
MARGIN_B = 2.0 * cm
HEADER_H = 0.9 * cm  # space for running header
FOOTER_H = 0.7 * cm  # space for page number

# ---------------------------------------------------------------------------
# FONTS — register DejaVu Sans family from system path
# ---------------------------------------------------------------------------

DEJAVU_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
FONT_ITALIC = "DejaVuSans-Oblique"
FONT_BOLD_ITALIC = "DejaVuSans-BoldOblique"


def register_fonts():
    """Register DejaVu Sans family. Required for diacritic-heavy wine text."""
    families = [
        (FONT_REGULAR, "DejaVuSans.ttf"),
        (FONT_BOLD, "DejaVuSans-Bold.ttf"),
        (FONT_ITALIC, "DejaVuSans-Oblique.ttf"),
        (FONT_BOLD_ITALIC, "DejaVuSans-BoldOblique.ttf"),
    ]
    for name, filename in families:
        path = os.path.join(DEJAVU_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Required font missing: {path}\n"
                f"Install with: sudo apt-get install fonts-dejavu"
            )
        pdfmetrics.registerFont(TTFont(name, path))


# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------


def make_styles():
    """Return a dict of all paragraph styles used in the document."""
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName=FONT_BOLD,
            fontSize=32,
            leading=38,
            alignment=1,  # centre
            textColor=WINE_RED,
            spaceAfter=8,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            fontName=FONT_ITALIC,
            fontSize=15,
            leading=20,
            alignment=1,
            textColor=INK_SOFT,
            spaceAfter=24,
        ),
        "cover_principle": ParagraphStyle(
            "cover_principle",
            fontName=FONT_REGULAR,
            fontSize=12,
            leading=16,
            alignment=1,
            textColor=INK_MUTED,
            spaceAfter=4,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            fontName=FONT_REGULAR,
            fontSize=10,
            leading=14,
            alignment=1,
            textColor=INK_MUTED,
            spaceAfter=2,
        ),
        "h_section": ParagraphStyle(
            "h_section",
            fontName=FONT_BOLD,
            fontSize=22,
            leading=28,
            alignment=0,
            textColor=WINE_RED,
            spaceBefore=4,
            spaceAfter=12,
        ),
        "h_intro_body": ParagraphStyle(
            "h_intro_body",
            fontName=FONT_REGULAR,
            fontSize=10.5,
            leading=15,
            alignment=4,  # justify
            textColor=INK,
            spaceAfter=12,
        ),
        "h_group": ParagraphStyle(
            "h_group",
            fontName=FONT_BOLD,
            fontSize=13,
            leading=17,
            textColor=WINE_DARK,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "toc_chapter": ParagraphStyle(
            "toc_chapter",
            fontName=FONT_BOLD,
            fontSize=11,
            leading=15,
            textColor=WINE_RED,
            spaceBefore=4,
            spaceAfter=1,
        ),
        "toc_group": ParagraphStyle(
            "toc_group",
            fontName=FONT_REGULAR,
            fontSize=10,
            leading=14,
            leftIndent=14,
            textColor=INK_SOFT,
            spaceAfter=0,
        ),
        "footnote": ParagraphStyle(
            "footnote",
            fontName=FONT_ITALIC,
            fontSize=9,
            leading=12,
            alignment=4,
            textColor=INK_MUTED,
            leftIndent=6,
            rightIndent=6,
            spaceBefore=8,
            spaceAfter=4,
            borderColor=RULE_LIGHT,
            borderWidth=0,
            borderPadding=4,
        ),
        "notes_h": ParagraphStyle(
            "notes_h",
            fontName=FONT_BOLD,
            fontSize=18,
            leading=24,
            textColor=WINE_RED,
            spaceAfter=10,
        ),
        "notes_body": ParagraphStyle(
            "notes_body",
            fontName=FONT_REGULAR,
            fontSize=10.5,
            leading=15,
            alignment=4,
            textColor=INK,
            spaceAfter=10,
        ),
        # Cell styles for the per-site table
        "cell_site": ParagraphStyle(
            "cell_site",
            fontName=FONT_BOLD,
            fontSize=9,
            leading=11,
            textColor=INK,
        ),
        "cell_terroir": ParagraphStyle(
            "cell_terroir",
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=10.5,
            textColor=INK_SOFT,
        ),
        "cell_producers": ParagraphStyle(
            "cell_producers",
            fontName=FONT_ITALIC,
            fontSize=8.5,
            leading=10.5,
            textColor=INK,
        ),
        "cell_character": ParagraphStyle(
            "cell_character",
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=10.5,
            textColor=INK,
        ),
        "cell_header": ParagraphStyle(
            "cell_header",
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
            alignment=0,
        ),
    }


# ---------------------------------------------------------------------------
# PAGE TEMPLATES
# ---------------------------------------------------------------------------


def draw_cover_page(canvas, doc):
    """No header/footer on the cover."""
    pass


def draw_content_page(canvas, doc):
    """Running header and page number on all non-cover pages."""
    canvas.saveState()
    # Header text — running title at top, wine-red rule below
    canvas.setFont(FONT_ITALIC, 8.5)
    canvas.setFillColor(INK_MUTED)
    canvas.drawString(
        MARGIN_L,
        PAGE_H - MARGIN_T + 0.45 * cm,
        "The Vineyard Atlas — World's Greatest Vineyards by Grape Variety",
    )
    canvas.setStrokeColor(WINE_RED)
    canvas.setLineWidth(0.4)
    canvas.line(
        MARGIN_L,
        PAGE_H - MARGIN_T + 0.25 * cm,
        PAGE_W - MARGIN_R,
        PAGE_H - MARGIN_T + 0.25 * cm,
    )

    # Page number bottom-right; "Page N" matches the source PDF convention
    canvas.setFont(FONT_REGULAR, 8.5)
    canvas.setFillColor(INK_MUTED)
    canvas.drawRightString(
        PAGE_W - MARGIN_R,
        MARGIN_B - 0.55 * cm,
        f"Page {doc.page}",
    )
    canvas.restoreState()


# ---------------------------------------------------------------------------
# DOCUMENT BUILDER
# ---------------------------------------------------------------------------


def site_table(sites, styles, available_w):
    """
    Build a four-column ReportLab Table for a list of sites.
    Columns: Vineyard / Site | Region & Terroir | Key Producers | Signature Character
    Banded backgrounds alternate light/raised paper. Wine-red header row.
    """
    # Column widths — total must equal available_w
    # Tuned for readability: site (24%), terroir (24%), producers (22%), character (30%)
    col_w = [
        available_w * 0.24,
        available_w * 0.24,
        available_w * 0.22,
        available_w * 0.30,
    ]

    header_cells = [
        Paragraph("Vineyard / Site", styles["cell_header"]),
        Paragraph("Region &amp; Terroir", styles["cell_header"]),
        Paragraph("Key Producers", styles["cell_header"]),
        Paragraph("Signature Character", styles["cell_header"]),
    ]

    data = [header_cells]
    for s in sites:
        producers_str = ", ".join(s["key_producers"])
        # Escape ampersands for ReportLab's mini-XML parser
        data.append(
            [
                Paragraph(_xml_escape(s["vineyard_site"]), styles["cell_site"]),
                Paragraph(_xml_escape(s["region_terroir"]), styles["cell_terroir"]),
                Paragraph(_xml_escape(producers_str), styles["cell_producers"]),
                Paragraph(
                    _xml_escape(s["signature_character"]), styles["cell_character"]
                ),
            ]
        )

    tbl = Table(data, colWidths=col_w, repeatRows=1)

    # Style: wine-red header, banded body, light grid
    base_style = [
        ("BACKGROUND", (0, 0), (-1, 0), WINE_RED),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.25, RULE_LIGHT),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, WINE_DARK),
    ]
    # Alternate row banding (skip header row)
    for i in range(1, len(data)):
        if i % 2 == 0:
            base_style.append(("BACKGROUND", (0, i), (-1, i), BAND_LIGHT))
        else:
            base_style.append(("BACKGROUND", (0, i), (-1, i), colors.white))

    tbl.setStyle(TableStyle(base_style))
    return tbl


def _xml_escape(s):
    """Escape special characters for ReportLab's mini-XML parser in Paragraph."""
    if s is None:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _para_escape(s):
    """Escape & preserve paragraph breaks for body prose."""
    return _xml_escape(s).replace("\n\n", "<br/><br/>").replace("\n", "<br/>")


def build_story(data, styles):
    """Construct the full list of flowables for the document."""
    story = []
    available_w = PAGE_W - MARGIN_L - MARGIN_R

    # ----- COVER PAGE -----
    atlas = data["atlas"]
    story.append(Spacer(1, 5 * cm))
    story.append(Paragraph(atlas["title"].upper(), styles["cover_title"]))
    story.append(Paragraph(atlas["subtitle"], styles["cover_subtitle"]))
    story.append(Paragraph(atlas["organising_principle"], styles["cover_principle"]))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(f"{atlas['edition']}", styles["cover_meta"]))
    story.append(
        Paragraph(
            f"{atlas['current_count']} vineyard sites · "
            f"{atlas['current_chapters']} chapters",
            styles["cover_meta"],
        )
    )
    story.append(Paragraph(atlas["license"], styles["cover_meta"]))
    story.append(PageBreak())

    # ----- TABLE OF CONTENTS -----
    story.append(Paragraph("Contents", styles["h_section"]))
    story.append(Paragraph("Introduction", styles["toc_chapter"]))
    for ch in data["chapters"]:
        story.append(
            Paragraph(
                f"{ch['roman']}. {_xml_escape(ch['title'])}", styles["toc_chapter"]
            )
        )
        for g in ch["groups"]:
            story.append(
                Paragraph(_xml_escape(g["name"]), styles["toc_group"])
            )
    story.append(Paragraph("Notes", styles["toc_chapter"]))
    story.append(PageBreak())

    # ----- INTRODUCTION -----
    story.append(Paragraph("Introduction", styles["h_section"]))
    story.append(Paragraph(_para_escape(data["introduction"]), styles["h_intro_body"]))
    story.append(PageBreak())

    # ----- CHAPTERS -----
    for ch in data["chapters"]:
        # Chapter header
        story.append(
            Paragraph(
                f"{ch['roman']}. {_xml_escape(ch['title'])}", styles["h_section"]
            )
        )
        # Chapter intro paragraph
        if ch.get("intro"):
            story.append(
                Paragraph(_para_escape(ch["intro"]), styles["h_intro_body"])
            )

        # Each group: sub-header + table of its sites
        for g in ch["groups"]:
            story.append(Paragraph(_xml_escape(g["name"]), styles["h_group"]))
            story.append(site_table(g["sites"], styles, available_w))

        # Optional footnote at end of chapter
        if ch.get("footnote"):
            story.append(
                Paragraph(
                    f"<i>Note: {_xml_escape(ch['footnote'])}</i>",
                    styles["footnote"],
                )
            )

        story.append(PageBreak())

    # ----- CLOSING NOTES SECTION -----
    story.append(Paragraph("Notes", styles["notes_h"]))
    story.append(Paragraph(_para_escape(data["notes"]), styles["notes_body"]))

    return story


def build_pdf():
    """Top-level build: load data, register fonts, build PDF."""
    if not INPUT_JSON.exists():
        print(f"ERROR: {INPUT_JSON} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {INPUT_JSON.name}...")
    with open(INPUT_JSON) as f:
        data = json.load(f)

    n_chapters = len(data["chapters"])
    n_sites = sum(
        sum(len(g["sites"]) for g in ch["groups"]) for ch in data["chapters"]
    )
    print(f"  {n_chapters} chapters, {n_sites} sites")

    register_fonts()
    styles = make_styles()

    doc = BaseDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=MARGIN_T,
        bottomMargin=MARGIN_B,
        title=data["atlas"]["title"],
        author="Jure Skarabot",
        subject=data["atlas"]["subtitle"],
    )

    # Two page templates: bare cover, then content with header/footer.
    cover_frame = Frame(
        MARGIN_L,
        MARGIN_B,
        PAGE_W - MARGIN_L - MARGIN_R,
        PAGE_H - MARGIN_T - MARGIN_B,
        id="cover_frame",
    )
    content_frame = Frame(
        MARGIN_L,
        MARGIN_B,
        PAGE_W - MARGIN_L - MARGIN_R,
        PAGE_H - MARGIN_T - MARGIN_B,
        id="content_frame",
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="Cover", frames=cover_frame, onPage=draw_cover_page),
            PageTemplate(
                id="Content", frames=content_frame, onPage=draw_content_page
            ),
        ]
    )

    story = build_story(data, styles)
    # After cover, switch to Content template
    story.insert(1, _NextPageTemplate("Content"))

    print(f"Building {OUTPUT_PDF.name}...")
    doc.build(story)

    size = OUTPUT_PDF.stat().st_size
    print(f"  Wrote {OUTPUT_PDF.name}: {size:,} bytes ({size / 1024:.1f} KB)")


def _NextPageTemplate(template_id):
    """Tiny shim — return a NextPageTemplate flowable without import cluttering top."""
    from reportlab.platypus import NextPageTemplate

    return NextPageTemplate(template_id)


if __name__ == "__main__":
    build_pdf()
