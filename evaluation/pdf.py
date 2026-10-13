"""Dokument wynikowy (PDF) z wypełnionego arkusza — ReportLab, czysty
Python, bez bibliotek systemowych, więc działa również na mydevil.

To nie jest kopia formularza, tylko arkusz oceny: dane obserwacji, tabela
wyników z komentarzami, podsumowanie i ocena opisowa.

`build_pdf(cleaned_data) -> bytes` nie zależy od requestu, więc ten sam
wynik można wysłać jako załącznik e-mail.
"""

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.utils import timezone
from django.utils.text import slugify

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from . import sheet

FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONT = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"

NAVY = colors.HexColor("#0B1822")
INK_SOFT = colors.HexColor("#566070")
SOFT = colors.HexColor("#F1F4F7")
LINE = colors.HexColor("#C9D1DA")
GOLD = colors.HexColor("#E8A832")
GREEN = colors.HexColor("#5C9A30")
BLUE = colors.HexColor("#2FA6E0")

# Tło komórki z oceną: powyżej / na poziomie / poniżej poziomu wyjściowego.
GRADE_BG = {
    "A": colors.HexColor("#DCEDCF"), "B": colors.HexColor("#DCEDCF"),
    "C": SOFT,
    "D": colors.HexColor("#F8DEDE"), "E": colors.HexColor("#F8DEDE"),
    "F": colors.HexColor("#F8DEDE"),
}

_fonts_registered = False


def _register_fonts():
    # Wbudowane fonty PDF (Helvetica) nie mają polskich znaków.
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont(FONT, FONT_DIR / "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, FONT_DIR / "DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFontFamily(FONT, normal=FONT, bold=FONT_BOLD)
    _fonts_registered = True


def _styles():
    base = ParagraphStyle("base", fontName=FONT, fontSize=9, leading=12)
    return {
        "base": base,
        "small": ParagraphStyle("small", parent=base, fontSize=8, leading=10.5, textColor=INK_SOFT),
        "label": ParagraphStyle("label", parent=base, fontSize=8.5, textColor=INK_SOFT),
        "bold": ParagraphStyle("bold", parent=base, fontName=FONT_BOLD),
        "th": ParagraphStyle("th", parent=base, fontName=FONT_BOLD, fontSize=8.5, textColor=colors.white),
        "brand": ParagraphStyle(
            "brand", parent=base, fontName=FONT_BOLD, fontSize=8.5, textColor=NAVY,
        ),
        "brand_r": ParagraphStyle(
            "brand_r", parent=base, fontSize=8.5, textColor=INK_SOFT, alignment=TA_RIGHT,
        ),
        "title": ParagraphStyle(
            "title", parent=base, fontName=FONT_BOLD, fontSize=17, leading=21,
            textColor=NAVY, spaceBefore=9, spaceAfter=0,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base, fontName=FONT_BOLD, fontSize=11.5, leading=15,
            textColor=NAVY, spaceBefore=9, spaceAfter=4,
        ),
        "grade": ParagraphStyle(
            "grade", parent=base, fontName=FONT_BOLD, fontSize=14, leading=16, alignment=TA_CENTER,
        ),
        "grade_label": ParagraphStyle(
            "grade_label", parent=base, fontSize=7, leading=8.5, alignment=TA_CENTER, textColor=INK_SOFT,
        ),
    }


def _text(text) -> str:
    """Tekst użytkownika do Paragraph — escapujemy, zachowujemy nowe linie."""
    return escape(str(text or "")).replace("\n", "<br/>")


def _stripe(width):
    """Trójkolorowy pasek z identyfikacji Wydziału."""
    t = Table([["", "", ""]], colWidths=[width / 3] * 3, rowHeights=[2.2])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), GOLD),
        ("BACKGROUND", (1, 0), (1, 0), GREEN),
        ("BACKGROUND", (2, 0), (2, 0), BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def _letterhead(st, width, generated):
    t = Table(
        [[Paragraph("WYDZIAŁ SĘDZIOWSKI<br/>ŚLĄSKIEGO ZWIĄZKU PIŁKI SIATKOWEJ", st["brand"]),
          Paragraph(f"Data sporządzenia: {generated:%d.%m.%Y}", st["brand_r"])]],
        colWidths=[width * 0.6, width * 0.4],
    )
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [t, _stripe(width)]


def _details(data, st, width):
    """Sekcja 1: dane obserwacji jako dwie kolumny etykieta → wartość."""
    date = data.get("match_date")
    pairs = [
        ("Oceniany sędzia", f"<b>{_text(data.get('referee_name'))}</b>"),
        ("Pozycja", sheet.choice_label(sheet.POSITIONS, data.get("position"))),
        ("Rozgrywki", sheet.choice_label(sheet.COMPETITIONS, data.get("competition"))),
        ("Trudność meczu", sheet.choice_label(sheet.DIFFICULTY, data.get("difficulty"))),
        ("Mecz", _text(data.get("teams"))),
        ("Data meczu", date.strftime("%d.%m.%Y") if date else "—"),
        ("Wynik", _text(data.get("result"))),
        ("Obserwator", _text(data.get("observer"))),
    ]
    rows = []
    for i in range(0, len(pairs), 2):
        row = []
        for label, value in pairs[i:i + 2]:
            row += [Paragraph(label, st["label"]), Paragraph(value or "—", st["base"])]
        rows.append(row)
    lw = 30 * mm
    vw = width / 2 - lw
    t = Table(rows, colWidths=[lw, vw, lw, vw])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# Wiersz tabeli nie może być wyższy niż strona (ReportLab rzuca wtedy
# LayoutError), więc dłuższe komentarze idą do sekcji pod tabelą.
INLINE_COMMENT_MAX = 500


def _long_comments(data):
    """[(lp, element, komentarz)] dla komentarzy za długich do tabeli."""
    return [
        (i, label, data.get(sheet.comment_field(key)))
        for i, (key, label, _info) in enumerate(sheet.ELEMENTS, start=1)
        if len(data.get(sheet.comment_field(key)) or "") > INLINE_COMMENT_MAX
    ]


def _results(data, st, width):
    """Sekcja 2: Lp. | element | ocena | komentarz obserwatora."""
    rows = [[
        Paragraph("Lp.", st["th"]),
        Paragraph("Element oceny", st["th"]),
        Paragraph("Ocena", st["th"]),
        Paragraph("Komentarz obserwatora", st["th"]),
    ]]
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (2, 0), "CENTER"),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i, (key, label, _info) in enumerate(sheet.ELEMENTS, start=1):
        grade = data.get(sheet.grade_field(key), "")
        comment = data.get(sheet.comment_field(key))
        rows.append([
            Paragraph(str(i), st["base"]),
            Paragraph(escape(label), st["bold"]),
            [Paragraph(grade, st["grade"]),
             Paragraph(sheet.GRADE_LABELS.get(grade, ""), st["grade_label"])],
            _comment_cell(comment, i, st),
        ])
        style.append(("BACKGROUND", (2, i), (2, i), GRADE_BG.get(grade, SOFT)))
    t = Table(
        rows,
        colWidths=[11 * mm, 68 * mm, 23 * mm, width - 102 * mm],
        repeatRows=1,
    )
    t.setStyle(TableStyle(style))
    scale = ", ".join(f"{g} – {label}" for g, label in sheet.GRADE_LABELS.items())
    return [
        t,
        Spacer(1, 4),
        Paragraph(
            f"Skala ocen: {scale}. Poziomem wyjściowym jest ocena C; "
            "oceny A–B oraz D–F wymagają uzasadnienia.",
            st["small"],
        ),
    ]


def _comment_cell(comment, lp, st):
    if not comment:
        return Paragraph("—", st["small"])
    if len(comment) > INLINE_COMMENT_MAX:
        return Paragraph(f"Komentarz szczegółowy poniżej (pkt {lp}).", st["small"])
    return Paragraph(_text(comment), st["base"])


def _detailed_comments(data, st):
    """Komentarze za długie do tabeli — zwykłe akapity, dzielą się między strony."""
    out = []
    for lp, label, comment in _long_comments(data):
        out.append(Paragraph(f"{lp}. {escape(label)}", st["bold"]))
        out += [
            Paragraph(_text(p), ParagraphStyle("pc", parent=st["base"], spaceAfter=5))
            for p in comment.split("\n\n") if p.strip()
        ]
    return out


def _summary(data, st):
    """Sekcja 3: podsumowanie wyliczone z ocen (bez interpretacji)."""
    graded = [
        (label, data.get(sheet.grade_field(key)))
        for key, label, _info in sheet.ELEMENTS
    ]
    counts = {g: sum(1 for _l, x in graded if x == g) for g in sheet.GRADES}
    dist = ", ".join(f"{g} × {n}" for g, n in counts.items() if n)
    above = [f"{escape(l)} ({g})" for l, g in graded if g in ("A", "B")]
    below = [f"{escape(l)} ({g})" for l, g in graded if g in ("D", "E", "F")]

    out = [Paragraph(f"Rozkład ocen ({len(graded)} elementów): <b>{dist}</b>.", st["base"])]
    if not above and not below:
        out.append(Paragraph(
            "Wszystkie elementy ocenione na poziomie wyjściowym (C).", st["base"]))
    if above:
        out.append(Paragraph(
            "Powyżej poziomu wyjściowego: " + "; ".join(above) + ".", st["base"]))
    if below:
        out.append(Paragraph(
            "Poniżej poziomu wyjściowego — obszary do poprawy: " + "; ".join(below) + ".",
            st["base"]))
    return out


def _description(data, st):
    """Sekcja 4: komentarz opisowy jako zwykłe akapity."""
    text = (data.get("comment") or "").strip()
    if not text:
        return [Paragraph("Obserwator nie dodał komentarza opisowego.", st["small"])]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [Paragraph(_text(p), ParagraphStyle("p", parent=st["base"], spaceAfter=5)) for p in paragraphs]


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 13 * mm, A4[0] - doc.rightMargin, 13 * mm)
    canvas.setFont(FONT, 7.5)
    canvas.setFillColor(INK_SOFT)
    canvas.drawString(doc.leftMargin, 9 * mm, "Arkusz oceny — Wydział Sędziowski ŚZPS")
    canvas.drawRightString(A4[0] - doc.rightMargin, 9 * mm, f"Strona {doc.page}")
    canvas.restoreState()


def build_pdf(data: dict) -> bytes:
    _register_fonts()
    st = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=13 * mm, bottomMargin=18 * mm,
        title="Arkusz oceny", author=str(data.get("observer", "")),
        subject=f"{data.get('referee_name', '')} — {data.get('teams', '')}",
    )
    width = doc.width
    generated = timezone.localtime()

    story = _letterhead(st, width, generated) + [
        Paragraph("Arkusz oceny", st["title"]),
        Paragraph("1. Dane obserwacji", st["h2"]),
        _details(data, st, width),
        Paragraph("2. Wyniki oceny", st["h2"]),
        *_results(data, st, width),
    ]
    sections = []
    if _long_comments(data):
        sections.append(("Komentarze szczegółowe", _detailed_comments(data, st)))
    sections.append(("Podsumowanie", _summary(data, st)))
    sections.append(("Ocena opisowa", _description(data, st)))
    for n, (title, body) in enumerate(sections, start=3):
        # Nagłówek nie zostaje sam na dole strony.
        story.append(KeepTogether([Paragraph(f"{n}. {title}", st["h2"]), body[0]]))
        story += body[1:]

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


def pdf_filename(data: dict) -> str:
    date = data.get("match_date")
    parts = [
        "arkusz-oceny",
        date.isoformat() if date else "",
        slugify(data.get("referee_name", "")),
    ]
    return "-".join(p for p in parts if p)[:120] + ".pdf"
