#!/usr/bin/env python3
"""
build_atlas_pdf.py — Generate The Maker Atlas PDF compendium.

Reads estates.json (sibling of this script) and produces The_Maker_Atlas.pdf.
Designed as a sibling reference instrument to The Vineyard Atlas, sharing
its typographic register (sans-serif body, wine-red accents, banded tables)
but adapted for estate-level (rather than vineyard-level) content, organised
by country and region.

Each region is presented in a two-tier hybrid format:
  1. A summary table at the top of the region — one row per estate, with
     columns Estate / Location / Principal grapes / Signature character.
     Mirrors the visual scan-table of the Vineyard Atlas.
  2. Below the summary, fuller prose entries for the same estates: founding
     date, signature wines (full list), descriptive paragraph, and any
     founding-date footnote.

Re-run on each refresh cycle. The PDF is a single artefact; all selection
logic, allocation, and editorial discipline are upstream in estates.json.

Usage:
    python3 build_atlas_pdf.py                     # writes The_Maker_Atlas.pdf
    python3 build_atlas_pdf.py --out path.pdf      # custom output path

Vinotheca · CC BY-NC 4.0
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Fonts — DejaVu Sans matches the Vineyard Atlas's sans-serif register and
# carries full Unicode coverage for diacritics in estate names (Méo-Camuzet,
# von Hövel, Trimbach, Quinta do Vesúvio, Simčič, Saša, etc.).
# ---------------------------------------------------------------------------

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

pdfmetrics.registerFont(TTFont("Atlas", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Atlas-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Atlas-Italic", str(FONT_DIR / "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("Atlas-BoldItalic", str(FONT_DIR / "DejaVuSans-BoldOblique.ttf")))
pdfmetrics.registerFontFamily(
    "Atlas",
    normal="Atlas",
    bold="Atlas-Bold",
    italic="Atlas-Italic",
    boldItalic="Atlas-BoldItalic",
)

# ---------------------------------------------------------------------------
# Palette — matches the Vineyard Atlas: wine-red accent on pure white.
# Wine-red is used for chapter titles, region headings, and table header
# bands. Body copy is near-black; secondary metadata is mid-grey.
# ---------------------------------------------------------------------------

WINE = colors.HexColor("#7a1e2d")        # accent — chapter titles, headings, table head
INK = colors.HexColor("#222222")         # body text
INK_SOFT = colors.HexColor("#5a5a5a")    # secondary text, captions
INK_FAINT = colors.HexColor("#888888")   # running header, page numbers
RULE = colors.HexColor("#cccccc")
RULE_SOFT = colors.HexColor("#dddddd")


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def build_styles() -> dict:
    s = getSampleStyleSheet()
    styles = {}

    styles["CoverTitle"] = ParagraphStyle(
        "CoverTitle", parent=s["Title"],
        fontName="Atlas-Bold", fontSize=28, leading=34,
        alignment=TA_CENTER, textColor=WINE, spaceAfter=14,
    )
    styles["CoverSubtitle"] = ParagraphStyle(
        "CoverSubtitle", parent=s["Normal"],
        fontName="Atlas", fontSize=12, leading=18,
        alignment=TA_CENTER, textColor=INK, spaceAfter=4,
    )
    styles["CoverSubtitleItalic"] = ParagraphStyle(
        "CoverSubtitleItalic", parent=s["Normal"],
        fontName="Atlas-Italic", fontSize=11, leading=16,
        alignment=TA_CENTER, textColor=INK_SOFT, spaceAfter=14,
    )
    styles["CoverMeta"] = ParagraphStyle(
        "CoverMeta", parent=s["Normal"],
        fontName="Atlas", fontSize=10, leading=14,
        alignment=TA_CENTER, textColor=INK_SOFT,
    )

    styles["ChapterTitle"] = ParagraphStyle(
        "ChapterTitle", parent=s["Heading1"],
        fontName="Atlas-Bold", fontSize=22, leading=28,
        alignment=TA_LEFT, textColor=WINE, spaceBefore=0, spaceAfter=10,
    )
    styles["RegionHeading"] = ParagraphStyle(
        "RegionHeading", parent=s["Heading2"],
        fontName="Atlas-Bold", fontSize=13, leading=18,
        alignment=TA_LEFT, textColor=WINE, spaceBefore=10, spaceAfter=6,
    )
    styles["SectionTitle"] = ParagraphStyle(
        "SectionTitle", parent=s["Heading1"],
        fontName="Atlas-Bold", fontSize=18, leading=24,
        alignment=TA_LEFT, textColor=WINE, spaceBefore=0, spaceAfter=12,
    )

    styles["Body"] = ParagraphStyle(
        "Body", parent=s["BodyText"],
        fontName="Atlas", fontSize=9.5, leading=13,
        alignment=TA_JUSTIFY, textColor=INK, spaceAfter=8,
    )
    styles["BodyLead"] = ParagraphStyle(
        "BodyLead", parent=s["BodyText"],
        fontName="Atlas", fontSize=9.5, leading=14,
        alignment=TA_JUSTIFY, textColor=INK, spaceAfter=10,
    )
    styles["BodySmall"] = ParagraphStyle(
        "BodySmall", parent=s["BodyText"],
        fontName="Atlas", fontSize=9, leading=12,
        alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6,
    )
    styles["Footnote"] = ParagraphStyle(
        "Footnote", parent=s["Normal"],
        fontName="Atlas-Italic", fontSize=8, leading=11,
        textColor=INK_SOFT, spaceAfter=6,
    )

    # Table cell styles — match Grand Cru's tight, scannable grid
    styles["TblHead"] = ParagraphStyle(
        "TblHead", fontName="Atlas-Bold", fontSize=8.5, leading=11,
        textColor=colors.white, alignment=TA_LEFT,
    )
    styles["TblName"] = ParagraphStyle(
        "TblName", fontName="Atlas-Bold", fontSize=8.5, leading=11,
        textColor=INK, alignment=TA_LEFT,
    )
    styles["TblBody"] = ParagraphStyle(
        "TblBody", fontName="Atlas", fontSize=8.5, leading=11,
        textColor=INK, alignment=TA_LEFT,
    )

    # Prose-entry styles — used in the "fuller entries" block per region
    styles["EntryName"] = ParagraphStyle(
        "EntryName", fontName="Atlas-Bold", fontSize=10.5, leading=14,
        textColor=INK, alignment=TA_LEFT, spaceAfter=2,
    )
    styles["EntryMeta"] = ParagraphStyle(
        "EntryMeta", fontName="Atlas-Italic", fontSize=8.5, leading=12,
        textColor=INK_SOFT, alignment=TA_LEFT, spaceAfter=4,
    )
    styles["EntryValue"] = ParagraphStyle(
        "EntryValue", fontName="Atlas", fontSize=8.5, leading=12,
        textColor=INK, alignment=TA_LEFT,
    )

    # TOC styles
    styles["TOCHeading"] = ParagraphStyle(
        "TOCHeading", parent=s["Heading1"],
        fontName="Atlas-Bold", fontSize=18, leading=24,
        alignment=TA_LEFT, textColor=WINE, spaceAfter=14,
    )
    styles["TOCCountry"] = ParagraphStyle(
        "TOCCountry", parent=s["Normal"],
        fontName="Atlas-Bold", fontSize=10.5, leading=15,
        alignment=TA_LEFT, textColor=INK, spaceBefore=6, spaceAfter=2,
    )
    styles["TOCRegion"] = ParagraphStyle(
        "TOCRegion", parent=s["Normal"],
        fontName="Atlas", fontSize=9.5, leading=13,
        alignment=TA_LEFT, textColor=INK_SOFT, leftIndent=14, spaceAfter=1,
    )

    return styles


# ---------------------------------------------------------------------------
# Page template — Grand Cru style: italic running header on left,
# horizontal rule below it, "Page N" centred at the foot.
# ---------------------------------------------------------------------------

PAGE_W, PAGE_H = A4
MARGIN_L = 2.0 * cm
MARGIN_R = 2.0 * cm
MARGIN_T = 2.4 * cm
MARGIN_B = 2.2 * cm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R  # ≈ 17 cm


class AtlasDocTemplate(BaseDocTemplate):
    """Cover page (no header/footer) followed by content pages with running
    header and centred page number. Header text is consistent across all
    body pages — chapters announce themselves via their large title.
    Mirrors the Vineyard Atlas's static-running-header convention."""

    HEADER_TEXT = "The Maker Atlas — World's Wine Estates by Country and Region"

    def __init__(self, filename, **kw):
        super().__init__(filename, pagesize=A4, **kw)

        cover_frame = Frame(
            MARGIN_L, MARGIN_B,
            CONTENT_W, PAGE_H - MARGIN_T - MARGIN_B,
            id="cover", showBoundary=0,
        )
        body_frame = Frame(
            MARGIN_L, MARGIN_B,
            CONTENT_W, PAGE_H - MARGIN_T - MARGIN_B,
            id="body", showBoundary=0,
        )

        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame], onPage=self._cover_page),
            PageTemplate(id="Body", frames=[body_frame], onPage=self._body_page),
        ])

    def _cover_page(self, canvas, doc):
        # Pure white background — no tint, no header, no folio.
        pass

    def _body_page(self, canvas, doc):
        canvas.saveState()

        # Running header (italic grey)
        canvas.setFont("Atlas-Italic", 9)
        canvas.setFillColor(INK_FAINT)
        header_y = PAGE_H - MARGIN_T + 0.7 * cm
        canvas.drawString(MARGIN_L, header_y, self.HEADER_TEXT)

        # Hairline rule below the header
        canvas.setStrokeColor(RULE_SOFT)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN_L, header_y - 5, PAGE_W - MARGIN_R, header_y - 5)

        # Footer: "Page N" centred
        canvas.setFont("Atlas", 9)
        canvas.setFillColor(INK_FAINT)
        canvas.drawCentredString(PAGE_W / 2.0, MARGIN_B - 0.9 * cm, f"Page {doc.page}")

        canvas.restoreState()


# ---------------------------------------------------------------------------
# Data plumbing
# ---------------------------------------------------------------------------

# Country ordering: anchor regions first (France, Italy, Germany, Spain,
# Portugal, Austria), then the rest of Europe, then the New World.
COUNTRY_ORDER = [
    "France", "Italy", "Germany", "Spain", "Portugal", "Austria",
    "Hungary", "Greece", "Slovenia", "Switzerland", "England",
    "Georgia", "Israel", "Lebanon",
    "United States", "Argentina", "Chile",
    "South Africa", "Australia", "New Zealand", "China",
]

ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII",
    9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV",
    16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX", 21: "XXI",
    22: "XXII", 23: "XXIII", 24: "XXIV", 25: "XXV", 26: "XXVI", 27: "XXVII",
    28: "XXVIII", 29: "XXIX", 30: "XXX",
}


def organise_estates(estates):
    """Group estates by country (canonical order), then by region (alphabetical
    within country). Returns [(country, [(region, [estates])])]."""
    by_country = defaultdict(lambda: defaultdict(list))
    for e in estates:
        by_country[e["country"]][e["region"]].append(e)

    seen = set()
    ordered_countries = []
    for c in COUNTRY_ORDER:
        if c in by_country:
            ordered_countries.append(c)
            seen.add(c)
    for c in sorted(by_country):
        if c not in seen:
            ordered_countries.append(c)

    out = []
    for c in ordered_countries:
        regions = by_country[c]
        ordered_regions = sorted(regions.keys())
        region_blocks = [
            (r, sorted(regions[r], key=lambda e: e["name"].lower()))
            for r in ordered_regions
        ]
        out.append((c, region_blocks))
    return out


# ---------------------------------------------------------------------------
# One-line "signature character" synthesis
# ---------------------------------------------------------------------------
# Condenses the existing `description` field into a single short phrase for
# the summary table. Never adds new factual claims — pure extraction. The
# full description below is the authoritative text.

EM_DASH = "—"
EN_DASH = "–"

# Patterns that mark a useful "topic sentence" — anchored to sentence starts.
# Bare word matches like \bcanonical\b are deliberately avoided because
# they fire anywhere and can promote a worse sentence (e.g. one describing
# founding history) over the actual topic sentence.
ESTATE_THESIS_PATTERNS = [
    re.compile(r"^The (?:canonical|reference|historical|defining|foundational|leading|principal|singular)\b", re.I),
    re.compile(r"^The [A-Za-z\-]+ (?:reference|estate|producer|anchor)\b", re.I),
    re.compile(r"^A (?:reference|canonical|leading|principal|defining|foundational|historical|major)\b", re.I),
    re.compile(r"^An (?:elite|established|important|emerging)\b", re.I),
    re.compile(r"^One of (?:the|Spain's|France's|Italy's|Germany's|Austria's)\b", re.I),
]


def _split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", text)
    return [p.strip() for p in parts if p.strip()]


def _looks_like_topic_sentence(sentence):
    """Heuristic: does this sentence read like an estate's thesis sentence
    (the kind that would belong in a summary table) rather than a
    founding-history detail or a concluding remark?"""
    return any(pat.search(sentence) for pat in ESTATE_THESIS_PATTERNS)


def signature_character(estate, max_chars=95):
    """Synthesize a one-line signature character for the summary table.
    Strategy:
      1. Always prefer the first sentence — descriptions in this atlas
         are written with a topic sentence first.
      2. Only override if the first sentence is too long to trim usefully
         AND a later sentence (within the first three) is a clear thesis.
      3. Trim to ≤ max_chars using clause boundaries.
    Output is plain text (no HTML), suitable for a table cell."""
    desc = (estate.get("description") or "").strip()
    if not desc:
        return ""

    sentences = _split_sentences(desc)
    if not sentences:
        return ""

    chosen = sentences[0]
    trimmed = _trim_to_first_clause(chosen, max_chars=max_chars)

    # If the first sentence trimmed cleanly to a short, sentence-like result,
    # we're done. Heuristic for "cleanly": the trimmed result is at most
    # max_chars and starts with a capital letter (always true here).
    if len(trimmed) <= max_chars and len(trimmed) >= 20:
        return trimmed

    # First sentence didn't trim well — see if any of the next two sentences
    # are obvious topic sentences.
    for s in sentences[1:3]:
        if _looks_like_topic_sentence(s):
            alt = _trim_to_first_clause(s, max_chars=max_chars)
            if 20 <= len(alt) <= max_chars:
                return alt

    return trimmed  # accept whatever the first-sentence trim produced


def _trim_to_first_clause(sentence, max_chars=95):
    sentence = sentence.rstrip(".!?")
    if len(sentence) <= max_chars:
        return sentence

    # Try em-dash break (parenthetical clarifications). Accept a head that
    # fits the budget; otherwise continue.
    for sep in [f" {EM_DASH} ", f" {EN_DASH} ", " - "]:
        if sep in sentence:
            head = sentence.split(sep, 1)[0].strip()
            if 20 <= len(head) <= max_chars:
                return head

    # Try comma break — pick the longest head that fits the budget.
    # NB: must enforce upper bound on the result. A 270-char "head" before
    # the first comma is not a valid summary.
    if "," in sentence:
        parts = sentence.split(",")
        # First, see if parts[0] alone is already over budget. If so, comma
        # break can't help us — fall through to word-truncate.
        if len(parts[0].strip()) <= max_chars:
            head = parts[0].strip()
            for i in range(1, len(parts)):
                candidate = ",".join(parts[: i + 1]).strip()
                if len(candidate) <= max_chars:
                    head = candidate
                else:
                    break
            if 20 <= len(head) <= max_chars:
                return head.strip()

    # Last resort: word-truncate to the budget, ending on a clean word.
    words = sentence.split()
    out, length = [], 0
    for w in words:
        # +1 for the joining space, but the first word adds no leading space
        addition = len(w) + (1 if out else 0)
        if length + addition > max_chars:
            break
        out.append(w)
        length += addition
    truncated = " ".join(out).rstrip(",;:")
    return truncated if truncated else sentence[:max_chars].rstrip()


def signature_character(estate, max_chars=95):
    desc = (estate.get("description") or "").strip()
    if not desc:
        return ""
    sentences = _split_sentences(desc)
    if not sentences:
        return ""

    chosen = sentences[0]
    trimmed = _trim_to_first_clause(chosen, max_chars=max_chars)
    if 20 <= len(trimmed) <= max_chars:
        return trimmed

    for s in sentences[1:3]:
        if _looks_like_topic_sentence(s):
            alt = _trim_to_first_clause(s, max_chars=max_chars)
            if 20 <= len(alt) <= max_chars:
                return alt
    return trimmed


def _strip_parentheticals(s):
    """Remove parenthetical clauses for compact display in the summary table.
    Some `sub_region` values in estates.json carry editorial prose inside
    parentheses (e.g. 'Ribeauvillé (in the central Alsace, the historical
    heart of fine-wine Alsace)') — useful for the prose entry but too long
    for a four-column table cell. Strip the parens and any leading/trailing
    whitespace and stray punctuation."""
    if not s:
        return s
    out = re.sub(r"\s*\([^()]*\)", "", s)
    out = re.sub(r"\s+", " ", out).strip(" ,;-")
    return out


def fmt_location_short(e):
    """Compact location for the summary table. Region is implied by the
    region heading directly above the table; we include sub-region and
    commune if they add information. Parenthetical clauses inside fields
    (some sub_region values carry editorial prose in parens) are stripped
    so the summary table stays scannable. The full prose entry below
    preserves the unabridged location string."""
    parts = []
    sub = _strip_parentheticals(e.get("sub_region"))
    region = e.get("region")
    commune = _strip_parentheticals(e.get("commune"))
    if sub and sub != region:
        parts.append(sub)
    if commune and commune != sub:
        parts.append(commune)
    if not parts and region:
        parts.append(region)
    return " · ".join(parts) if parts else "—"


def fmt_location_full(e):
    parts = []
    region = e.get("region")
    if region:
        parts.append(region)
    sub = e.get("sub_region")
    if sub and sub != region:
        parts.append(sub)
    commune = e.get("commune")
    if commune and commune not in (region, sub):
        parts.append(commune)
    location = " · ".join(parts) if parts else "—"
    appellation = e.get("appellation")
    if appellation and appellation not in (region, sub, commune):
        location = f"{location} ({appellation})"
    return location


def fmt_grapes_short(e, max_grapes=3):
    grapes = e.get("principal_grapes", []) or []
    if not grapes:
        return "—"
    if len(grapes) <= max_grapes:
        return ", ".join(grapes)
    head = ", ".join(grapes[:max_grapes])
    return f"{head} +{len(grapes) - max_grapes} more"


def fmt_grapes_full(e):
    grapes = e.get("principal_grapes", []) or []
    return ", ".join(grapes) if grapes else "—"


def fmt_founded(e):
    f = e.get("founded")
    return str(f) if f else "—"


def esc(s):
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


# ---------------------------------------------------------------------------
# Region rendering: summary table + prose entries
# ---------------------------------------------------------------------------

def region_summary_table(region_estates, styles):
    """Grand Cru-style 4-column summary table for a region.
    Columns: Estate | Location | Principal grapes | Signature character.
    Wine-red header band; bold name in left column; hairlines between rows."""

    head = [
        Paragraph("Estate", styles["TblHead"]),
        Paragraph("Location", styles["TblHead"]),
        Paragraph("Principal grapes", styles["TblHead"]),
        Paragraph("Signature character", styles["TblHead"]),
    ]
    rows = [head]
    for e in region_estates:
        rows.append([
            Paragraph(esc(e["name"]), styles["TblName"]),
            Paragraph(esc(fmt_location_short(e)), styles["TblBody"]),
            Paragraph(esc(fmt_grapes_short(e)), styles["TblBody"]),
            Paragraph(esc(signature_character(e)), styles["TblBody"]),
        ])

    # Column widths sum to CONTENT_W (≈17 cm)
    col_w = [4.4 * cm, 3.7 * cm, 3.4 * cm, 5.5 * cm]

    tbl = Table(rows, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header band — wine red with white text
        ("BACKGROUND", (0, 0), (-1, 0), WINE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        # Hairline rules between body rows
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE),
        # Outer border
        ("BOX", (0, 0), (-1, -1), 0.4, RULE),
    ]))
    return tbl


def estate_prose_entry(e, styles):
    """The full-prose tier for a single estate. Returns a list of flowables.
    The header strip (name + location + meta) is wrapped in KeepTogether so
    the metadata never strands at the bottom of a page above its name. The
    description is allowed to flow naturally if needed."""

    # Header row: name (bold, left) and location (italic grey, right)
    name_para = Paragraph(esc(e["name"]), styles["EntryName"])
    loc_para = Paragraph(esc(fmt_location_full(e)), styles["EntryMeta"])
    header_tbl = Table(
        [[name_para, loc_para]],
        colWidths=[10.5 * cm, 6.5 * cm],
    )
    header_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 0.4, RULE_SOFT),
    ]))

    # Compact meta strip — Founded · Principal grapes
    meta_text = (
        f"<b>Founded</b> &nbsp;{esc(fmt_founded(e))} "
        f"&nbsp;&nbsp;·&nbsp;&nbsp; "
        f"<b>Principal grapes</b> &nbsp;{esc(fmt_grapes_full(e))}"
    )
    meta_para = Paragraph(meta_text, styles["EntryValue"])

    # Signature wines block (full list — bullets)
    signatures = e.get("signature_wines", []) or []
    sig_para = None
    if signatures:
        sig_html = "<b>Signature wines</b><br/>" + "<br/>".join(
            f"&nbsp;&nbsp;• {esc(s)}" for s in signatures
        )
        sig_para = Paragraph(sig_html, styles["EntryValue"])

    # Full description paragraph
    desc = (e.get("description") or "").strip()
    desc_para = Paragraph(esc(desc), styles["BodySmall"]) if desc else None

    # Founded note (italic grey, small)
    fn = e.get("founded_note")
    fn_para = None
    if fn:
        fn_para = Paragraph(
            f"<i>Note on founding date.</i> {esc(fn)}",
            styles["Footnote"],
        )

    # Keep header + meta together; everything else may flow.
    card_top = KeepTogether([
        header_tbl,
        Spacer(1, 0.1 * cm),
        meta_para,
        Spacer(1, 0.15 * cm),
    ])

    out = [card_top]
    if sig_para is not None:
        out.append(sig_para)
        out.append(Spacer(1, 0.15 * cm))
    if desc_para is not None:
        out.append(desc_para)
    if fn_para is not None:
        out.append(fn_para)
    out.append(Spacer(1, 0.4 * cm))
    return out


def country_intro(country, n_estates, n_regions):
    region_word = "region" if n_regions == 1 else "regions"
    estate_word = "estate" if n_estates == 1 else "estates"
    return (
        f"This chapter covers <b>{n_estates} {estate_word}</b> across "
        f"<b>{n_regions} {region_word}</b> of {country}. Each region opens "
        f"with a summary table; fuller entries — founding date, signature "
        f"wines, and a descriptive paragraph drawn from the producers' own "
        f"published material and regulatory filings — follow below."
    )


# ---------------------------------------------------------------------------
# Document assembly
# ---------------------------------------------------------------------------

def build(estates_path, out_path):
    data = json.loads(estates_path.read_text(encoding="utf-8"))
    atlas = data["atlas"]
    estates = data["estates"]
    grouped = organise_estates(estates)

    styles = build_styles()
    doc = AtlasDocTemplate(
        str(out_path),
        title=atlas.get("title", "The Maker Atlas"),
        author="Vinotheca",
        subject="A curated reference of the world's wine estates",
        creator="Vinotheca · build_atlas_pdf.py",
    )

    story = []

    # ---- Cover page ---------------------------------------------------------
    # Mirrors Grand Cru: top-aligned, sparse. Keeps the informational tweaks
    # (estate count, edition, license) below the title block as agreed.
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("THE MAKER ATLAS", styles["CoverTitle"]))
    story.append(Paragraph(
        "A Compendium of the World's Wine Estates",
        styles["CoverSubtitle"],
    ))
    story.append(Paragraph(
        "Organised by Country and Region",
        styles["CoverSubtitleItalic"],
    ))
    story.append(Paragraph(
        atlas.get("edition", "1st edition (2026)"),
        styles["CoverMeta"],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"{atlas.get('current_count', len(estates))} estates · "
        f"{len({e['country'] for e in estates})} countries",
        styles["CoverMeta"],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Vinotheca · published under CC BY-NC 4.0",
        styles["CoverMeta"],
    ))

    # Switch to body template before the next page break, so the TOC inherits it.
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    # ---- Contents -----------------------------------------------------------
    story.append(Paragraph("Contents", styles["TOCHeading"]))
    story.append(Paragraph("<i>Introduction</i>", styles["TOCRegion"]))
    for idx, (country, region_blocks) in enumerate(grouped, start=1):
        roman = ROMAN.get(idx, str(idx))
        country_count = sum(len(rs) for _, rs in region_blocks)
        country_word = "estate" if country_count == 1 else "estates"
        story.append(Paragraph(
            f"{roman}. &nbsp;{esc(country)} "
            f"<font color='#888888'>· {country_count} {country_word}</font>",
            styles["TOCCountry"],
        ))
        for region, region_estates in region_blocks:
            story.append(Paragraph(
                f"{esc(region)} "
                f"<font color='#aaaaaa'>({len(region_estates)})</font>",
                styles["TOCRegion"],
            ))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "<i>Notes &amp; Editorial Principles</i>",
        styles["TOCCountry"],
    ))

    story.append(PageBreak())

    # ---- Introduction -------------------------------------------------------
    story.append(Paragraph("Introduction", styles["SectionTitle"]))

    n_total = len(estates)
    n_countries = len({e["country"] for e in estates})
    n_regions = len({(e["country"], e["region"]) for e in estates})

    intro_paragraphs = [
        (
            f"This volume is a curated reference to <b>{n_total}</b> wine estates "
            f"across <b>{n_countries}</b> countries and <b>{n_regions}</b> regions, "
            f"presented alongside a clickable companion map at the project's "
            f"web edition. Each region is shown in two tiers: a compact summary "
            f"table — estate, location, principal grapes, and a one-line "
            f"signature character — followed by fuller prose entries with "
            f"founding date, signature wines, and a descriptive paragraph drawn "
            f"from the producers' own published material and regulatory filings."
        ),
        (
            "The atlas is organised by country, then by region within each "
            "country. This follows the way the companion map's filters are "
            "structured and corresponds to how working wine references are "
            "most often consulted: a reader looking for estates in the Mosel "
            "or Stellenbosch can locate them under their country chapter "
            "without crossing thematic boundaries."
        ),
        (
            "Inclusion is based on durable recognition in publicly available "
            "sources, balanced to give coverage of the principal wine regions, "
            "grapes, and styles of established global viticulture. Selection "
            "is anchored in regional allocation — small, stylistically narrow "
            "regions receive a small number of representative estates; larger "
            "regions with greater internal diversity receive more, capped to "
            "preserve global legibility."
        ),
        (
            "<i>What this volume does not contain.</i> No ratings, tasting notes, "
            "scores, prices, or qualitative judgments. No references to named "
            "critics, proprietary scoring systems, or commercial certification "
            "frameworks. Estates appear because they illustrate their region "
            "or grape clearly, not because they are ranked above others. The "
            "atlas is a reference, not a ranking."
        ),
        (
            "<i>Geographic resolution.</i> The location given for each estate "
            "is its cellar or headquarters, not the vineyards from which it "
            "sources. For most estates these are nearly the same place; for "
            "négociants and producers sourcing broadly, the entry text "
            "clarifies the wider scope. Vineyard-level geography belongs to "
            "the sibling reference, <i>The Vineyard Atlas</i>."
        ),
        (
            "<i>Living document.</i> The atlas is refreshed on an annual cadence. "
            "The country and regional structure is the stable backbone; "
            "individual estate selections may be added or removed in scheduled "
            "refreshes documented in the version history. The web edition and "
            "this PDF companion are versioned together."
        ),
    ]
    for p in intro_paragraphs:
        story.append(Paragraph(p, styles["BodyLead"]))

    # ---- Country chapters ---------------------------------------------------
    for idx, (country, region_blocks) in enumerate(grouped, start=1):
        roman = ROMAN.get(idx, str(idx))
        n_country = sum(len(rs) for _, rs in region_blocks)
        n_region_count = len(region_blocks)

        # Always start each chapter on a fresh page
        story.append(PageBreak())
        story.append(Paragraph(
            f"{roman}. &nbsp;{esc(country)}",
            styles["ChapterTitle"],
        ))
        story.append(Paragraph(
            country_intro(country, n_country, n_region_count),
            styles["BodyLead"],
        ))

        for region, region_estates in region_blocks:
            # Region heading (wine-red, bold)
            story.append(Paragraph(esc(region), styles["RegionHeading"]))
            # Tier 1: summary table
            story.append(region_summary_table(region_estates, styles))
            story.append(Spacer(1, 0.5 * cm))
            # Tier 2: full prose entries for the same estates
            for e in region_estates:
                story.extend(estate_prose_entry(e, styles))

    # ---- Notes & editorial principles --------------------------------------
    story.append(PageBreak())
    story.append(Paragraph(
        "Notes &amp; Editorial Principles",
        styles["SectionTitle"],
    ))

    notes = [
        (
            "<b>Source material.</b> Estate descriptions, founding dates, "
            "principal grapes, and signature wines are drawn from the producers' "
            "own published material — estate websites, official press releases, "
            "and regulatory filings — and from the publicly available output of "
            "appellation and regulatory bodies. No commercial wine-platform "
            "data, critic notes, or proprietary databases have been ingested."
        ),
        (
            "<b>Editorial framing.</b> Descriptions are factual and neutral, "
            "written in the project's own language. No tasting notes, no "
            "vintage assessments, no qualitative ranking. Where a stylistic "
            "tendency is noted (for example, the use of botrytised fruit, "
            "biodynamic farming, or extended élevage), it is recorded because "
            "the estate itself describes its work in those terms, not as an "
            "evaluation."
        ),
        (
            "<b>Summary tables.</b> Each region opens with a four-column "
            "summary: estate, location, principal grapes, and a one-line "
            "signature character. The signature character is a condensed "
            "extract from the estate's own descriptive paragraph below; it "
            "introduces no new factual claims and serves as a navigational "
            "aid only. The full descriptive entry is the authoritative text."
        ),
        (
            "<b>Grape names.</b> Where a grape is known by different names in "
            "different traditions (Garnacha and Grenache; Syrah and Shiraz; "
            "Pinot Grigio and Pinot Gris), the atlas uses the form most "
            "commonly used in the country of the estate. A future edition will "
            "carry a global normalisation pass; the present edition preserves "
            "the local convention."
        ),
        (
            "<b>Coordinates.</b> Map coordinates correspond to the estate's "
            "cellar or headquarters location and are intended as guide points "
            "for the companion map. Where a sourcing region differs materially "
            "from the cellar location, the entry text clarifies."
        ),
        (
            "<b>Founding dates.</b> Where an estate's founding date is recorded "
            "as a single year, that year reflects the estate's establishment "
            "under its present name or by its present family. Where the "
            "underlying viticultural operation is older than the present "
            "estate, a brief note distinguishes the two."
        ),
        (
            "<b>License.</b> This atlas is published under a Creative Commons "
            "Attribution-NonCommercial 4.0 International licence (CC BY-NC 4.0). "
            "It may be redistributed and adapted for non-commercial use with "
            "attribution. The full licence text is at "
            "<i>creativecommons.org/licenses/by-nc/4.0</i>."
        ),
        (
            "<b>Sibling reference.</b> The Maker Atlas sits alongside <i>The "
            "Vineyard Atlas</i> within the Vinotheca library. Where the Vineyard "
            "Atlas maps the world's most revered <i>vineyard sites</i> to "
            "the grape varieties that have made them famous, the Maker Atlas "
            "maps the <i>producers</i> who farm and bottle wine across the "
            "world's principal regions. The two volumes are complementary, "
            "and several estates here are key producers of vineyards listed "
            "in the Vineyard Atlas."
        ),
        (
            f"<b>Version.</b> {esc(atlas.get('edition', '1st edition (2026)'))} · "
            f"version {esc(atlas.get('version', '1.0.0'))} · "
            f"last updated {esc(atlas.get('last_updated', ''))}."
        ),
    ]
    for note in notes:
        story.append(Paragraph(note, styles["Body"]))

    doc.build(story)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None):
    p = argparse.ArgumentParser(description="Build The Maker Atlas PDF.")
    here = Path(__file__).resolve().parent
    p.add_argument("--estates", default=str(here / "estates.json"),
                   help="Path to estates.json (default: alongside this script)")
    p.add_argument("--out", default=str(here / "The_Maker_Atlas.pdf"),
                   help="Output PDF path")
    args = p.parse_args(argv)

    estates_path = Path(args.estates)
    out_path = Path(args.out)
    if not estates_path.exists():
        print(f"error: estates file not found: {estates_path}", file=sys.stderr)
        return 1

    build(estates_path, out_path)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
