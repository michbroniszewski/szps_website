"""Definicja arkusza ewaluacyjnego (na bazie wzoru WZPS 2017, uproszczona).

Jedno źródło prawdy dla formularza HTML, walidacji i PDF-a — zmiana
treści arkusza (np. nowy element oceny) to edycja tylko tego pliku.
Klucze (`key`) trafiają do nazw pól formularza, więc po wdrożeniu nie
należy ich zmieniać bez potrzeby.
"""

GRADES = ["A", "B", "C", "D", "E", "F"]
# Punkt wyjścia wg objaśnień — ocena C nie wymaga komentarza.
DEFAULT_GRADE = "C"

DIFFICULTY = [
    ("latwy", "łatwy"),
    ("sredni", "średni"),
    ("trudny", "trudny"),
]

# Rodzaj rozgrywek — lista rozwijana w nagłówku arkusza.
COMPETITIONS = [
    ("mlodzicy", "młodziczki / młodzicy"),
    ("juniorki_mlodsze", "juniorki młodsze"),
    ("juniorzy_mlodsi", "juniorzy młodsi"),
    ("juniorki", "juniorki"),
    ("juniorzy", "juniorzy"),
    ("2ligak", "II Liga Śląska Kobiet"),
    ("1ligak", "I Liga Śląska Kobiet"),
    ("1ligam", "I Liga Śląska Mężczyzn"),
]

# Elementy oceny — wspólne dla obu pozycji.
ELEMENTS = [
    ("organizacja", "Organizacja, przygotowanie do zawodów"),
    ("technika", "Technika sędziowania"),
    ("przepisy", "Znajomość, stosowanie i interpretacja przepisów gry"),
    ("relacje", "Relacje z zespołami (dyscyplina, zaufanie zawodników i trenerów)"),
    ("osobowosc", "Osobowość i zarządzanie meczem"),
]

REFEREES = [
    {"key": "r1", "title": "Sędzia I"},
    {"key": "r2", "title": "Sędzia II"},
]

GRADE_SCALE = [
    ("A", 'wybitna, doskonała, wzorcowa ocena danego elementu („przykład dla innych”)'),
    ("B", "bardzo dobra i prawidłowa ocena danego elementu, bez błędów, pełna kontrola zdarzeń, zwłaszcza przy trudnych zawodach / szczególnie trudnych sytuacjach"),
    ("C", "prawidłowa ocena danego elementu, dobra kontrola – bez wpływu na przebieg i charakter rywalizacji sportowej, bez uwag i komentarzy"),
    ("D", "niewielka ilość błędów w ocenie danego elementu – w tym incydentalne (1-2) błędy wpływające na przebieg lub charakter rywalizacji sportowej, zachowana kontrola, ale potrzebna poprawa w danym elemencie"),
    ("E", "znacząca liczba błędów w ocenie danego elementu – w tym kilka (3-5) wpływających na przebieg lub charakter rywalizacji sportowej, braki w umiejętnościach, utrata kontroli, potrzebna znacząca poprawa w danym elemencie"),
    ("F", "rażąco duża liczba błędów w ocenie danego elementu – poziom oceny wpłynął znacząco na przebieg rywalizacji sportowej, kompletny brak kontroli danego elementu, katastrofa, zachowania nieakceptowalne"),
]

GRADE_RULES = [
    "Oceny szczegółowe (A-F) odzwierciedlają ogólne wrażenie dotyczące odpowiedniej sekcji (elementu gry) przedstawionego w arkuszu.",
    "Punktem wyjściowym jest ocena C. Wystawienie tej oceny w danym elemencie nie wymaga opisu ani komentarza ze strony Obserwatora w podsumowaniu.",
    "Każdorazowe wystawienie oceny innej niż C, tj. A-B lub D-F wymaga komentarza – opisania w komentarzu opisowym sytuacji uzasadniającej podwyższenie oceny w danym elemencie (oceny A-B) lub obniżenie oceny w danym elemencie (oceny D-F).",
    "Oceny A-B są zatem bonusem za szczególnie wybitną ocenę danego elementu.",
    "Oceny D-F stanowią odzwierciedlenie błędów popełnionych przez Sędziego w ocenie danego elementu.",
]


def grade_field(referee_key: str, item_key: str) -> str:
    return f"{referee_key}_g_{item_key}"


def choice_label(choices, value) -> str:
    return dict(choices).get(value, "")
