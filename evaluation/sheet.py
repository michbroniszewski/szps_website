"""Definicja arkusza oceny jednego sędziego (na bazie wzoru WZPS 2017).

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
    ("mlodzicy", "Młodziczki / Młodzicy"),
    ("juniorki_mlodsze", "Juniorki młodsze"),
    ("juniorzy_mlodsi", "Juniorzy młodsi"),
    ("juniorki", "Juniorki"),
    ("juniorzy", "Juniorzy"),
    ("2ligak", "II Liga Śląska Kobiet"),
    ("1ligak", "I Liga Śląska Kobiet"),
    ("1ligam", "I Liga Śląska Mężczyzn"),
]

# Rekomendacja dla sędziego, który NIE jest kandydatem na szczebel
# centralny (uproszczony arkusz: mocne/słabe strony + rekomendacja).
RECOMMENDATIONS = [
    ("podwyzszenie", "Podwyższenie uprawnień"),
    ("obserwacja_podwyzszenie", "Do obserwacji pod kątem podwyższenia uprawnień"),
    ("bez_zmian", "Pozostawienie uprawnień bez zmian"),
    ("obserwacja_obnizenie", "Do obserwacji pod kątem obniżenia uprawnień"),
    ("obnizenie", "Obniżenie uprawnień"),
]

# Pozycja ocenianego sędziego — od niej zależą rozwinięcia (przycisk „i”).
POSITIONS = [
    ("r1", "Sędzia I"),
    ("r2", "Sędzia II"),
]

# Rozwinięcie elementu: lista sekcji {title?, text?, points?}. Punkty
# wyświetlane są jako a), b), c)…
_ORGANIZACJA = [
    {"points": [
        "Przybycie na obiekt na co najmniej godzinę przed meczem",
        "Ocena wyposażenia Sędziego /przygotowanie do zawodów/ – gwizdek, kartki itd.",
        "Punktualność poszczególnych elementów ceremoniału zawodów (protokołu meczowego), w tym punktualność rozpoczęcia meczu",
        "Sprawdzenie przygotowania obiektu do zawodów, w tym wyposażenia obszaru kontrolowanego: wyznaczenie pól rozgrzewki i pól kar, usytuowanie stolika sekretarza, usytuowanie i ustawienie wys. stanowiska Sędziego I, tablica wyników, sprawdzenie parametrów technicznych piłek meczowych, przymiar do mierzenia wysokości siatki, siatka (wysokość, struktura), antenki, taśmy boczne oraz osłony na słupkach",
        "Opieszałość, brak inicjatywy w usuwaniu nieprawidłowości",
        "Brak oznaczenia Kapitana lub Kapitanów podczas losowania",
        "Poprawność zarządzania oficjalną rozgrzewką oraz prezentacji zespołów i sędziów",
        "Weryfikacja obecności w obszarze kontrolowanym uprawnionych członków zespołu, w tym uczestnictwa w rozgrzewce zawodników i ich numerów z zapisami w protokole zawodów",
    ]},
]

_SYGNALIZACJA = [
    "Stosowanie oficjalnej sygnalizacji (nieprawidłowa, niechlujna sygnalizacja, pominięcie sygnalizacji)",
    "Kolejność wykonywania poszczególnych elementów sygnalizacji",
]

_NIETYPOWE = (
    "Sytuacje nietypowe, ekstremalne, w szczególności nieopisane w Przepisach gry "
    "lub Wytycznych – zachowanie Sędziów, umiejętność wybrnięcia z tego typu sytuacji"
)

_ZARZADZANIE = "Zarządzanie grą, komunikacja, nadmierna liczba lub zbędne konsultacje"

_PRZERWY_PROSBY = [
    "Przerwy pomiędzy setami, przerwa przed setem decydującym – np. zmiana stron boiska",
    "Prośby nieuzasadnione, nieodróżnienie prośby nieuzasadnionej od opóźniania gry",
]

_OSOBOWOSC = [
    {"title": "Ogólne wrażenie: wygląd, koncentracja, język ciała", "points": [
        "Ocena stroju, w którym Sędzia przybył na zawody – czystość, elegancja, prezencja",
        "Ocena stroju sędziowskiego – czystość, zgodność z wymogami, prezencja",
    ]},
    {"title": "Cechy przywódcze: stabilność, bycie fair, odporność psychiczna, autorytet", "points": [
        "Zachowanie i postawa Sędziów: zdecydowanie, stanowczość, opanowanie, pewność w podejmowaniu decyzji, mowa ciała",
        "Podatność na czynniki zewnętrzne – poddawanie się presji zespołów lub publiczności",
        "Zaufanie i akceptacja przez zespoły, wiarygodność decyzji – umiejętność uzyskania akceptacji wśród zespołów i publiczności dla podejmowanych decyzji",
    ]},
    {"title": "Kompetencje psychologiczne: czucie meczu, zachowanie w sytuacjach kryzysowych, zaufanie"},
]

# Elementy oceny: (klucz, nazwa, {pozycja: rozwinięcie}).
ELEMENTS = [
    ("organizacja",
     "Przygotowanie zawodów (czynności administracyjne), "
     "ceremoniał przedmeczowy i meczowy, punktualność",
     {"r1": _ORGANIZACJA, "r2": _ORGANIZACJA}),
    ("technika", "Technika sędziowania", {
        "r1": [
            {"title": "Podejmowanie decyzji: gwizdek, zebranie informacji, tempo/rytm", "points": [
                "Moment gwizdka/reakcja: za wcześnie lub za późno względem momentu popełnienia błędu",
                "Zebranie informacji od komisji sędziowskiej, kontakt wzrokowy",
            ]},
            {"title": "Współpraca z Sędzią II", "points": [
                "Brak kontaktu wzrokowego i obserwacji ukrytej sygnalizacji Sędziego II",
                "Nieuwzględnienie prawidłowej decyzji Sędziego II lub/oraz zmiana tej decyzji przez Sędziego I na błędną",
                _ZARZADZANIE,
            ]},
            {"title": "Sygnalizacja i użycie gwizdka", "points": _SYGNALIZACJA},
        ],
        "r2": [
            {"title": "Pilnowanie siatki i linii środkowej: pozycja do obserwacji",
             "text": "Zajęcie przez Sędziego II optymalnej pozycji do obserwacji gry."},
            {"title": "Współpraca z Sędzią I", "points": [
                "Brak pomocy Sędziego II w sytuacjach boisko/aut/„po bloku” albo czwartego odbicia (Sędzia II mógł pomóc Sędziemu I, gdyż znajdował się w dogodnej pozycji do obserwacji danego zagrania – przy błędnej decyzji ocenę należy obniżyć obu Sędziom)",
                "Stosowanie pomocniczej sygnalizacji Sędziego II, która nie jest dyskretna (jest widoczna dla zespołów, publiczności) lub nie jest jednoznacznie wyraźna dla Sędziego I",
                _ZARZADZANIE,
            ]},
            {"title": "Współpraca z sekretarzem", "points": [
                "Współpraca przy zmianach",
                "Kontrola protokołu podczas przerw w grze oraz przerw pomiędzy setami",
            ]},
            {"title": "Pozycja, koordynacja, aktywność",
             "text": "Aktywność, przemieszczanie (w tym tempo przemieszczania się, odpowiednie do tempa gry) – ustawianie się po stronie zespołu przyjmującego zagrywkę / blokującego."},
            {"title": "Sygnalizacja i użycie gwizdka", "points": _SYGNALIZACJA + [
                "Zajmowanie przez Sędziego II prawidłowej pozycji do wykonania sygnalizacji",
            ]},
        ],
    }),
    ("przepisy", "Znajomość, stosowanie i interpretacja przepisów gry", {
        "r1": [
            {"points": [
                "Ocena odbicia piłki: dokładność / stałość oceny, konsekwencja, poziom celownika, pierwsze odbicie, ocena podwójnego odbicia w ataku, czystość ataku",
                "Gra nad siatką: przestrzeń przejścia, sięganie, gra w przestrzeni przeciwnika, dotknięcie siatki, dotknięcie piłki w bloku",
                "Ocena innych sytuacji: zagrywka, błąd rotacji, zasłona, 4 odbicia, boisko, aut",
                f"Radzenie sobie w sytuacjach nietypowych. {_NIETYPOWE}",
            ]},
        ],
        "r2": [
            {"title": "Akcje przy siatce: przestrzeń przejścia, linia środkowa, kontakt z siatką, dotknięcie piłki w bloku"},
            {"title": "Ocena innych sytuacji: błędy ustawienia (w tym Libero), kontakt piłki z obiektem zewnętrznym"},
            {"title": "Radzenie sobie z przerwami w grze", "points": [
                "Przerwy na odpoczynek, czas ich trwania, zgłaszanie wykorzystania 2 przerwy – przykładowo błędem jest przyznanie przerwy wyłącznie na podstawie prośby słownej lub zgłoszonej wyłącznie przy użyciu sygnalizatora dźwiękowego (bez sygnalizacji Trenera), albo przez nieuprawnioną do tego osobę",
                "Zmiany zawodników, m.in.: procedura zmiany, strefa zmian, zgłaszanie wykorzystania 7 i 8 zmiany, dopuszczenie do zmiany z udziałem nieprzygotowanego do zmiany zawodnika",
                "Prośba o zmianę nieregulaminową (próba zmiany nieregulaminowej)",
                "Przerwy pomiędzy setami – w przypadku Sędziego II dostarczenie kartek z ustawieniem zespołów",
            ]},
            {"title": "Radzenie sobie w sytuacjach nietypowych", "text": _NIETYPOWE},
        ],
    }),
    ("relacje", "Relacje z zespołami (dyscyplina, zaufanie zawodników i trenerów)", {
        "r1": [
            {"title": "Reagowanie na nieprawidłowe zachowanie / Prewencja / Sankcje", "points": [
                "Utrzymanie dyscypliny na zawodach, drobne przewinienia i prewencja",
                "Sankcje za niewłaściwe zachowanie – adekwatność w stosunku do zachowania, gradacja",
                "Dyskusje z nieuprawnionymi członkami zespołów, przedłużające się dyskusje lub dyskusje niezwiązane z interpretacją przepisów – podczas oraz bezpośrednio po meczu w obszarze kontrolowanym przez komisję sędziowską",
                "Umiejętność zachowania się w trudnych sytuacjach",
            ]},
            {"title": "Reagowanie na prośby nieuzasadnione i opóźnianie gry", "points": [
                "Utrzymanie „tempa gry”, płynność przeprowadzenia zawodów",
                *_PRZERWY_PROSBY,
                "Sankcje za opóźnianie gry",
            ]},
        ],
        "r2": [
            {"title": "Kontrola ławek i pól rozgrzewki",
             "text": "Utrzymanie „tempa gry”, płynność przeprowadzenia zawodów – w przypadku Sędziego II:",
             "points": [
                "Opóźnienie wznowienia gry przez podjęcie zbędnej interwencji w związku z wyposażeniem zespołu znajdującym się na ławce lub w jej okolicy, które nie powodowało zagrożenia",
                "Brak reakcji najpóźniej przed kolejną wymianą na wyposażenie zespołu stwarzające zagrożenie, nieprawidłową pozycję, zachowanie lub strój członka zespołu, znajdujące się na / przy ławce rezerwowych albo w polu rozgrzewki (niezależnie od czasu trwania nieprawidłowości)",
                "Przeszkadzanie zespołowi podczas przerwy na odpoczynek",
             ]},
            {"title": "Kontakt z zespołami i przeciwdziałanie konfliktom", "points": _PRZERWY_PROSBY},
        ],
    }),
    ("osobowosc", "Osobowość i zarządzanie meczem", {"r1": _OSOBOWOSC, "r2": _OSOBOWOSC}),
]

GRADE_SCALE = [
    ("A", 'wybitna, doskonała, wzorcowa ocena danego elementu („przykład dla innych”)'),
    ("B", "bardzo dobra i prawidłowa ocena danego elementu, bez błędów, pełna kontrola zdarzeń, zwłaszcza przy trudnych zawodach / szczególnie trudnych sytuacjach"),
    ("C", "prawidłowa ocena danego elementu, dobra kontrola – bez wpływu na przebieg i charakter rywalizacji sportowej, bez uwag i komentarzy"),
    ("D", "niewielka ilość błędów w ocenie danego elementu – w tym incydentalne (1-2) błędy wpływające na przebieg lub charakter rywalizacji sportowej, zachowana kontrola, ale potrzebna poprawa w danym elemencie"),
    ("E", "znacząca liczba błędów w ocenie danego elementu – w tym kilka (3-5) wpływających na przebieg lub charakter rywalizacji sportowej, braki w umiejętnościach, utrata kontroli, potrzebna znacząca poprawa w danym elemencie"),
    ("F", "rażąco duża liczba błędów w ocenie danego elementu – poziom oceny wpłynął znacząco na przebieg rywalizacji sportowej, kompletny brak kontroli danego elementu, katastrofa, zachowania nieakceptowalne"),
]

# Krótkie nazwy ocen do dokumentu wynikowego (PDF).
GRADE_LABELS = {
    "A": "wybitna",
    "B": "bardzo dobra",
    "C": "prawidłowa",
    "D": "niewielkie błędy",
    "E": "znaczące błędy",
    "F": "rażące błędy",
}

GRADE_RULES = [
    "Oceny szczegółowe (A-F) odzwierciedlają ogólne wrażenie dotyczące odpowiedniej sekcji (elementu gry) przedstawionego w arkuszu.",
    "Punktem wyjściowym jest ocena C. Wystawienie tej oceny w danym elemencie nie wymaga opisu ani komentarza ze strony Obserwatora w podsumowaniu.",
    "Każdorazowe wystawienie oceny innej niż C, tj. A-B lub D-F wymaga komentarza przy danym elemencie – opisania sytuacji uzasadniającej podwyższenie oceny w danym elemencie (oceny A-B) lub obniżenie oceny w danym elemencie (oceny D-F).",
    "Oceny A-B są zatem bonusem za szczególnie wybitną ocenę danego elementu.",
    "Oceny D-F stanowią odzwierciedlenie błędów popełnionych przez Sędziego w ocenie danego elementu.",
]


def grade_field(item_key: str) -> str:
    return f"g_{item_key}"


def comment_field(item_key: str) -> str:
    return f"c_{item_key}"


def choice_label(choices, value) -> str:
    return dict(choices).get(value, "")
