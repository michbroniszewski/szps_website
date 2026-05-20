# Dokumentacja projektu — Wydział Sędziowski ŚZPS

> Zwięzły przewodnik po kodzie dla programisty uczącego się Django.
> Wersja: maj 2026 | Django 5.2 | Python 3.11+

---

## Spis treści

1. [Architektura projektu](#1-architektura-projektu)
2. [Struktura plików](#2-struktura-plików)
3. [Konfiguracja — `szps/settings.py`](#3-konfiguracja--szpssettingspy)
4. [Routing URL — `szps/urls.py`](#4-routing-url--szpsurlspy)
5. [Aplikacje i ich komponenty](#5-aplikacje-i-ich-komponenty)
   - [news — Aktualności](#51-news--aktualności)
   - [documents — Dokumenty](#52-documents--dokumenty)
   - [sponsors — Sponsorzy](#53-sponsors--sponsorzy)
   - [contact — Kontakt i ankiety](#54-contact--kontakt-i-ankiety)
6. [Szablony HTML](#6-szablony-html)
7. [Style CSS](#7-style-css)
8. [Panel administracyjny](#8-panel-administracyjny)
9. [Mapa zależności](#9-mapa-zależności)
10. [Jak dodać nową funkcję](#10-jak-dodać-nową-funkcję)
11. [Optymalizacje i wzorce wydajnościowe](#11-optymalizacje-i-wzorce-wydajnościowe)
12. [Przydatne linki do dokumentacji](#12-przydatne-linki-do-dokumentacji)

---

## 1. Architektura projektu

Projekt oparty jest na wzorcu **MVT (Model–View–Template)** — odpowiednik popularnego MVC:

```
Przeglądarka → URL dispatcher → View (logika) → Model (baza) → Template (HTML)
                                     ↑
                               Context processor
                               (zmienne globalne)
```

| Warstwa | Rola | Gdzie w kodzie |
|---|---|---|
| **Model** | Definicja struktury bazy danych | `*/models.py` |
| **View** | Logika biznesowa, odpowiedź HTTP | `*/views.py` |
| **Template** | Prezentacja HTML | `templates/**/*.html` |
| **URL** | Mapowanie adresów na widoki | `*/urls.py` |
| **Admin** | Automatyczny panel zarządzania | `*/admin.py` |
| **Form** | Walidacja danych z formularzy | `*/forms.py` |

📖 [Podstawy MVT w Django](https://docs.djangoproject.com/en/5.2/intro/overview/)

---

## 2. Struktura plików

```
szps_website/
│
├── manage.py                  # Narzędzie CLI do zarządzania projektem
│
├── szps/                      # Pakiet konfiguracyjny projektu
│   ├── settings.py            # Wszystkie ustawienia aplikacji
│   ├── urls.py                # Główny router URL (wejście dla wszystkich ścieżek)
│   ├── context_processors.py  # Zmienne dostępne we wszystkich szablonach
│   ├── wsgi.py                # Punkt wejścia dla serwerów WSGI (produkcja)
│   └── asgi.py                # Punkt wejścia dla serwerów ASGI (WebSocket)
│
├── news/                      # Aplikacja: Aktualności
│   ├── models.py              # NewsCategory, NewsPost
│   ├── views.py               # home(), news_list(), news_detail()
│   ├── urls.py                # /aktualnosci/
│   ├── urls_home.py           # / (strona główna)
│   └── admin.py               # Rejestracja w panelu admina
│
├── documents/                 # Aplikacja: Dokumenty
│   ├── models.py              # DocumentCategory, Document
│   ├── views.py               # document_list()
│   ├── urls.py                # /dokumenty/
│   └── admin.py
│
├── sponsors/                  # Aplikacja: Sponsorzy
│   ├── models.py              # Sponsor
│   ├── views.py               # sponsor_list()
│   ├── urls.py                # /sponsorzy/
│   └── admin.py
│
├── contact/                   # Aplikacja: Kontakt + Ankiety
│   ├── models.py              # ContactMessage, Survey, Question, Choice,
│   │                          #   SurveyResponse, Answer
│   ├── forms.py               # ContactForm, SurveyResponseForm
│   ├── views.py               # contact(), survey_detail(), survey_done()
│   ├── urls.py                # /kontakt/
│   └── admin.py
│
├── templates/                 # Wszystkie szablony HTML
│   ├── base.html              # Bazowy layout (header, footer, nav)
│   ├── home.html              # Strona główna
│   ├── news/
│   │   ├── list.html          # Lista aktualności
│   │   └── detail.html        # Pojedynczy artykuł
│   ├── documents/
│   │   └── list.html          # Archiwum dokumentów
│   ├── sponsors/
│   │   └── list.html          # Lista sponsorów
│   └── contact/
│       ├── contact.html       # Formularz kontaktowy
│       ├── survey.html        # Wypełnianie ankiety
│       └── survey_done.html   # Podziękowanie po ankiecie
│
├── static/
│   └── css/
│       ├── main.css           # Główny arkusz stylów
│       └── article.css        # Style treści artykułu (zachowany jako alias)
│
├── media/                     # Pliki uploadowane przez admina (zdjęcia, dokumenty)
├── requirements.txt           # Lista zależności Python
└── .env.example               # Przykładowe zmienne środowiskowe
```

---

## 3. Konfiguracja — `szps/settings.py`

### Kluczowe ustawienia

```python
BASE_DIR = Path(__file__).resolve().parent.parent
# Absolutna ścieżka do katalogu projektu — wszystkie inne ścieżki
# są względem niej. parent.parent = wychodzi z szps/ do szps_website/
```

```python
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-...")
# Klucz kryptograficzny do podpisywania sesji i tokenów CSRF.
# W produkcji ZAWSZE z zmiennej środowiskowej, nie z kodu!
```

```python
INSTALLED_APPS = [
    "django.contrib.admin",      # Panel /admin/
    "django.contrib.auth",       # System użytkowników i uprawnień
    "django.contrib.contenttypes",
    "django.contrib.sessions",   # Sesje (koszyk, logowanie)
    "django.contrib.messages",   # Flash messages (komunikaty po akcji)
    "django.contrib.staticfiles",
    "django_ckeditor_5",         # Edytor WYSIWYG w panelu admina
    "news", "documents", "sponsors", "contact",  # Nasze aplikacje
]
```

```python
TEMPLATES = [{
    "DIRS": [BASE_DIR / "templates"],  # Szukaj szablonów w /templates/
    "OPTIONS": {
        "context_processors": [
            ...
            "szps.context_processors.site_settings",  # Dodaje STAFFING_SYSTEM_URL
        ]
    }
}]
```

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# SQLite = jeden plik db.sqlite3. Produkcja → zmień na PostgreSQL:
# ENGINE: "django.db.backends.postgresql"
# + NAME, USER, PASSWORD, HOST, PORT
```

```python
LANGUAGE_CODE = "pl"
TIME_ZONE = "Europe/Warsaw"
# Interfejs admina po polsku, czas lokalny w bazie danych
```

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
# Pliki uploadowane (zdjęcia, PDFy) trafiają do katalogu media/
# W produkcji serwuje je Nginx, nie Django
```

```python
STAFFING_SYSTEM_URL = os.environ.get("STAFFING_SYSTEM_URL", "#")
# Adres zewnętrznego systemu obsad — ustawiany przez zmienną środowiskową
```

```python
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
# Domyślnie logi w konsoli. W produkcji ustaw np.:
#   DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

📖 [Pełna lista ustawień Django](https://docs.djangoproject.com/en/5.2/ref/settings/)

---

## 4. Routing URL — `szps/urls.py`

```python
urlpatterns = [
    path("admin/",       admin.site.urls),               # /admin/
    path("ckeditor5/",   include("django_ckeditor_5.urls")),  # upload zdjęć w edytorze
    path("aktualnosci/", include("news.urls", namespace="news")),
    path("dokumenty/",   include("documents.urls", namespace="documents")),
    path("sponsorzy/",   include("sponsors.urls", namespace="sponsors")),
    path("kontakt/",     include("contact.urls", namespace="contact")),
    path("",             include("news.urls_home")),      # Strona główna /
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
# Ostatnia linia: w trybie DEBUG Django serwuje pliki z media/
```

### Jak działa `include()` i `namespace`

`include("news.urls", namespace="news")` oznacza:
- Wszystkie URL z `news/urls.py` są dostępne pod prefiksem `/aktualnosci/`
- Namespace `"news"` pozwala odwoływać się do nich w szablonach jako `{% url 'news:list' %}` zamiast po nazwie — unika kolizji nazw między aplikacjami

```
Żądanie: GET /aktualnosci/mecz-ligowy/
  → szps/urls.py dopasowuje "aktualnosci/"
  → news/urls.py dopasowuje "<slug:slug>/"
  → wywołuje views.news_detail(request, slug="mecz-ligowy")
```

📖 [URL dispatcher](https://docs.djangoproject.com/en/5.2/topics/http/urls/) | [Namespaces](https://docs.djangoproject.com/en/5.2/topics/http/urls/#url-namespaces)

---

## 5. Aplikacje i ich komponenty

### 5.1 `news` — Aktualności

#### Modele (`news/models.py`)

```
NewsCategory          NewsPost
─────────────         ────────────────────────────
id (PK)           ←── category (FK, SET_NULL)
name                   id (PK)
slug (unique)          title
                       slug (unique)
                       summary
                       content        ← CKEditor5Field (HTML)
                       image          ← ImageField → media/news/images/
                       published_at   ← domyślnie timezone.now
                       created_at     ← auto_now_add (tylko przy tworzeniu)
                       updated_at     ← auto_now (przy każdym zapisie)
                       is_published   ← Bool, domyślnie False
                       is_pinned      ← Bool, wyróżniony post
```

**Ważne koncepty:**
- `SlugField` — URL-friendly wersja tytułu, np. `"Mecz ligowy"` → `"mecz-ligowy"` | [doc](https://docs.djangoproject.com/en/5.2/ref/models/fields/#slugfield)
- `ForeignKey(on_delete=SET_NULL)` — jeśli kategoria zostanie usunięta, post zostaje (kategoria = NULL) | [doc](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.ForeignKey.on_delete)
- `CKEditor5Field` — pole tekstowe z edytorem WYSIWYG, zapisuje HTML | [django-ckeditor-5](https://github.com/hvlads/django-ckeditor-5)
- `ordering = ["-is_pinned", "-published_at"]` — minus oznacza DESC (malejąco)

#### Widoki (`news/views.py`)

```python
def home(request):
    # Pobiera max 3 wyróżnione posty i 6 najnowszych zwykłych.
    # select_related("category") pobiera kategorię razem z postem (JOIN),
    # zamiast wykonywać osobne zapytanie dla każdego posta z szablonu.
    pinned = (
        NewsPost.objects.filter(is_published=True, is_pinned=True)
        .select_related("category")[:3]
    )
    latest = (
        NewsPost.objects.filter(is_published=True, is_pinned=False)
        .select_related("category")[:6]
    )
```

```python
def news_list(request):
    # Obsługuje filtrowanie przez ?kategoria=slug i paginację przez ?strona=2.
    # QuerySet jest "leniwy" — zapytanie do bazy dopiero przy renderowaniu.
    posts = NewsPost.objects.filter(is_published=True).select_related("category")
    paginator = Paginator(posts, 10)        # 10 postów na stronę
    page = paginator.get_page(request.GET.get("strona"))
```

```python
def news_detail(request, slug):
    # get_object_or_404 → zwraca post lub odpowiedź HTTP 404.
    # select_related przekazany bezpośrednio do get_object_or_404 przez queryset.
    post = get_object_or_404(
        NewsPost.objects.select_related("category"),
        slug=slug, is_published=True
    )
    related = (
        NewsPost.objects.filter(is_published=True, category=post.category)
        .exclude(pk=post.pk)
        .select_related("category")[:3]
    )
```

📖 [QuerySet API](https://docs.djangoproject.com/en/5.2/ref/models/querysets/) | [Paginator](https://docs.djangoproject.com/en/5.2/topics/pagination/) | [get_object_or_404](https://docs.djangoproject.com/en/5.2/topics/http/shortcuts/#get-object-or-404)

#### URL (`news/urls.py` + `news/urls_home.py`)

| URL | Widok | Nazwa |
|---|---|---|
| `/` | `home()` | `home` |
| `/aktualnosci/` | `news_list()` | `news:list` |
| `/aktualnosci/<slug>/` | `news_detail()` | `news:detail` |

Dwa pliki URL to celowe rozwiązanie: `urls_home.py` nie ma namespace, co pozwala używać `{% url 'home' %}` zamiast `{% url 'news:home' %}`.

---

### 5.2 `documents` — Dokumenty

#### Modele (`documents/models.py`)

```
DocumentCategory      Document
────────────────      ────────────────────────────
id (PK)           ←── category (FK, SET_NULL)
name                   id (PK)
slug (unique)          title
order                  description
                       file        ← FileField → media/documents/
                       uploaded_at ← auto_now_add
                       updated_at  ← auto_now
                       is_active   ← Bool

Metoda: Document.extension()
  → zwraca rozszerzenie pliku ("PDF", "DOCX" itd.)
  → używana w szablonie do kolorowania ikony
```

#### Widok (`documents/views.py`)

```python
def document_list(request):
    # Wyszukiwanie pełnotekstowe w tytule i opisie.
    # select_related("category") eliminuje N+1 przy iteracji w szablonie.
    base_qs = Document.objects.filter(is_active=True).select_related("category")
    base_qs = base_qs.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )
```

**`Q` objects** — pozwalają łączyć warunki przez `|` (OR) i `&` (AND).
Bez `Q` można tylko AND: `.filter(title=..., description=...)` | [doc](https://docs.djangoproject.com/en/5.2/topics/db/queries/#complex-lookups-with-q-objects)

`icontains` — wyszukiwanie bez uwzględnienia wielkości liter (`i` = case-insensitive).

W widoku domyślnym (grupowanie po kategoriach) wszystkie dokumenty pobierane są jednym zapytaniem, a podział na kategorie następuje w Pythonie — zamiast wykonywać osobne `filter()` dla każdej kategorii w pętli:

```python
# Jeden SELECT na wszystkie dokumenty
all_docs = list(base_qs)
# Grupowanie w Pythonie — bez dodatkowych zapytań do bazy
grouped = []
for cat in categories:
    docs = [d for d in all_docs if d.category_id == cat.pk]
    if docs:
        grouped.append({"category": cat, "documents": docs})
```

---

### 5.3 `sponsors` — Sponsorzy

#### Model (`sponsors/models.py`)

```python
class Sponsor(models.Model):
    TIER_CHOICES = [("gold", "Złoty"), ("silver", "Srebrny"), ...]
    tier = models.CharField(choices=TIER_CHOICES, default="partner")
```

`choices` — ogranicza wartości pola do listy i automatycznie generuje metodę `get_tier_display()` zwracającą czytelną nazwę (np. `"gold"` → `"Złoty"`). | [doc](https://docs.djangoproject.com/en/5.2/ref/models/fields/#choices)

#### Widok (`sponsors/views.py`)

```python
def sponsor_list(request):
    # Jeden SELECT na wszystkich sponsorów; grupowanie w Pythonie.
    # Poprzednie podejście wykonywało osobne zapytanie dla każdego tieru.
    all_sponsors = list(Sponsor.objects.filter(is_active=True))
    sponsors_by_tier = {}
    for tier_key, tier_label in Sponsor.TIER_CHOICES:
        group = [s for s in all_sponsors if s.tier == tier_key]
        if group:
            sponsors_by_tier[tier_label] = group
    # Efekt: {"Złoty": [...], "Srebrny": [...]}
    # Kolejność tierów zgodna z TIER_CHOICES
```

---

### 5.4 `contact` — Kontakt i ankiety

Najbardziej złożona aplikacja. Zawiera dwa niezależne podsystemy.

#### Modele (`contact/models.py`)

**Podsystem 1: Formularz kontaktowy**
```
ContactMessage
──────────────
name, email, subject, message  ← dane z formularza
created_at                     ← auto_now_add
is_read                        ← admin oznacza jako przeczytane
```

**Podsystem 2: Ankiety** — 5 powiązanych modeli:

```
Survey ──────────── Question ──────── Choice
  │                    │
  │                    └── TYPE_TEXT / TYPE_CHOICE / TYPE_YES_NO
  │
  └── SurveyResponse ── Answer ──┬── text_answer (dla TYPE_TEXT / TYPE_YES_NO)
                                  └── choice_answer FK→Choice (dla TYPE_CHOICE)
```

Diagram zależności:
```
Survey
  ↓ (1→N, CASCADE)
Question
  ↓ (1→N, CASCADE)
Choice

Survey
  ↓ (1→N, CASCADE)
SurveyResponse
  ↓ (1→N, CASCADE)
Answer ──FK→ Question
Answer ──FK→ Choice (nullable)
```

`CASCADE` = usunięcie rodzica usuwa wszystkie dzieci. | [doc](https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.CASCADE)

#### Formularze (`contact/forms.py`)

```python
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
```

`ModelForm` — automatycznie tworzy pola formularza na podstawie modelu. Metoda `form.save()` zapisuje dane do bazy. | [doc](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/)

```python
class SurveyResponseForm(forms.Form):
    def __init__(self, survey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for question in survey.questions.all():
            field_name = f"question_{question.pk}"
            # Dynamicznie dodaje pola w zależności od pytań ankiety
```

`forms.Form` (nie `ModelForm`) — forma dynamiczna, pola generowane programatycznie w `__init__`. | [doc](https://docs.djangoproject.com/en/5.2/topics/forms/)

#### Widoki (`contact/views.py`)

```python
def contact(request):
    if request.method == "POST":       # Formularz wysłany
        form = ContactForm(request.POST)
        if form.is_valid():            # Walidacja (wymagane pola, format email)
            form.save()                # Zapis do bazy
            messages.success(...)      # Flash message
            return redirect(...)       # PRG pattern: zapobiega podwójnemu wysłaniu
    else:                              # GET — wyświetl pusty formularz
        form = ContactForm()
```

**PRG Pattern** (Post/Redirect/Get) — po pomyślnym POST-cie robimy redirect zamiast renderować stronę. Zapobiega ponownemu wysłaniu formularza przy odświeżeniu. | [Wikipedia](https://en.wikipedia.org/wiki/Post/Redirect/Get)

```python
def survey_detail(request, pk):
    # prefetch_related pobiera pytania i ich opcje w 2 dodatkowych zapytaniach,
    # zamiast N zapytań (po jednym dla każdego pytania) przy budowie formularza.
    survey = get_object_or_404(
        Survey.objects.prefetch_related("questions__choices"),
        pk=pk, is_active=True
    )
    if survey.closes_at and survey.closes_at < timezone.now():
        # Sprawdza czy ankieta nie wygasła
        ...

    # Zapis odpowiedzi: najpierw SurveyResponse (nagłówek),
    # potem wszystkie Answer naraz przez bulk_create (1 INSERT zamiast N).
    resp = SurveyResponse.objects.create(survey=survey, ...)
    answers = []
    for question in survey.questions.all():
        answers.append(Answer(response=resp, question=question, ...))
    Answer.objects.bulk_create(answers)
```

**`prefetch_related`** vs **`select_related`**:
- `select_related` — relacje ForeignKey/OneToOne, używa SQL JOIN, pobiera w jednym zapytaniu
- `prefetch_related` — relacje wstecz (reverse FK) i M2M, używa osobnych SELECT + łączy w Pythonie

**`bulk_create`** — wstawia listę obiektów jednym `INSERT ... VALUES (...), (...), (...)` zamiast N osobnych `INSERT`. | [doc](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#bulk-create)

---

## 6. Szablony HTML

### Dziedziczenie szablonów

```
base.html          ← bazowy layout: header, nav, footer, <html>
    ├── home.html                  {% extends "base.html" %}
    ├── news/list.html             {% extends "base.html" %}
    ├── news/detail.html           {% extends "base.html" %}
    ├── documents/list.html        {% extends "base.html" %}
    ├── sponsors/list.html         {% extends "base.html" %}
    ├── contact/contact.html       {% extends "base.html" %}
    ├── contact/survey.html        {% extends "base.html" %}
    └── contact/survey_done.html   {% extends "base.html" %}
```

Każdy szablon dziecko definiuje bloki:
```html
{% block title %}Aktualności — ŚZPS{% endblock %}
{% block content %}
  <!-- zawartość strony -->
{% endblock %}
```

`base.html` zawiera `{% block content %}{% endblock %}` — placeholder wypełniany przez dzieci. | [doc](https://docs.djangoproject.com/en/5.2/ref/templates/language/#template-inheritance)

### Kluczowe tagi szablonów

| Tag | Użycie | Przykład |
|---|---|---|
| `{% url %}` | Generuje URL po nazwie | `{% url 'news:detail' post.slug %}` |
| `{% for %}` | Pętla | `{% for post in posts %}` |
| `{% if %}` | Warunek | `{% if post.image %}` |
| `{% include %}` | Wstawia inny szablon | `{% include "partials/card.html" %}` |
| `{% load static %}` | Ładuje tag `{% static %}` | `{% static 'css/main.css' %}` |
| `{% csrf_token %}` | Token bezpieczeństwa formularzy | wewnątrz `<form>` |
| `{% now "Y" %}` | Aktualny rok | w stopce copyright |
| `{{ var\|safe }}` | Wypisuje HTML bez escapowania | `{{ post.content\|safe }}` |
| `{{ var\|truncatechars:80 }}` | Skraca tekst | w podglądzie |
| `{{ var\|date:"d.m.Y" }}` | Formatowanie daty | `{{ post.published_at\|date:"d.m.Y" }}` |

📖 [Tagi szablonów](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/)

### Context processor (`szps/context_processors.py`)

```python
def site_settings(request):
    logo_url = _find_logo()
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    return {
        "STAFFING_SYSTEM_URL": getattr(settings, "STAFFING_SYSTEM_URL", "#"),
        "logo_exists": bool(logo_url),
        "logo_url": logo_url,
        "SITE_URL": site_url,
        "CANONICAL_URL": site_url + request.path,
    }
```

Funkcja zwracająca słownik — jej klucze są dostępne w **każdym** szablonie automatycznie (nie trzeba przekazywać z widoku). Zarejestrowana w `settings.py` → `TEMPLATES.OPTIONS.context_processors`. | [doc](https://docs.djangoproject.com/en/5.2/ref/templates/api/#writing-your-own-context-processors)

```python
@lru_cache(maxsize=1)
def _find_logo():
    # Cached after the first call — restart server to pick up a new logo file
    images_dir = Path(settings.BASE_DIR) / "static" / "images"
    for ext in ("png", "svg", "jpg", "jpeg", "webp"):
        for name in (f"logo.{ext}", f"szps.{ext}", f"herb.{ext}"):
            if (images_dir / name).exists():
                return f"/static/images/{name}"
    return None
```

`_find_logo` jest dekorowana przez `@lru_cache(maxsize=1)` — skanuje system plików tylko przy pierwszym wywołaniu, a wynik pamięta na cały czas działania procesu serwera. Bez cache'u każde żądanie HTTP wykonywałoby kilkanaście wywołań `Path.exists()`. | [doc](https://docs.python.org/3/library/functools.html#functools.lru_cache)

---

## 7. Style CSS

### Architektura CSS (`static/css/main.css`)

Plik oparty na **CSS Custom Properties (zmienne)**:

```css
:root {
  --clr-accent:    #c8a84b;    /* kolor akcentu — zmień tutaj, działa wszędzie */
  --font-heading:  'Oswald', sans-serif;
  --section-py:    5rem;        /* padding sekcji */
  --container-max: 1200px;
}
```

Zmiana kolorystu = edycja kilku linii w `:root`. | [MDN: CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)

### Struktura sekcji CSS

```
Reset & Base           → box-sizing, font, body
Tokens (:root)         → kolory, fonty, spacing
Buttons (.btn)         → .btn--primary, .btn--outline, .btn--ghost
Tags                   → .tag, .tag--accent
Header                 → .site-header, .nav-*, .logo-*
Hero                   → .hero, .hero__title, .hero__actions
Quick links            → .quick-links, .quick-link
Sections               → .section, .section--dark, .section-header
Cards                  → .card, .card--dark, .card__image, .card__body
Page hero              → .page-hero (nagłówki podstron)
Sidebar layout         → .layout-sidebar, .filter-box
News list              → .news-row (wiersz listy)
Article                → .article, .article__body (style treści)
Documents              → .doc-card, .doc-card__type
Sponsors               → .sponsor-tier, .sponsor-card
Contact & Forms        → .contact-layout, .form-field, .survey-*
Footer                 → .site-footer, .footer-grid
Responsive             → @media max-width: 1024px, 768px, 480px
```

---

## 8. Panel administracyjny

Dostępny pod `/admin/`. Każdy model jest zarejestrowany z klasą `ModelAdmin`.

### Kluczowe opcje `ModelAdmin`

```python
@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display   = [...]   # kolumny na liście
    list_filter    = [...]   # panel filtrów po prawej
    search_fields  = [...]   # pole wyszukiwania (icontains)
    list_editable  = [...]   # edycja inline na liście (np. checkbox)
    prepopulated_fields = {"slug": ("title",)}  # auto-wypełnianie slug z tytułu
    date_hierarchy = "published_at"  # nawigacja po dacie
    readonly_fields = [...]  # pola tylko do odczytu
    fieldsets = [...]        # grupowanie pól w sekcje
```

### Inline Admin (contact)

```python
class ChoiceInline(admin.TabularInline):
    model = Choice    # edycja opcji odpowiedzi wewnątrz formularza pytania

class QuestionInline(admin.StackedInline):
    model = Question  # edycja pytań wewnątrz formularza ankiety
```

`TabularInline` = poziomy układ | `StackedInline` = pionowy układ | [doc](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#inlinemodeladmin-objects)

### Niestandardowa metoda na liście

```python
def response_count(self, obj):
    return obj.responses.count()  # obj = instancja Survey
response_count.short_description = "Odpowiedzi"  # nagłówek kolumny
```

📖 [ModelAdmin reference](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/)

---

## 9. Mapa zależności

```
szps/settings.py
    └── INSTALLED_APPS → rejestruje: news, documents, sponsors, contact
    └── TEMPLATES.context_processors → szps/context_processors.py

szps/urls.py
    ├── include("news.urls")        → news/views.py → news/models.py
    ├── include("documents.urls")   → documents/views.py → documents/models.py
    ├── include("sponsors.urls")    → sponsors/views.py → sponsors/models.py
    ├── include("contact.urls")     → contact/views.py → contact/models.py
    │                                                   → contact/forms.py
    └── include("news.urls_home")   → news/views.py (home)

Wszystkie widoki:
    └── render(request, "template.html", context)
            └── base.html + {{ STAFFING_SYSTEM_URL }} z context_processor
```

### Schemat bazy danych

```
NewsCategory ←── NewsPost
                   (image → media/news/images/)

DocumentCategory ←── Document
                       (file → media/documents/)

Sponsor
  (logo → media/sponsors/logos/)

Survey ──→ Question ──→ Choice
  │
  └──→ SurveyResponse ──→ Answer ──→ Question
                                └──→ Choice (nullable)

ContactMessage  (niezależny)
```

---

## 10. Jak dodać nową funkcję

### Przykład: nowa podstrona "Regulaminy"

1. **Stwórz aplikację** (lub dodaj do istniejącej):
   ```bash
   python manage.py startapp regulations
   ```

2. **Zdefiniuj model** (`regulations/models.py`):
   ```python
   class Regulation(models.Model):
       title = models.CharField(max_length=300)
       ...
   ```

3. **Zarejestruj w settings.py**:
   ```python
   INSTALLED_APPS = [..., "regulations"]
   ```

4. **Stwórz migrację** (aktualizuje schemat bazy):
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Napisz widok** (`regulations/views.py`):
   ```python
   def regulation_list(request):
       items = Regulation.objects.all()
       return render(request, "regulations/list.html", {"items": items})
   ```

6. **Dodaj URL** (`regulations/urls.py` + `szps/urls.py`):
   ```python
   # regulations/urls.py
   urlpatterns = [path("", views.regulation_list, name="list")]

   # szps/urls.py
   path("regulaminy/", include("regulations.urls", namespace="regulations"))
   ```

7. **Stwórz szablon** (`templates/regulations/list.html`):
   ```html
   {% extends "base.html" %}
   {% block content %}...{% endblock %}
   ```

8. **Zarejestruj w admin** (`regulations/admin.py`):
   ```python
   @admin.register(Regulation)
   class RegulationAdmin(admin.ModelAdmin):
       list_display = ["title"]
   ```

---

## 11. Optymalizacje i wzorce wydajnościowe

### Problem N+1

N+1 to klasyczny błąd ORM: pętla wykonuje jedno dodatkowe zapytanie do bazy **dla każdego** elementu listy. Przykład:

```python
# ŹLE — każde post.category w szablonie → osobny SELECT
posts = NewsPost.objects.filter(is_published=True)

# DOBRZE — JOIN pobiera kategorie razem z postami, 1 zapytanie
posts = NewsPost.objects.filter(is_published=True).select_related("category")
```

| Wzorzec | Kiedy używać | Efekt |
|---|---|---|
| `select_related("fk_field")` | ForeignKey, OneToOne | SQL JOIN — 1 zapytanie |
| `prefetch_related("reverse_fk")` | reverse FK, ManyToMany | 2 zapytania + Python join |
| `list(qs)` + Python grouping | grupowanie po kolumnie | 1 SELECT zamiast N |
| `bulk_create(objects)` | wiele INSERT-ów naraz | 1 INSERT zamiast N |

### Cachowanie w procesie (`lru_cache`)

Dla danych, które nie zmieniają się w trakcie działania serwera (np. ścieżka do logo), używamy `@lru_cache` z biblioteki standardowej:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def _find_logo():
    # Skanuje dysk tylko raz — wynik jest zapamiętany do restartu serwera
    ...
```

Uwaga: `lru_cache` pamięta wynik dla danego zestawu argumentów. Zrestartuj serwer po zmianie pliku logo.

### Zmienne środowiskowe

Wszystkie wartości zależne od środowiska (klucz tajny, adresy e-mail, hosty) pobierane są przez `os.environ.get()`:

```python
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
```

Plik `.env.example` zawiera pełną listę zmiennych z przykładowymi wartościami — skopiuj go do `.env` i uzupełnij przed uruchomieniem.

---

## 12. Przydatne linki do dokumentacji

### Django

| Temat | Link |
|---|---|
| Tutorial (od zera) | https://docs.djangoproject.com/en/5.2/intro/tutorial01/ |
| Models i pola | https://docs.djangoproject.com/en/5.2/ref/models/fields/ |
| QuerySet API | https://docs.djangoproject.com/en/5.2/ref/models/querysets/ |
| Views — skróty | https://docs.djangoproject.com/en/5.2/topics/http/shortcuts/ |
| Formularze | https://docs.djangoproject.com/en/5.2/topics/forms/ |
| Szablony | https://docs.djangoproject.com/en/5.2/ref/templates/language/ |
| Admin | https://docs.djangoproject.com/en/5.2/ref/contrib/admin/ |
| Pliki statyczne | https://docs.djangoproject.com/en/5.2/howto/static-files/ |
| Media (upload) | https://docs.djangoproject.com/en/5.2/topics/files/ |
| Migracje | https://docs.djangoproject.com/en/5.2/topics/migrations/ |
| Deployment checklist | https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/ |

### Pakiety użyte w projekcie

| Pakiet | Dokumentacja |
|---|---|
| django-ckeditor-5 | https://github.com/hvlads/django-ckeditor-5 |
| Pillow (obrazy) | https://pillow.readthedocs.io/ |

### CSS / Frontend

| Temat | Link |
|---|---|
| CSS Custom Properties | https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties |
| CSS Grid | https://css-tricks.com/snippets/css/complete-guide-grid/ |
| CSS Flexbox | https://css-tricks.com/snippets/css/a-guide-to-flexbox/ |
| Google Fonts — Oswald | https://fonts.google.com/specimen/Oswald |

---

*Dokumentacja wygenerowana: maj 2026*
