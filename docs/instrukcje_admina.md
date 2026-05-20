# Instrukcje dla administratora strony

---

## 1. Jak dodać post do Aktualności

### Krok 1 — Zaloguj się do panelu administracyjnego

Wejdź na adres: `http://adres-twojej-strony/admin/`

Podaj login i hasło administratora.

---

### Krok 2 — Przejdź do Aktualności

Na stronie głównej panelu kliknij **„Aktualności"** w sekcji **News**.

![Panel admina — sekcja News]

---

### Krok 3 — Utwórz nowy post

Kliknij przycisk **„Dodaj aktualność +"** w prawym górnym rogu.

---

### Krok 4 — Wypełnij formularz

**Sekcja „Treść":**

| Pole | Co wpisać | Wymagane |
|---|---|---|
| **Tytuł** | Nagłówek artykułu | ✅ |
| **Slug** | Wypełnia się automatycznie z tytułu — możesz zostawić | ✅ |
| **Kategoria** | Wybierz z listy (opcjonalnie) | — |
| **Skrót** | Krótki opis widoczny na liście (max 500 znaków) | — |
| **Treść** | Pełna treść artykułu w edytorze | ✅ |
| **Zdjęcie** | Zdjęcie nagłówkowe (JPG, PNG) | — |

> **Slug** to fragment adresu URL, np. tytuł `"Mecz ligowy 2025"` → adres `/aktualnosci/mecz-ligowy-2025/`. Nie używaj polskich znaków — Django usuwa je automatycznie.

**Sekcja „Publikacja":**

| Pole | Co oznacza |
|---|---|
| **Opublikowany** | ☑ zaznacz, żeby post był widoczny na stronie |
| **Przypięty** | ☑ zaznacz, żeby post pojawił się w sekcji „Ważne komunikaty" na stronie głównej |
| **Data publikacji** | Domyślnie dzisiaj — możesz ustawić datę wstecz lub przyszłą |

---

### Krok 5 — Zapisz

Kliknij **„Zapisz"** (prawy dolny róg).

Post z **odznaczonym „Opublikowany"** jest zapisany jako wersja robocza — nie będzie widoczny na stronie.

---

### Szybka edycja z listy

Na liście aktualności możesz kliknąć checkboxy w kolumnach **„Opublikowany"** i **„Przypięty"** bezpośrednio — bez otwierania posta. Po zmianie kliknij **„Zapisz"** na dole listy.

---

---

## 2. Jak udostępnić dokument na stronie

### Krok 1 — Zaloguj się do panelu administracyjnego

Wejdź na adres: `http://adres-twojej-strony/admin/`

---

### Krok 2 — Przejdź do Dokumentów

Na stronie głównej panelu kliknij **„Dokumenty"** w sekcji **Documents**.

---

### Krok 3 — Dodaj nowy dokument

Kliknij przycisk **„Dodaj dokument +"** w prawym górnym rogu.

---

### Krok 4 — Wypełnij formularz

| Pole | Co wpisać | Wymagane |
|---|---|---|
| **Tytuł** | Nazwa dokumentu widoczna na stronie | ✅ |
| **Opis** | Krótki opis zawartości (opcjonalnie, pomaga w wyszukiwaniu) | — |
| **Plik** | Wybierz plik z dysku (PDF, DOCX, XLSX, ZIP…) | ✅ |
| **Kategoria** | Przyporządkuj do kategorii (opcjonalnie) | — |
| **Aktywny** | ☑ zaznaczone = dokument widoczny na stronie | ✅ |

> **Wskazówka:** Dobrze wypełniony **Opis** sprawia, że dokument łatwiej znaleźć przez wyszukiwarkę na stronie. Wpisz np. słowa kluczowe: sezon, rok, typ dokumentu.

---

### Krok 5 — Zapisz

Kliknij **„Zapisz"**.

Dokument pojawi się natychmiast na stronie `/dokumenty/` i będzie dostępny do pobrania.

---

### Jak ukryć dokument bez usuwania

Na liście dokumentów odznacz checkbox w kolumnie **„Aktywny"** i kliknij **„Zapisz"**. Dokument pozostaje w bazie, ale znika ze strony.

---

### Jak zarządzać kategoriami dokumentów

W panelu admina wejdź w **„Kategorie dokumentów"**:

- Dodaj nową kategorię (np. „Przepisy gry", „Protokoły", „Regulaminy sezonu")
- Ustaw pole **„Kolejność"** — liczba decyduje o kolejności wyświetlania (0 = pierwsza)

Kategorię przypisujesz do dokumentu w polu **„Kategoria"** podczas dodawania lub edycji dokumentu.

---

---

## 3. Jak wyróżnić dokument na stronie głównej

W panelu admina wejdź w **„Dokumenty"** i otwórz wybrany dokument (lub utwórz nowy).

Zaznacz pole **„Wyróżniony (strona główna)"** — dokument pojawi się w sekcji „Ważne dokumenty" na stronie głównej (maksymalnie 6 wyróżnionych dokumentów jest wyświetlanych).

Odznacz to pole, żeby usunąć dokument z sekcji na stronie głównej, nie usuwając go z archiwum.

---

## 4. Jak dodać i zarządzać ankietą

### Krok 1 — Utwórz ankietę

W panelu admina wejdź w **„Ankiety"** (sekcja Contact) i kliknij **„Dodaj ankietę +"**.

| Pole | Co wpisać |
|---|---|
| **Tytuł** | Nagłówek ankiety widoczny dla respondentów |
| **Opis** | Krótkie wprowadzenie (opcjonalnie) |
| **Aktywna** | ☑ zaznacz, żeby ankieta była widoczna pod `/ankiety/` |
| **Zamknięcie** | Data i godzina automatycznego zamknięcia (opcjonalnie) |

### Krok 2 — Dodaj pytania

W tym samym formularzu, poniżej danych ankiety, pojawi się sekcja **„Pytania"**. Kliknij **„Dodaj kolejny Pytanie"**.

| Pole | Co oznacza |
|---|---|
| **Pytanie** | Treść pytania |
| **Typ pytania** | Odpowiedź tekstowa / Wybór spośród opcji / Tak–Nie |
| **Kolejność** | Liczba — decyduje o kolejności wyświetlania (0 = pierwsze) |
| **Wymagane** | ☑ respondent musi odpowiedzieć na to pytanie |

Dla pytań typu **„Wybór spośród opcji"** — po zapisaniu ankiety otwórz pytanie osobno i dodaj opcje odpowiedzi w sekcji **„Opcje odpowiedzi"**.

### Krok 3 — Przeglądaj odpowiedzi

W panelu admina wejdź w **„Odpowiedzi na ankiety"**. Widok pokazuje każde przesłane wypełnienie z datą i e-mailem respondenta (jeśli podał).

### Jak zamknąć ankietę przed terminem

Odznacz pole **„Aktywna"** na liście ankiet i kliknij „Zapisz". Ankieta znika z listy publicznej, odpowiedzi zostają w bazie.

---

## Szybki podgląd — gdzie co widać na stronie

| Co dodajesz | Gdzie pojawia się na stronie |
|---|---|
| Post z **„Opublikowany" ☑** | `/aktualnosci/` oraz strona główna |
| Post z **„Przypięty" ☑** | Sekcja „Ważne komunikaty" na stronie głównej |
| Dokument z **„Aktywny" ☑** | `/dokumenty/` — widoczny i możliwy do pobrania |
| Dokument z **„Aktywny" ☐** | Ukryty — tylko w panelu admina |
| Dokument z **„Wyróżniony" ☑** | Sekcja „Ważne dokumenty" na stronie głównej |
| Ankieta z **„Aktywna" ☑** | `/ankiety/` — widoczna i możliwa do wypełnienia |
| Ankieta z **„Aktywna" ☐** | Ukryta — tylko w panelu admina |
