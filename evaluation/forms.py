from django import forms

from . import sheet


class EvaluationForm(forms.Form):
    """Formularz budowany dynamicznie z `sheet.py`.

    Nazwy pól: nagłówek meczu bez prefiksu, a pola sędziów z prefiksem
    `r1_` / `r2_` (np. `r1_name`, `r1_g_technika`, `r1_comment`).
    """

    competition = forms.ChoiceField(
        label="Rozgrywki",
        choices=[("", "Wybierz rozgrywki…")] + sheet.COMPETITIONS,
    )
    difficulty = forms.ChoiceField(
        label="Trudność meczu",
        choices=sheet.DIFFICULTY,
        widget=forms.RadioSelect,
        error_messages={"required": "Zaznacz jedną z opcji."},
    )
    teams = forms.CharField(
        label="Mecz",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "np. KS Gwarek Zabrze – MKS Będzin"}),
    )
    match_date = forms.DateField(
        label="Data",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    result = forms.CharField(
        label="Wynik",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "np. 3:1 (25:20, 23:25, 25:18, 25:22)"}),
    )
    observer = forms.CharField(label="Obserwator", max_length=120)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for ref in sheet.REFEREES:
            r = ref["key"]
            self.fields[f"{r}_name"] = forms.CharField(
                label="Imię i nazwisko", max_length=120,
            )
            for item_key, item_label in sheet.ELEMENTS:
                self.fields[sheet.grade_field(r, item_key)] = forms.ChoiceField(
                    label=item_label,
                    choices=[(g, g) for g in sheet.GRADES],
                    initial=sheet.DEFAULT_GRADE,
                    widget=forms.RadioSelect,
                )
            self.fields[f"{r}_comment"] = forms.CharField(
                label="Komentarz opisowy",
                required=False,
                max_length=8000,
                widget=forms.Textarea(attrs={"rows": 6}),
            )

    def clean(self):
        cleaned = super().clean()
        # Zasada z objaśnień: każda ocena inna niż C wymaga komentarza.
        for ref in sheet.REFEREES:
            r = ref["key"]
            non_default = any(
                cleaned.get(sheet.grade_field(r, k), sheet.DEFAULT_GRADE) != sheet.DEFAULT_GRADE
                for k, _label in sheet.ELEMENTS
            )
            if non_default and not cleaned.get(f"{r}_comment"):
                self.add_error(
                    f"{r}_comment",
                    "Wystawiono ocenę inną niż C — uzasadnij ją w komentarzu.",
                )
        return cleaned

    # ── struktury pomocnicze dla szablonu ────────────────────────────
    def referee_sections(self):
        for ref in sheet.REFEREES:
            r = ref["key"]
            yield {
                "key": r,
                "title": ref["title"],
                "name": self[f"{r}_name"],
                "items": [self[sheet.grade_field(r, k)] for k, _l in sheet.ELEMENTS],
                "comment": self[f"{r}_comment"],
            }
