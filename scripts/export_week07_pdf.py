"""Export the Week 07 Markdown report to a readable PDF using ReportLab."""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "T03_Milestone3_Knowledge_Base_Vector_Search.md"
OUTPUT = ROOT / "docs" / "Laporan_W07_Basis_Pengetahuan_Vector_Search.pdf"


def register_fonts() -> str:
    fonts = Path("C:/Windows/Fonts")
    regular = fonts / "arial.ttf"
    bold = fonts / "arialbd.ttf"
    italic = fonts / "ariali.ttf"
    if regular.exists() and bold.exists() and italic.exists():
        pdfmetrics.registerFont(TTFont("ReportArial", str(regular)))
        pdfmetrics.registerFont(TTFont("ReportArial-Bold", str(bold)))
        pdfmetrics.registerFont(TTFont("ReportArial-Italic", str(italic)))
        pdfmetrics.registerFontFamily(
            "ReportArial", normal="ReportArial", bold="ReportArial-Bold",
            italic="ReportArial-Italic", boldItalic="ReportArial-Bold",
        )
        return "ReportArial"
    return "Helvetica"


FONT = register_fonts()


def inline_markup(value: str) -> str:
    value = escape(value.strip())
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#1769aa">\1</link>', value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
    value = re.sub(r"\\([%$#&_{}])", r"\1", value)
    return value


class PipelineDiagram(Flowable):
    """Draw the ingestion and query stages as a compact vector diagram."""

    def __init__(self):
        super().__init__()
        self.width = 168 * mm
        self.height = 61 * mm

    def draw(self):
        c = self.canv
        labels = [
            "Dokumen\nMD / TXT / PDF", "Loader &\nCleaner", "Chunker\n150 / 30",
            "Embedding\nMiniLM L12", "ChromaDB\nCosine HNSW", "Retriever +\nGuardrail",
        ]
        box_w, box_h, gap = 25 * mm, 17 * mm, 2.7 * mm
        x0, y = 1 * mm, 37 * mm
        for i, label in enumerate(labels):
            x = x0 + i * (box_w + gap)
            c.setFillColor(colors.HexColor("#EAF2F8" if i < 5 else "#E8F5E9"))
            c.setStrokeColor(colors.HexColor("#315B7D"))
            c.roundRect(x, y, box_w, box_h, 2 * mm, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#17324D"))
            c.setFont(FONT, 7.2)
            for j, line in enumerate(label.split("\n")):
                c.drawCentredString(x + box_w / 2, y + box_h / 2 + (3 - j * 8) * mm, line)
            if i < len(labels) - 1:
                c.setStrokeColor(colors.HexColor("#526777"))
                sx = x + box_w
                ex = sx + gap - 0.5 * mm
                cy = y + box_h / 2
                c.line(sx, cy, ex, cy)
                c.line(ex - 1.3 * mm, cy + 1 * mm, ex, cy)
                c.line(ex - 1.3 * mm, cy - 1 * mm, ex, cy)
        c.setFont(FONT, 7)
        c.setFillColor(colors.HexColor("#425466"))
        c.drawString(2 * mm, 26 * mm, "Ingestion: dokumen dibersihkan, dipotong, di-embedding, lalu diindeks secara persisten.")
        c.drawString(2 * mm, 17 * mm, "Runtime: kueri dicari berdasarkan cosine similarity; hasil di bawah threshold ditolak tanpa chunk.")
        c.setStrokeColor(colors.HexColor("#88A"))
        c.line(2 * mm, 13 * mm, 160 * mm, 13 * mm)
        c.setFillColor(colors.HexColor("#17324D"))
        c.drawString(2 * mm, 7 * mm, "Lolos → kandidat Top-k + sitasi")
        c.drawString(87 * mm, 7 * mm, "Ditolak → fallback santun / zero leakage")


def styles_for(font: str):
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("ReportH1", parent=base["Heading1"], fontName=font + "-Bold" if font != "Helvetica" else "Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#123B5D"), spaceBefore=14, spaceAfter=8, keepWithNext=True),
        "h2": ParagraphStyle("ReportH2", parent=base["Heading2"], fontName=font + "-Bold" if font != "Helvetica" else "Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#205A7A"), spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "h3": ParagraphStyle("ReportH3", parent=base["Heading3"], fontName=font + "-Bold" if font != "Helvetica" else "Helvetica-Bold", fontSize=10.2, leading=13, textColor=colors.HexColor("#2D4A5D"), spaceBefore=8, spaceAfter=4, keepWithNext=True),
        "body": ParagraphStyle("ReportBody", parent=base["BodyText"], fontName=font, fontSize=9, leading=13, alignment=TA_JUSTIFY, spaceAfter=6, splitLongWords=1),
        "small": ParagraphStyle("ReportSmall", parent=base["BodyText"], fontName=font, fontSize=7.3, leading=9.5, alignment=TA_LEFT, spaceAfter=2, splitLongWords=1),
        "center": ParagraphStyle("ReportCenter", parent=base["BodyText"], fontName=font, fontSize=10, leading=15, alignment=TA_CENTER, spaceAfter=6),
        "quote": ParagraphStyle("ReportQuote", parent=base["BodyText"], fontName=font, fontSize=8.5, leading=12, leftIndent=12, rightIndent=8, borderColor=colors.HexColor("#A7C5D8"), borderWidth=1, borderPadding=6, backColor=colors.HexColor("#F3F8FB"), spaceBefore=4, spaceAfter=8),
        "code": ParagraphStyle("ReportCode", parent=base["Code"], fontName="Courier", fontSize=7.2, leading=9, backColor=colors.HexColor("#F2F4F7"), borderPadding=5, spaceBefore=3, spaceAfter=6),
    }


def make_table(lines: list[str], styles):
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells):
            continue
        rows.append([Paragraph(inline_markup(c), styles["small"]) for c in cells])
    if not rows:
        return None
    count = max(map(len, rows))
    for row in rows:
        row.extend([Paragraph("", styles["small"])] * (count - len(row)))
    available = 168 * mm
    widths = [available / count] * count
    if count == 2:
        widths = [available * 0.34, available * 0.66]
    elif count == 3:
        widths = [available * 0.26, available * 0.28, available * 0.46]
    elif count >= 6:
        widths = [available / count] * count
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEAF3")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#123B5D")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#AAB8C2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    return table


def draw_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(colors.HexColor("#CCD6DE"))
    canvas.line(20 * mm, h - 15 * mm, w - 20 * mm, h - 15 * mm)
    canvas.setFont(FONT, 7.5)
    canvas.setFillColor(colors.HexColor("#526777"))
    canvas.drawString(20 * mm, h - 11.5 * mm, "10S3001 Kecerdasan Buatan (+P) | Tugas 3 (W07) | Institut Teknologi Del")
    canvas.line(20 * mm, 14 * mm, w - 20 * mm, 14 * mm)
    canvas.drawString(20 * mm, 9 * mm, "Del-Academic Navigator")
    canvas.drawRightString(w - 20 * mm, 9 * mm, f"Halaman {doc.page}")
    canvas.restoreState()


def build():
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=21 * mm, leftMargin=21 * mm,
        topMargin=21 * mm, bottomMargin=20 * mm,
        title="Pembangunan Basis Pengetahuan Korpus & Vector Semantic Search",
        author="Tim Del-Academic Navigator",
    )
    styles = styles_for(FONT)
    text = SOURCE.read_text(encoding="utf-8").splitlines()
    story = []
    i = 0
    code_mode = False
    code_lines: list[str] = []
    while i < len(text):
        line = text[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            if not code_mode:
                code_mode = True
                code_lines = []
            else:
                code_mode = False
                if code_lines and code_lines[0].strip().lower() == "mermaid":
                    story.append(PipelineDiagram())
                else:
                    story.append(Preformatted("\n".join(code_lines), styles["code"], maxLineLength=105))
                story.append(Spacer(1, 3))
            i += 1
            continue
        if code_mode:
            code_lines.append(line)
            i += 1
            continue
        if stripped in ("<div align=\"center\">", "</div>", "---"):
            if stripped == "---":
                story.append(Spacer(1, 4))
            i += 1
            continue
        if not stripped:
            i += 1
            continue
        if stripped.startswith("|"):
            if stripped.startswith("| Identitas Modul |"):
                story.append(PageBreak())
            table_lines = []
            while i < len(text) and text[i].strip().startswith("|"):
                table_lines.append(text[i])
                i += 1
            table = make_table(table_lines, styles)
            if table:
                story.append(table)
                story.append(Spacer(1, 6))
            continue
        if stripped.startswith("!["):
            match = re.search(r"\]\(([^)]+)\)", stripped)
            if match:
                path = ROOT / match.group(1)
                if path.exists():
                    image = Image(str(path))
                    max_w, max_h = 165 * mm, 105 * mm
                    ratio = min(max_w / image.imageWidth, max_h / image.imageHeight, 1)
                    image.drawWidth = image.imageWidth * ratio
                    image.drawHeight = image.imageHeight * ratio
                    story.append(image)
                    story.append(Spacer(1, 6))
            i += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading:
            level, title = len(heading.group(1)), heading.group(2)
            if title.startswith("PEMBANGUNAN BASIS PENGETAHUAN"):
                story.append(Spacer(1, 14 * mm))
                story.append(Paragraph(inline_markup(title), ParagraphStyle("CoverTitle", parent=styles["h1"], alignment=TA_CENTER, fontSize=20, leading=26, spaceAfter=14)))
                story.append(Spacer(1, 7 * mm))
            else:
                style = styles[{1: "h1", 2: "h2", 3: "h3"}[level]]
                story.append(Paragraph(inline_markup(title), style))
            i += 1
            continue
        if stripped.startswith(">"):
            quote_lines = []
            while i < len(text) and text[i].strip().startswith(">"):
                quote_lines.append(text[i].strip()[1:].strip())
                i += 1
            story.append(Paragraph(inline_markup(" ".join(quote_lines)), styles["quote"]))
            continue
        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            item = re.sub(r"^(?:[-*]|\d+\.)\s+", "", stripped)
            story.append(Paragraph("• " + inline_markup(item), styles["body"]))
            i += 1
            continue
        if stripped.startswith("<br"):
            story.append(Spacer(1, 4))
            i += 1
            continue
        para_lines = [stripped]
        i += 1
        while i < len(text):
            nxt = text[i].strip()
            if (not nxt or nxt.startswith(("#", "|", ">", "![", "```", "---"))
                    or re.match(r"^[-*]\s+|^\d+\.\s+", nxt)
                    or nxt.startswith("<div") or nxt == "</div>"):
                break
            para_lines.append(nxt)
            i += 1
        para = " ".join(para_lines)
        if "**Disusun untuk memenuhi" in para or para.startswith("**Dosen Pengampu") or para.startswith("Samuel Indra") or para.startswith("**Disusun oleh"):
            story.append(Paragraph(inline_markup(para), styles["center"]))
        else:
            story.append(Paragraph(inline_markup(para), styles["body"]))
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
