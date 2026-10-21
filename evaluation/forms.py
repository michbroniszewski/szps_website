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
    """Arkusz jednego sędziego; elementy oceny budowane z `sheet.py`.

    Pola elementów: `g_<klucz>` (ocena A–F) i `c_<klucz>` (komentarz).
    """

    competition = forms.ChoiceField(
        label="Rozgrywki",
        choices=[("", "Wybierz rozgrywki…")] + sheet.COMPETITIONS,
    )
    difficulty = _radio(sheet.DIFFICULTY, label="Trudność meczu")
    teams = forms.CharField(
        label="Mecz",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "np. GKS Katowice – MKS Będzin"}),
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
    observer_email = forms.EmailField(
        label="E-mail obserwatora (kopia wysyłki)",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "opcjonalnie", "autocomplete": "email"}),
    )

    referee_name = forms.CharField(label="Imię i nazwisko sędziego", max_length=120)
    position = _radio(sheet.POSITIONS, label="Pozycja")

    comment = forms.CharField(
        label="Komentarz opisowy",
        required=False,
        max_length=8000,
        widget=forms.Textarea(attrs={"rows": 6}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pola elementów wstawiamy przed komentarzem ogólnym.
        comment = self.fields.pop("comment")
        for key, label, _info in sheet.ELEMENTS:
            self.fields[sheet.grade_field(key)] = forms.ChoiceField(
                label=label,
                choices=[(g, g) for g in sheet.GRADES],
                initial=sheet.DEFAULT_GRADE,
                widget=forms.RadioSelect,
            )
            self.fields[sheet.comment_field(key)] = forms.CharField(
                label="Komentarz do oceny",
                required=False,
                max_length=4000,
                widget=forms.Textarea(attrs={"rows": 2}),
            )
        self.fields["comment"] = comment

    def clean(self):
        cleaned = super().clean()
        # Zasada z objaśnień: każda ocena inna niż C wymaga komentarza.
        for key, _label, _info in sheet.ELEMENTS:
            grade = cleaned.get(sheet.grade_field(key), sheet.DEFAULT_GRADE)
            if grade != sheet.DEFAULT_GRADE and not cleaned.get(sheet.comment_field(key)):
                self.add_error(
                    sheet.comment_field(key),
                    "Wystawiono ocenę inną niż C — uzasadnij ją w komentarzu.",
                )
        return cleaned

    # ── struktura pomocnicza dla szablonu ────────────────────────────
    def elements(self):
        for key, label, info in sheet.ELEMENTS:
            yield {
                "key": key,
                "label": label,
                "grade": self[sheet.grade_field(key)],
                "comment": self[sheet.comment_field(key)],
                # Ta sama treść dla obu pozycji → jedno rozwinięcie bez przełączania.
                "info_shared": info["r1"] if info["r1"] is info["r2"] else None,
                "info": [(pos, info[pos]) for pos, _l in sheet.POSITIONS],
            }
