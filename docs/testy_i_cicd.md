# Plan testowania i model CI/CD

> Dokument opisuje strategię testowania projektu ŚZPS oraz założenia pod automatyczny pipeline CI/CD.

---

## Spis treści

1. [Piramida testów](#1-piramida-testów)
2. [Co testować w tym projekcie](#2-co-testować-w-tym-projekcie)
3. [Testy jednostkowe — modele](#3-testy-jednostkowe--modele)
4. [Testy integracyjne — widoki i formularze](#4-testy-integracyjne--widoki-i-formularze)
5. [Testy szablonów](#5-testy-szablonów)
6. [Testy manualne — lista kontrolna](#6-testy-manualne--lista-kontrolna)
7. [Model CI/CD z GitHub Actions](#7-model-cicd-z-github-actions)
8. [Uruchamianie testów lokalnie](#8-uruchamianie-testów-lokalnie)
9. [Co dalej — kolejne etapy](#9-co-dalej--kolejne-etapy)

---

## 1. Piramida testów

```
        /\
       /  \        E2E / Selenium
      / UI \       (wolne, kosztowne)
     /------\
    /        \     Testy integracyjne
   / Integracja\   widoki, formularze, URL
  /------------\
 /              \  Testy jednostkowe
/ Jednostkowe   \  modele, funkcje, logika
/________________\
```

**Zasada:** Im niżej w piramidzie, tym więcej testów. Testy jednostkowe są szybkie i tanie — piszemy ich najwięcej. Testy E2E są powolne — piszemy tylko dla krytycznych ścieżek.

---

## 2. Co testować w tym projekcie

### Priorytety

| Obszar | Priorytet | Typ testu |
|---|---|---|
| Modele — walidacja pól | 🔴 Wysoki | Jednostkowy |
| Widoki — kody HTTP | 🔴 Wysoki | Integracyjny |
| Formularz kontaktowy — zapis do bazy | 🔴 Wysoki | Integracyjny |
| Ankiety — kompletny przepływ | 🔴 Wysoki | Integracyjny |
| Wyszukiwarka dokumentów | 🟡 Średni | Integracyjny |
| Panel admina — dostęp | 🟡 Średni | Integracyjny |
| Szablony — renderowanie bez błędów | 🟡 Średni | Integracyjny |
| Responsywność UI | 🟢 Niski | Manualny / E2E |
| SEO (meta tagi) | 🟢 Niski | Integracyjny |

### Czego **nie** testować

- Wbudowanych mechanizmów Django (np. że `CharField` ma `max_length`) — Django sam to testuje
- Wyglądu CSS — to domena testów wizualnych / manualnych
- Zewnętrznego systemu obsad — to nie jest nasz kod

---

## 3. Testy jednostkowe — modele

Plik: `news/tests.py`, `documents/tests.py`, `contact/tests.py`

### Przykłady do zaimplementowania

```python
# news/tests.py
from django.test import TestCase
from django.utils import timezone
from .models import NewsCategory, NewsPost


class NewsCategoryTest(TestCase):

    def test_str_zwraca_nazwe(self):
        cat = NewsCategory.objects.create(name="Komunikaty", slug="komunikaty")
        self.assertEqual(str(cat), "Komunikaty")


class NewsPostTest(TestCase):

    def setUp(self):
        self.category = NewsCategory.objects.create(
            name="Komunikaty", slug="komunikaty"
        )

    def test_str_zwraca_tytul(self):
        post = NewsPost.objects.create(
            title="Mecz ligowy",
            slug="mecz-ligowy",
            content="Treść.",
        )
        self.assertEqual(str(post), "Mecz ligowy")

    def test_domyslnie_nieopublikowany(self):
        post = NewsPost.objects.create(
            title="Roboczy post", slug="roboczy", content="."
        )
        self.assertFalse(post.is_published)

    def test_domyslnie_nieprzypiety(self):
        post = NewsPost.objects.create(
            title="Roboczy post", slug="roboczy-2", content="."
        )
        self.assertFalse(post.is_pinned)

    def test_kolejnosc_przypiety_pierwszy(self):
        NewsPost.objects.create(
            title="Zwykły", slug="zwykly", content=".", is_published=True
        )
        NewsPost.objects.create(
            title="Przypięty", slug="przypiety", content=".",
            is_published=True, is_pinned=True
        )
        pierwszy = NewsPost.objects.filter(is_published=True).first()
        self.assertEqual(pierwszy.title, "Przypięty")
```

```python
# documents/tests.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Document


class DocumentExtensionTest(TestCase):

    def test_rozszerzenie_pdf(self):
        plik = SimpleUploadedFile("regulamin.pdf", b"dane", content_type="application/pdf")
        doc = Document(title="Regulamin", file=plik)
        self.assertEqual(doc.extension(), "PDF")

    def test_rozszerzenie_brak(self):
        plik = SimpleUploadedFile("plik", b"dane")
        doc = Document(title="Bez rozszerzenia", file=plik)
        self.assertEqual(doc.extension(), "PLIK")
```

```python
# contact/tests.py
from django.test import TestCase
from .models import Survey, Question, Choice


class SurveyModelTest(TestCase):

    def test_str_zwraca_tytul(self):
        survey = Survey.objects.create(title="Ankieta sezonowa")
        self.assertEqual(str(survey), "Ankieta sezonowa")

    def test_domyslnie_aktywna(self):
        survey = Survey.objects.create(title="Nowa ankieta")
        self.assertTrue(survey.is_active)
```

📖 [Django TestCase](https://docs.djangoproject.com/en/5.2/topics/testing/tools/#django.test.TestCase) | [SimpleUploadedFile](https://docs.djangoproject.com/en/5.2/ref/files/uploads/#django.core.files.uploadedfile.SimpleUploadedFile)

---

## 4. Testy integracyjne — widoki i formularze

Django dostarcza `Client` — symulator przeglądarki do testowania widoków.

```python
# news/tests.py (cd.)
from django.test import TestCase, Client
from django.urls import reverse
from .models import NewsPost, NewsCategory


class NewsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.post = NewsPost.objects.create(
            title="Testowy post",
            slug="testowy-post",
            content="Treść testowego posta.",
            is_published=True,
        )
        self.draft = NewsPost.objects.create(
            title="Wersja robocza",
            slug="wersja-robocza",
            content="Szkic.",
            is_published=False,
        )

    def test_lista_zwraca_200(self):
        url = reverse("news:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_lista_zawiera_opublikowany_post(self):
        url = reverse("news:list")
        response = self.client.get(url)
        self.assertContains(response, "Testowy post")

    def test_lista_nie_zawiera_roboczego_posta(self):
        url = reverse("news:list")
        response = self.client.get(url)
        self.assertNotContains(response, "Wersja robocza")

    def test_szczegoly_opublikowanego_posta(self):
        url = reverse("news:detail", args=["testowy-post"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Treść testowego posta.")

    def test_szczegoly_roboczego_posta_zwraca_404(self):
        url = reverse("news:detail", args=["wersja-robocza"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_filtrowanie_po_kategorii(self):
        cat = NewsCategory.objects.create(name="Liga", slug="liga")
        NewsPost.objects.create(
            title="Post w lidze", slug="post-liga",
            content=".", is_published=True, category=cat
        )
        url = reverse("news:list") + "?kategoria=liga"
        response = self.client.get(url)
        self.assertContains(response, "Post w lidze")
        self.assertNotContains(response, "Testowy post")
```

```python
# contact/tests.py (cd.)
from django.test import TestCase, Client
from django.urls import reverse
from .models import ContactMessage, Survey, Question, SurveyResponse


class ContactFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("contact:contact")

    def test_strona_kontaktowa_zwraca_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_poprawny_formularz_zapisuje_wiadomosc(self):
        dane = {
            "name": "Jan Kowalski",
            "email": "jan@example.com",
            "subject": "Pytanie",
            "message": "Treść wiadomości testowej.",
        }
        self.client.post(self.url, dane)
        self.assertEqual(ContactMessage.objects.count(), 1)
        wiadomosc = ContactMessage.objects.first()
        self.assertEqual(wiadomosc.name, "Jan Kowalski")

    def test_formularz_bez_emaila_nie_zapisuje(self):
        dane = {"name": "Jan", "email": "", "subject": "Test", "message": "Treść."}
        self.client.post(self.url, dane)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_po_wyslaniu_redirect(self):
        dane = {
            "name": "Jan", "email": "jan@example.com",
            "subject": "Test", "message": "Treść."
        }
        response = self.client.post(self.url, dane)
        self.assertRedirects(response, self.url)


class SurveyViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.survey = Survey.objects.create(title="Ankieta testowa", is_active=True)
        self.question = Question.objects.create(
            survey=self.survey,
            text="Jak oceniasz sezón?",
            question_type=Question.TYPE_TEXT,
            order=1,
        )

    def test_ankieta_zwraca_200(self):
        url = reverse("contact:survey", args=[self.survey.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_wypelnienie_ankiety_zapisuje_odpowiedz(self):
        url = reverse("contact:survey", args=[self.survey.pk])
        dane = {
            "email": "",
            f"question_{self.question.pk}": "Bardzo dobrze!",
        }
        self.client.post(url, dane)
        self.assertEqual(SurveyResponse.objects.count(), 1)

    def test_nieaktywna_ankieta_zwraca_404(self):
        nieaktywna = Survey.objects.create(title="Zamknięta", is_active=False)
        url = reverse("contact:survey", args=[nieaktywna.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
```

```python
# documents/tests.py (cd.)
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Document, DocumentCategory


class DocumentViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        plik = SimpleUploadedFile("test.pdf", b"dane", content_type="application/pdf")
        self.doc = Document.objects.create(
            title="Regulamin sezonu 2025",
            description="Oficjalny regulamin",
            file=plik,
            is_active=True,
        )

    def test_lista_dokumentow_zwraca_200(self):
        url = reverse("documents:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_wyszukiwanie_po_tytule(self):
        url = reverse("documents:list") + "?q=Regulamin"
        response = self.client.get(url)
        self.assertContains(response, "Regulamin sezonu 2025")

    def test_wyszukiwanie_brak_wynikow(self):
        url = reverse("documents:list") + "?q=xyzxyz"
        response = self.client.get(url)
        self.assertNotContains(response, "Regulamin sezonu 2025")

    def test_nieaktywny_dokument_ukryty(self):
        plik2 = SimpleUploadedFile("ukryty.pdf", b"dane")
        Document.objects.create(title="Ukryty doc", file=plik2, is_active=False)
        url = reverse("documents:list")
        response = self.client.get(url)
        self.assertNotContains(response, "Ukryty doc")
```

📖 [Django test Client](https://docs.djangoproject.com/en/5.2/topics/testing/tools/#the-test-client) | [assertContains](https://docs.djangoproject.com/en/5.2/topics/testing/tools/#django.test.SimpleTestCase.assertContains)

---

## 5. Testy szablonów

Weryfikują, że szablony renderują się bez błędów i zawierają oczekiwane elementy.

```python
# news/tests.py (cd.)
class TemplateTest(TestCase):

    def test_strona_glowna_uzywa_szablonu(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_detail_zawiera_tytul_w_title(self):
        post = NewsPost.objects.create(
            title="Ważny komunikat",
            slug="wazny-komunikat",
            content="Treść.",
            is_published=True,
        )
        response = self.client.get(reverse("news:detail", args=["wazny-komunikat"]))
        self.assertContains(response, "Ważny komunikat")
```

---

## 6. Testy manualne — lista kontrolna

Przed każdym wdrożeniem na produkcję sprawdź ręcznie:

### Strona główna
- [ ] Hero sekcja wyświetla się poprawnie
- [ ] Wyróżnione posty pojawiają się w sekcji „Ważne komunikaty"
- [ ] Link „System obsad" otwiera zewnętrzną stronę w nowej karcie
- [ ] Nawigacja działa na mobile (hamburger menu)

### Aktualności
- [ ] Lista pokazuje tylko opublikowane posty
- [ ] Filtrowanie po kategorii działa
- [ ] Paginacja działa przy >10 postach
- [ ] Szczegóły posta pokazują treść z edytora (HTML renderuje się, nie wypisuje tagów)
- [ ] Post bez zdjęcia wyświetla się bez błędu

### Dokumenty
- [ ] Wyszukiwarka filtruje po tytule i opisie
- [ ] Przyciski „Pobierz" pobierają właściwy plik
- [ ] Nieaktywne dokumenty są ukryte
- [ ] Filtrowanie po kategorii działa

### Formularz kontaktowy
- [ ] Wysłanie pustego formularza pokazuje błędy walidacji
- [ ] Wysłanie z błędnym emailem pokazuje błąd
- [ ] Poprawne wysłanie tworzy wpis w panelu admina (`/admin/contact/contactmessage/`)
- [ ] Po wysłaniu pojawia się komunikat potwierdzający

### Ankiety
- [ ] Aktywna ankieta pojawia się na stronie kontaktowej
- [ ] Wypełnienie i wysłanie tworzy odpowiedź w panelu admina
- [ ] Ankieta z datą zamknięcia w przeszłości przekierowuje z komunikatem

### Panel admina
- [ ] Niezalogowany użytkownik nie ma dostępu do `/admin/`
- [ ] Slug wypełnia się automatycznie przy wpisywaniu tytułu
- [ ] Upload zdjęcia w poście działa
- [ ] Upload pliku do dokumentu działa

---

## 7. Model CI/CD z GitHub Actions

### Założenia

| Zdarzenie | Akcja |
|---|---|
| `push` na dowolną gałąź | Uruchom testy, linter |
| `pull request` do `main` | Testy + linter + blokada merge przy błędzie |
| `push` na `main` | Testy + automatyczny deployment |

### Plik pipeline: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Pobierz kod
        uses: actions/checkout@v4

      - name: Ustaw Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Zainstaluj zależności
        run: pip install -r requirements.txt

      - name: Sprawdź styl kodu (flake8)
        run: |
          pip install flake8
          flake8 . --max-line-length=120 --exclude=migrations,staticfiles

      - name: Sprawdź konfigurację Django
        run: python manage.py check
        env:
          DJANGO_SECRET_KEY: "ci-test-key-not-for-production"

      - name: Uruchom migracje (test DB)
        run: python manage.py migrate
        env:
          DJANGO_SECRET_KEY: "ci-test-key-not-for-production"

      - name: Uruchom testy
        run: python manage.py test --verbosity=2
        env:
          DJANGO_SECRET_KEY: "ci-test-key-not-for-production"
```

### Plik pipeline: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: []   # tutaj dodaj job "test" gdy będzie gotowy

    steps:
      - name: Pobierz kod
        uses: actions/checkout@v4

      - name: Deploy na serwer (SSH)
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /var/www/szps_website
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate --noinput
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn
```

> Sekrety (`SERVER_HOST`, `SERVER_SSH_KEY` itp.) ustawiasz w:
> **GitHub → repo → Settings → Secrets and variables → Actions**

📖 [GitHub Actions](https://docs.github.com/en/actions) | [appleboy/ssh-action](https://github.com/appleboy/ssh-action)

---

## 8. Uruchamianie testów lokalnie

```bash
# Aktywuj środowisko wirtualne
source venv/bin/activate

# Wszystkie testy
python manage.py test

# Testy jednej aplikacji
python manage.py test news
python manage.py test contact

# Testy z większą szczegółowością
python manage.py test --verbosity=2

# Jeden konkretny test
python manage.py test news.tests.NewsPostTest.test_domyslnie_nieopublikowany

# Z raportem pokrycia kodu (wymaga: pip install coverage)
coverage run manage.py test
coverage report
coverage html          # otwórz htmlcov/index.html w przeglądarce
```

### Dodaj `coverage` do zależności deweloperskich

Utwórz plik `requirements-dev.txt`:
```
-r requirements.txt
coverage>=7.0
flake8>=7.0
```

Instalacja: `pip install -r requirements-dev.txt`

---

## 9. Co dalej — kolejne etapy

### Etap 1 — Fundament (teraz)
- [ ] Napisać testy jednostkowe dla modeli (sekcja 3)
- [ ] Napisać testy integracyjne dla widoków (sekcja 4)
- [ ] Dodać plik `.github/workflows/ci.yml`
- [ ] Uruchomić pipeline na GitHub

### Etap 2 — Jakość
- [ ] Osiągnąć pokrycie kodu testami ≥ 80% (`coverage report`)
- [ ] Dodać `flake8` lub `ruff` jako linter
- [ ] Dodać `pre-commit` — sprawdzanie kodu przed każdym commitem

### Etap 3 — Deployment
- [ ] Skonfigurować serwer produkcyjny (Nginx + Gunicorn)
- [ ] Przejść z SQLite na PostgreSQL
- [ ] Dodać plik `.github/workflows/deploy.yml`
- [ ] Ustawić sekrety w GitHub Actions

### Etap 4 — Monitoring (produkcja)
- [ ] Dodać [Sentry](https://sentry.io) — automatyczne zbieranie błędów
- [ ] Skonfigurować powiadomienia email przy błędach 500
- [ ] Dodać health-check endpoint (`/health/`)

---

*Dokument: maj 2026 | Django 5.2*
