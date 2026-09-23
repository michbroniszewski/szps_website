import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from documents.models import Document, DocumentCategory

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
    page = get_object_or_404(StaticPage, slug=slug, is_published=True)
    return render(request, "pages/static_page.html", {"page": page})


# ── Formularz kontaktowy ─────────────────────────────────────────────
# JS wysyła POST z formularza kontaktowego na home.
# Zwracamy JSON, JS pokazuje ekran "Dziękujemy" bez przeładowania strony.

_TOPIC_CHOICES = {
    "Obsady i delegacje",
    "Szkolenia i egzaminy",
    "Sprawy organizacyjne",
    "Współpraca / sponsoring",
    "Inne",
}


def _validate_contact(post) -> tuple[dict, dict]:
    """Walidacja server-side (JS ma swoją, ale jej nie ufamy).
    Zwraca (dane, errors)."""
    data = {
        "name": post.get("name", "").strip(),
        "email": post.get("email", "").strip(),
        "topic": post.get("topic", "").strip(),
        "message": post.get("message", "").strip(),
        "consent": post.get("consent") in {"on", "true", "1"},
    }
    errors = {}
    if len(data["name"]) < 3:
        errors["name"] = "Podaj imię i nazwisko."
    if "@" not in data["email"] or "." not in data["email"].split("@")[-1]:
        errors["email"] = "Podaj poprawny adres e-mail."
    if data["topic"] not in _TOPIC_CHOICES:
        errors["topic"] = "Wybierz temat z listy."
    if len(data["message"]) < 10:
        errors["message"] = "Wiadomość jest zbyt krótka (min. 10 znaków)."
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
    return JsonResponse({"ok": True})
