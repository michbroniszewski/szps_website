from django import forms

from . import sheet


def _radio(choices, **kwargs):
    return forms.ChoiceField(
        choices=choices,
        widget=forms.RadioSelect,
        error_messages={"required": "Zaznacz jedną z opcji."},
        **kwargs,
    )


class EvaluationForm(forms.Form):
    """Formularz budowany dynamicznie z `sheet.py`.

    Nazwy pól: nagłówek meczu bez prefiksu, a pola sędziów z prefiksem
    `r1_` / `r2_` (np. `r1_name`, `r1_g_organizacja`).
    """

    competition = forms.CharField(label="Rozgrywki", max_length=200)
    match_date = forms.DateField(
        label="Data",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    teams = forms.CharField(label="Zespoły", max_length=200)
    result = forms.CharField(label="Wynik", max_length=120)
    observer = forms.CharField(label="Obserwator", max_length=120)
    difficulty = _radio(sheet.DIFFICULTY, label="Trudność meczu")

    staff_info = forms.CharField(
        label="Informacje o obsadzie pomocniczej nieadekwatnej do poziomu "
              "meczu lub problemach organizacyjnych",
        required=False,
        max_length=4000,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    notes = forms.CharField(
        label="Notatki",
        required=False,
        max_length=4000,
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for ref in sheet.REFEREES:
            r = ref["key"]
            self.fields[f"{r}_name"] = forms.CharField(
                label="Imię i nazwisko", max_length=120,
            )
            for key, label, choices in sheet.REFEREE_CHOICES:
                self.fields[f"{r}_{key}"] = _radio(choices, label=label)
            for _group, items in ref["groups"]:
                for item_key, item_label in items:
                    self.fields[sheet.grade_field(r, item_key)] = _radio(
                        [(g, g) for g in sheet.GRADES],
                        label=item_label,
                        initial=sheet.DEFAULT_GRADE,
                    )
            self.fields[f"{r}_summary"] = forms.CharField(
                label="Podsumowanie mocnych i słabszych stron sędziego — "
                      "sugerowane obszary do poprawy, wskazówki",
                required=False,
                max_length=6000,
                widget=forms.Textarea(attrs={"rows": 5}),
            )
            self.fields[f"{r}_reasons"] = forms.CharField(
                label="Przyczyny uzasadniające wystawienie ocen A-B lub D-F",
                required=False,
                max_length=6000,
                widget=forms.Textarea(attrs={"rows": 5}),
            )

    def clean(self):
        cleaned = super().clean()
        # Zasada z objaśnień: każda ocena inna niż C wymaga komentarza.
        for ref in sheet.REFEREES:
            r = ref["key"]
            if self._non_default_grades(cleaned, ref) and not cleaned.get(f"{r}_reasons"):
                self.add_error(
                    f"{r}_reasons",
                    "Wystawiono ocenę inną niż C — opisz przyczyny.",
                )
        return cleaned

    @staticmethod
    def _non_default_grades(cleaned, ref):
        return [
            item_key
            for _group, items in ref["groups"]
            for item_key, _label in items
            if cleaned.get(sheet.grade_field(ref["key"], item_key), sheet.DEFAULT_GRADE)
            != sheet.DEFAULT_GRADE
        ]

    # ── struktury pomocnicze dla szablonu ────────────────────────────
    def referee_sections(self):
        for ref in sheet.REFEREES:
            r = ref["key"]
            yield {
                "key": r,
                "title": ref["title"],
                "name": self[f"{r}_name"],
                "choices": [self[f"{r}_{key}"] for key, _l, _c in sheet.REFEREE_CHOICES],
                "groups": [
                    {
                        "title": group,
                        "items": [self[sheet.grade_field(r, k)] for k, _l in items],
                    }
                    for group, items in ref["groups"]
                ],
                "summary": self[f"{r}_summary"],
                "reasons": self[f"{r}_reasons"],
            }
