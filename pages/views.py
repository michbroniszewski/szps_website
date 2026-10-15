import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from documents.models import Document, DocumentCategory
from evaluation.models import RateLimitHit
from evaluation.ratelimit import is_limited, record

from .models import Article, StaticPage

log = logging.getLogger(__name__)


def home(request):
    articles = Article.objects.filter(is_published=True)[:6]
    doc_categories = DocumentCategory.objects.prefetch_related(
        Prefetch(
            "documents",
            queryset=Document.objects.filter(is_published=True),
        )
    )
    return render(
        request,
        "pages/home.html",
        {
            "articles": articles,
            "doc_categories": doc_categories,
            "active_nav": "home",
        },
    )


def article_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(
        request,
        "pages/article_list.html",
        {"articles": articles, "active_nav": "aktualnosci"},
    )


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, "pages/article_detail.html", {"article": article})


def static_page(request, slug):
    # Redaktorzy widzą też szkice (np. politykę prywatności przed publikacją);
    # dla pozostałych nieopublikowana strona nie istnieje.
    pages = StaticPage.objects.all() if request.user.is_staff else StaticPage.objects.filter(is_published=True)
    page = get_object_or_404(pages, slug=slug)
    return render(request, "pages/static_page.html", {"page": page})


# ── Formularz kontaktowy ─────────────────────────────────────────────
# JS wysyła POST z formularza kontaktowego na home.
# Zwracamy JSON, JS pokazuje ekran "Dziękujemy" bez przeładowania strony.

TOPIC_MIN, TOPIC_MAX = 3, 120
NAME_MIN, NAME_MAX = 3, 200
MESSAGE_MIN, MESSAGE_MAX = 10, 10000


def _validate_contact(post) -> tuple[dict, dict]:
    """Walidacja server-side (JS ma swoją, ale jej nie ufamy).
    Zwraca (dane, errors)."""
    data = {
        "name": post.get("name", "").strip(),
        "email": post.get("email", "").strip(),
        # Temat trafia do nagłówka Subject — scalamy białe znaki (w tym
        # nowe linie), bo Django odrzuca wieloliniowe nagłówki maila.
        "topic": " ".join(post.get("topic", "").split()),
        "message": post.get("message", "").strip(),
        "consent": post.get("consent") in {"on", "true", "1"},
    }
    errors = {}
    if not NAME_MIN <= len(data["name"]) <= NAME_MAX:
        errors["name"] = "Podaj imię i nazwisko."
    try:
        # Adres trafia do nagłówka Reply-To — walidator Django odrzuca też
        # nowe linie i inne znaki, które mogłyby go zepsuć.
        validate_email(data["email"])
    except ValidationError:
        errors["email"] = "Podaj poprawny adres e-mail."
    if not TOPIC_MIN <= len(data["topic"]) <= TOPIC_MAX:
        errors["topic"] = f"Wpisz temat ({TOPIC_MIN}–{TOPIC_MAX} znaków)."
    if len(data["message"]) < MESSAGE_MIN:
        errors["message"] = f"Wiadomość jest zbyt krótka (min. {MESSAGE_MIN} znaków)."
    elif len(data["message"]) > MESSAGE_MAX:
        errors["message"] = f"Wiadomość jest zbyt długa (maks. {MESSAGE_MAX} znaków)."
    if not data["consent"]:
        errors["consent"] = "Zgoda RODO jest wymagana."
    return data, errors


@require_POST
def contact_submit(request):
    # Honeypot: pole `website` niewidoczne dla ludzi; jeśli wypełnione,
    # to bot — cicho udajemy sukces, żeby nie zdradzać, że wykryliśmy.
    if request.POST.get("website"):
        return JsonResponse({"ok": True})

    data, errors = _validate_contact(request.POST)
    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    # Limit na IP — bez niego formularz pozwala zasypać skrzynkę Wydziału.
    if is_limited(RateLimitHit.CONTACT, request, settings.CONTACT_SEND_LIMIT):
        return JsonResponse({"ok": False, "error": "rate_limited"}, status=429)

    body = (
        f"Imię i nazwisko: {data['name']}\n"
        f"E-mail: {data['email']}\n"
        f"Temat: {data['topic']}\n\n"
        f"{data['message']}\n"
    )
    msg = EmailMessage(
        subject=f"[Formularz WWW] {data['topic']}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_RECIPIENT],
        reply_to=[data["email"]],
    )
    try:
        msg.send(fail_silently=False)
    except Exception:
        log.exception("Nie udało się wysłać wiadomości z formularza kontaktowego")
        return JsonResponse(
            {"ok": False, "error": "send_failed"}, status=502
        )
    record(RateLimitHit.CONTACT, request)
    return JsonResponse({"ok": True})
