"""Definicja arkusza ewaluacyjnego (wzór WZPS 2017).

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

IMPACT = [
    ("rozwiazujacy", "rozwiązujący problemy"),
    ("bez_wplywu", "bez wpływu"),
    ("prowokujacy", "prowokujący problemy"),
]

EXPERIENCE = [
    ("duze", "duże doświadczenie"),
    ("przecietne", "przeciętne doświadczenie"),
    ("slabe", "słabe doświadczenie"),
]

RECOMMENDATION = [
    ("podwyzszenie", "↑ Podwyższenie uprawnień"),
    ("utrzymanie", "↔ Utrzymanie uprawnień"),
    ("obnizenie", "↓ Obniżenie uprawnień"),
]

OVERALL = [
    ("doskonala", "doskonała"),
    ("bardzo_dobra", "bardzo dobra"),
    ("dobra", "dobra"),
    ("dostateczna", "dostateczna"),
    ("dopuszczajaca", "dopuszczająca"),
    ("niedostateczna", "niedostateczna"),
]

# Pola „kafelkowe” w nagłówku sekcji sędziego: (klucz, etykieta, wybory).
REFEREE_CHOICES = [
    ("impact", "Wpływ na przebieg meczu", IMPACT),
    ("experience", "Poziom doświadczenia", EXPERIENCE),
    ("recommendation", "Rekomendacja SG", RECOMMENDATION),
    ("overall", "Ocena sędziowania", OVERALL),
]

REFEREES = [
    {
        "key": "r1",
        "title": "Sędzia pierwszy",
        "groups": [
            ("Technika sędziowania", [
                ("organizacja", "Organizacja: przygotowanie zawodów (czynności administracyjne), ceremoniał przedmeczowy i meczowy, punktualność"),
                ("decyzje", "Podejmowanie decyzji: gwizdek, zebranie informacji, tempo/rytm"),
                ("wspolpraca_s2", "Współpraca z sędzią II"),
                ("wspolpraca_liniowi", "Współpraca z sędziami liniowymi"),
                ("sygnalizacja", "Sygnalizacja i użycie gwizdka"),
            ]),
            ("Znajomość, stosowanie i interpretacja przepisów", [
                ("odbicie", "Ocena odbicia piłki: dokładność / stałość oceny, konsekwencja, poziom celownika, pierwsze a drugie odbicie"),
                ("gra_nad_siatka", "Gra nad siatką: przestrzeń przejścia, sięganie / penetracja, dotknięcie siatki, dotknięcie piłki w bloku"),
                ("inne_sytuacje", "Ocena innych sytuacji: zagrywka, błąd rotacji, zasłona, 4 odbicia, błędy ustawienia (w tym Libero), boisko, aut"),
                ("nietypowe", "Radzenie sobie w sytuacjach nietypowych"),
                ("koncentracja", "Koncentracja na szczegółach"),
            ]),
            ("Relacje z zespołami", [
                ("zachowanie", "Reagowanie na nieprawidłowe zachowanie / Prewencja / Sankcje"),
                ("prosby", "Reagowanie na prośby nieuzasadnione i opóźnianie gry"),
                ("zaufanie", "Zaufanie i akceptacja przez zespoły, wiarygodność decyzji"),
            ]),
            ("Osobowość i zarządzanie meczem", [
                ("wrazenie", "Ogólne wrażenie: wygląd, koncentracja, język ciała"),
                ("przywodcze", "Cechy przywódcze: stabilność, bycie fair, odporność psychiczna, autorytet"),
                ("psychologiczne", "Kompetencje psychologiczne: czucie meczu, zachowanie w sytuacjach kryzysowych, zaufanie"),
                ("jakosc", "Ogólnie jakość sędziowania względem jakości meczu"),
            ]),
        ],
    },
    {
        "key": "r2",
        "title": "Sędzia drugi",
        "groups": [
            ("Technika sędziowania", [
                ("organizacja", "Organizacja: przygotowanie zawodów (czynności administracyjne), ceremoniał przedmeczowy i meczowy, punktualność"),
                ("siatka", "Pilnowanie siatki i linii środkowej: pozycja do obserwacji"),
                ("wspolpraca_s1", "Współpraca z sędzią I"),
                ("wspolpraca_sekretarz", "Współpraca z sekretarzem"),
                ("pozycja", "Pozycja / Koordynacja / Aktywność"),
                ("sygnalizacja", "Sygnalizacja i użycie gwizdka"),
            ]),
            ("Znajomość, stosowanie i interpretacja przepisów", [
                ("akcje_siatka", "Akcje przy siatce: przestrzeń przejścia, linia środkowa, kontakt z siatką, dotknięcie piłki w bloku"),
                ("inne_akcje", "Ocena innych akcji / sytuacji: błędy ustawienia (w tym Libero), kontakt piłki z obiektem zewnętrznym"),
                ("przerwy", "Radzenie sobie z przerwami w grze: zmiany, przerwy dla odpoczynku, przerwy techniczne"),
                ("nietypowe", "Radzenie sobie w sytuacjach nietypowych"),
                ("koncentracja", "Koncentracja na szczegółach"),
            ]),
            ("Relacje z zespołami", [
                ("lawki", "Kontrola ławek i pól rozgrzewki"),
                ("kontakt", "Kontakt z zespołami i przeciwdziałanie konfliktom"),
            ]),
            ("Osobowość i zarządzanie meczem", [
                ("wrazenie", "Ogólne wrażenie: wygląd, koncentracja, mowa ciała"),
                ("przywodcze", "Cechy przywódcze: stabilność, bycie fair, odporność psychiczna, autorytet"),
                ("psychologiczne", "Kompetencje psychologiczne: czucie meczu, zachowanie w sytuacjach kryzysowych, zaufanie"),
                ("jakosc", "Ogólnie jakość sędziowania względem jakości meczu"),
            ]),
        ],
    },
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
    "Każdorazowe wystawienie oceny innej niż C, tj. A-B lub D-F wymaga komentarza – opisania sytuacji uzasadniającej podwyższenie oceny w danym elemencie (oceny A-B) lub obniżenie oceny w danym elemencie (oceny D-F).",
    "Oceny A-B są zatem bonusem za szczególnie wybitną ocenę danego elementu.",
    "Oceny D-F stanowią odzwierciedlenie błędów popełnionych przez Sędziego w ocenie danego elementu.",
]


def grade_field(referee_key: str, item_key: str) -> str:
    return f"{referee_key}_g_{item_key}"


def choice_label(choices, value) -> str:
    return dict(choices).get(value, "")
