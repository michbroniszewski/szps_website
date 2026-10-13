"""Eksport arkusza do jednego pliku HTML (do przeglądu poza stroną).

    python manage.py export_evaluation_html -o arkusz-podglad.html

Plik ma wbudowane style i skrypt, działa po otwarciu w przeglądarce
(bez serwera). Generowany z tych samych szablonów co strona, więc po
zmianie `sheet.py` wystarczy go wyeksportować ponownie.
"""

import base64
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from evaluation import sheet
from evaluation.forms import EvaluationForm

STATIC_DIR = Path(settings.BASE_DIR) / "static"
FONT_URL = re.compile(r"url\('(fonts/[^']+\.woff2)'\)")


def _inline_fonts(css: str) -> str:
    """url('fonts/…woff2') → data URI, żeby plik działał bez serwera."""
    def embed(match):
        data = base64.b64encode((STATIC_DIR / match.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{data})"
    return FONT_URL.sub(embed, css)


class Command(BaseCommand):
    help = "Zapisuje arkusz oceny jako samodzielny plik HTML do przeglądu."

    def add_arguments(self, parser):
        parser.add_argument(
            "-o", "--output", default="arkusz-oceny-podglad.html",
            help="Ścieżka pliku wynikowego.",
        )

    def handle(self, *args, output, **options):
        form = EvaluationForm()
        html = render_to_string("evaluation/standalone.html", {
            "form": form,
            "elements": list(form.elements()),
            "grade_scale": sheet.GRADE_SCALE,
            "grade_rules": sheet.GRADE_RULES,
            "generated": timezone.localtime(),
            "css": _inline_fonts("\n".join(
                (STATIC_DIR / name).read_text(encoding="utf-8")
                for name in ("styles.css", "evaluation.css")
            )),
            "js": (STATIC_DIR / "evaluation.js").read_text(encoding="utf-8"),
        })
        Path(output).write_text(html, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Zapisano {output}"))
