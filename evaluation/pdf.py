"""Generowanie PDF-a z wypełnionego arkusza (ReportLab, czysty Python —
bez bibliotek systemowych, więc działa również na mydevil).

`build_pdf(cleaned_data) -> bytes` nie zależy od requestu, więc ten sam
wynik można wysłać jako załącznik e-mail.
"""

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.utils.text import slugify

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
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
SOFT = colors.HexColor("#EEF2F6")
LINE = colors.HexColor("#9AA5B1")
MARK = colors.HexColor("#E8A832")

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
    base = ParagraphStyle("base", fontName=FONT, fontSize=8.5, leading=10.5)
    return {
        "base": base,
        "small": ParagraphStyle("small", parent=base, fontSize=7.5, leading=9),
        "bold": ParagraphStyle("bold", parent=base, fontName=FONT_BOLD),
        "title": ParagraphStyle(
            "title", parent=base, fontName=FONT_BOLD, fontSize=14, leading=17,
            alignment=TA_CENTER, spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base, fontSize=8, alignment=TA_CENTER,
            textColor=colors.HexColor("#566070"), spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base, fontName=FONT_BOLD, fontSize=10.5, leading=13,
            textColor=colors.white,
        ),
        "center": ParagraphStyle("center", parent=base, alignment=TA_CENTER),
    }


def _p(text, style):
    """Paragraph z tekstu użytkownika — escapujemy, zachowujemy nowe linie."""
    text = escape(str(text or "")).replace("\n", "<br/>")
    return Paragraph(text or "—", style)


def _box(cell_style=None):
    return TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        *(cell_style or []),
    ])


def _options_row(choices, selected, st):
    """Wiersz opcji w stylu „☒ wybrane  ☐ niewybrane”."""
    parts = []
    for value, label in choices:
        mark = "☒" if value == selected else "☐"
        text = f"{mark} {escape(label)}"
        if value == selected:
            text = f"<b>{text}</b>"
        parts.append(text)
    return Paragraph("&nbsp;&nbsp;&nbsp;".join(parts), st["base"])


def _header(data, st, width):
    date = data.get("match_date")
    rows = [
        [_p("Rozgrywki:", st["bold"]), _p(data.get("competition"), st["base"]),
         _p("Data:", st["bold"]), _p(date.strftime("%d.%m.%Y") if date else "", st["base"])],
        [_p("Zespoły:", st["bold"]), _p(data.get("teams"), st["base"]),
         _p("Wynik:", st["bold"]), _p(data.get("result"), st["base"])],
        [_p("Obserwator:", st["bold"]), _p(data.get("observer"), st["base"]),
         _p("Trudność:", st["bold"]),
         _p(sheet.choice_label(sheet.DIFFICULTY, data.get("difficulty")), st["base"])],
    ]
    t = Table(rows, colWidths=[27 * mm, width - 27 * mm - 22 * mm - 45 * mm, 22 * mm, 45 * mm])
    t.setStyle(_box([("BACKGROUND", (0, 0), (0, -1), SOFT), ("BACKGROUND", (2, 0), (2, -1), SOFT)]))
    return t


def _referee(ref, data, st, width):
    r = ref["key"]
    out = []

    title = Table(
        [[Paragraph(f"{ref['title']} — {escape(data.get(f'{r}_name', ''))}", st["h2"])]],
        colWidths=[width],
    )
    title.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    out.append(title)

    rows = [
        [_p(label, st["bold"]), _options_row(choices, data.get(f"{r}_{key}"), st)]
        for key, label, choices in sheet.REFEREE_CHOICES
    ]
    t = Table(rows, colWidths=[40 * mm, width - 40 * mm])
    t.setStyle(_box([("BACKGROUND", (0, 0), (0, -1), SOFT)]))
    out += [t, Spacer(1, 4)]

    # Tabela ocen szczegółowych: element | A B C D E F
    gw = 8 * mm
    label_w = width - gw * len(sheet.GRADES)
    rows = [[_p("ELEMENTY OCENY", st["bold"])] + [_p("", st["base"])] * len(sheet.GRADES)]
    style = [
        ("SPAN", (0, 0), (-1, 0)),
        ("BACKGROUND", (0, 0), (-1, 0), SOFT),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]
    for group, items in ref["groups"]:
        row_i = len(rows)
        rows.append([_p(group, st["bold"])] + [_p(g, st["center"]) for g in sheet.GRADES])
        style.append(("BACKGROUND", (0, row_i), (-1, row_i), SOFT))
        for item_key, item_label in items:
            row_i = len(rows)
            grade = data.get(sheet.grade_field(r, item_key))
            cells = []
            for col, g in enumerate(sheet.GRADES, start=1):
                if g == grade:
                    cells.append(Paragraph(f"<b>{g}</b>", st["center"]))
                    style.append(("BACKGROUND", (col, row_i), (col, row_i), MARK))
                else:
                    cells.append("")
            rows.append([_p(item_label, st["small"])] + cells)
    t = Table(rows, colWidths=[label_w] + [gw] * len(sheet.GRADES), repeatRows=0)
    t.setStyle(_box(style))
    out.append(t)
    return out


def _text_block(title, text, st, width):
    t = Table([[_p(title, st["bold"])], [_p(text, st["base"])]], colWidths=[width])
    t.setStyle(_box([("BACKGROUND", (0, 0), (-1, 0), SOFT)]))
    return KeepTogether([t, Spacer(1, 6)])


def _legend(st, width):
    out = [Paragraph("Podstawowe objaśnienia dotyczące zasad oceny", st["bold"]), Spacer(1, 4)]
    for rule in sheet.GRADE_RULES:
        out.append(Paragraph(f"• {escape(rule)}", st["small"]))
    out.append(Spacer(1, 4))
    t = Table(
        [[_p(g, st["bold"]), _p(desc, st["small"])] for g, desc in sheet.GRADE_SCALE],
        colWidths=[8 * mm, width - 8 * mm],
    )
    t.setStyle(_box([("ALIGN", (0, 0), (0, -1), "CENTER")]))
    out.append(t)
    return out


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 7)
    canvas.setFillColor(colors.HexColor("#566070"))
    canvas.drawString(doc.leftMargin, 8 * mm, "Arkusz ewaluacyjny — Wydział Sędziowski ŚZPS")
    canvas.drawRightString(A4[0] - doc.rightMargin, 8 * mm, f"Strona {doc.page}")
    canvas.restoreState()


def build_pdf(data: dict) -> bytes:
    _register_fonts()
    st = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=14 * mm,
        title="Arkusz ewaluacyjny", author=str(data.get("observer", "")),
        subject=str(data.get("teams", "")),
    )
    width = doc.width

    story = [
        Paragraph("Arkusz ewaluacyjny sędziów", st["title"]),
        Paragraph("Wydział Sędziowski Śląskiego Związku Piłki Siatkowej", st["subtitle"]),
        _header(data, st, width),
        Spacer(1, 8),
    ]
    for i, ref in enumerate(sheet.REFEREES):
        if i:
            story.append(PageBreak())
        story += _referee(ref, data, st, width)

    story += [PageBreak()]
    for ref in sheet.REFEREES:
        r = ref["key"]
        name = data.get(f"{r}_name", "")
        story.append(_text_block(
            f"{ref['title']} ({name}) — podsumowanie mocnych i słabszych stron, "
            "sugerowane obszary do poprawy, wskazówki",
            data.get(f"{r}_summary"), st, width,
        ))
        story.append(_text_block(
            f"{ref['title']} ({name}) — przyczyny uzasadniające wystawienie ocen A-B lub D-F",
            data.get(f"{r}_reasons"), st, width,
        ))
    story.append(_text_block(
        "Informacje o obsadzie pomocniczej nieadekwatnej do poziomu meczu "
        "lub problemach organizacyjnych",
        data.get("staff_info"), st, width,
    ))
    story.append(_text_block("Notatki", data.get("notes"), st, width))
    story += [Spacer(1, 6)] + _legend(st, width)

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


def pdf_filename(data: dict) -> str:
    date = data.get("match_date")
    parts = ["arkusz", date.isoformat() if date else "", slugify(data.get("teams", ""))]
    return "-".join(p for p in parts if p)[:120] + ".pdf"
