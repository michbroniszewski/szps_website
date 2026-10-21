import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from . import access, sheet
from .forms import EvaluationForm
from .models import RateLimitHit
from .ratelimit import is_limited, record

log = logging.getLogger(__name__)

# Pole-pułapka: ukryte przed ludźmi, wypełniają je boty. Nazwa celowo nie
# przypomina „website”/„email”, żeby nie wypełniło jej autouzupełnianie.
HONEYPOT = "ev_hp_field"


def _noindex(response):
    # Podstrona celowo niepodlinkowana — dodatkowo prosimy wyszukiwarki,
    # żeby jej nie indeksowały, gdyby adres gdzieś wyciekł.
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


def _send_email(data, pdf: bytes, filename: str):
    date = data["match_date"].strftime("%d.%m.%Y")
    if data.get("central_candidate"):
        variant = "Kandydat na szczebel centralny: tak"
    else:
        variant = f"Rekomendacja: {sheet.choice_label(sheet.RECOMMENDATIONS, data.get('recommendation'))}"
    msg = EmailMessage(
        subject=f"[Arkusz oceny] {data['referee_name']} — {data['teams']} ({date})",
        body=(
            f"Obserwator: {data['observer']}\n"
            f"Rozgrywki: {sheet.choice_label(sheet.COMPETITIONS, data['competition'])}\n"
            f"Mecz: {data['teams']} — {data['result']} ({date})\n"
            f"Oceniany: {data['referee_name']} "
            f"({sheet.choice_label(sheet.POSITIONS, data['position'])})\n"
            f"{variant}\n\n"
            "Arkusz w załączniku.\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.EVALUATION_EMAIL_RECIPIENTS,
        # Kopia dla obserwatora; odpowiedź z Wydziału trafi prosto do niego.
        cc=[data["observer_email"]] if data.get("observer_email") else [],
        reply_to=[data["observer_email"]] if data.get("observer_email") else [],
    )
    msg.attach(filename, pdf, "application/pdf")
    msg.send(fail_silently=False)


def _access_page(request):
    """Strona z kodem dostępu (zamiast arkusza, dopóki nie ma dostępu)."""
    error = None
    status = 200
    if not access.is_configured():
        error = "Arkusz jest chwilowo niedostępny. Skontaktuj się z Wydziałem Sędziowskim."
        status = 503
    elif request.method == "POST" and "access_code" in request.POST:
        if request.POST.get(HONEYPOT):
            return redirect("evaluation:form")
        if is_limited(RateLimitHit.CODE, request, settings.EVALUATION_CODE_ATTEMPT_LIMIT):
            error = "Zbyt wiele błędnych prób. Spróbuj ponownie za godzinę."
            status = 429
        elif access.code_matches(request.POST.get("access_code", "")):
            response = redirect("evaluation:form")
            access.grant(response)
            return response
        else:
            record(RateLimitHit.CODE, request)
            error = "Nieprawidłowy kod dostępu."
            status = 403
    elif request.method == "POST":
        # Wysłany arkusz bez ważnego dostępu (np. zmieniony kod) — odpowiedzi
        # zostają w wersji roboczej przeglądarki, wystarczy podać kod.
        error = "Podaj kod dostępu, aby kontynuować. Wpisane odpowiedzi są zapisane w tej przeglądarce."
        status = 403
    return _noindex(render(
        request, "evaluation/access.html",
        {"error": error, "configured": access.is_configured(), "honeypot": HONEYPOT},
        status=status,
    ))


@never_cache
def evaluation_form(request):
    if not access.has_access(request):
        return _access_page(request)

    if request.method == "POST":
        if request.POST.get(HONEYPOT):
            # Bot — udajemy sukces, nic nie generujemy ani nie wysyłamy.
            return redirect(reverse("evaluation:form") + "?wyslano=1")
        form = EvaluationForm(request.POST)
        sending = request.POST.get("action") == "email"
        if form.is_valid() and sending and is_limited(
            RateLimitHit.SEND, request, settings.EVALUATION_SEND_LIMIT
        ):
            messages.error(
                request,
                f"Przekroczono limit {settings.EVALUATION_SEND_LIMIT} wysyłek na godzinę. "
                "Pobierz PDF i wyślij go ręcznie albo spróbuj później.",
            )
        elif form.is_valid():
            # Import dopiero tu: jeśli na serwerze zabraknie reportlab (deploy
            # nie instaluje pakietów), padnie tylko generowanie PDF, a nie
            # start całej aplikacji przy imporcie urls.
            from .pdf import build_pdf, pdf_filename

            data = form.cleaned_data
            pdf = build_pdf(data)
            filename = pdf_filename(data)

            if sending:
                try:
                    _send_email(data, pdf, filename)
                except Exception:
                    log.exception("Nie udało się wysłać arkusza oceny")
                    messages.error(
                        request,
                        "Nie udało się wysłać e-maila. Pobierz PDF i wyślij go ręcznie.",
                    )
                else:
                    record(RateLimitHit.SEND, request)
                    messages.success(
                        request,
                        "Arkusz został wysłany do Wydziału Sędziowskiego"
                        + (f" (kopia: {data['observer_email']})." if data.get("observer_email") else "."),
                    )
                    # ?wyslano=1 → JS czyści zapisaną wersję roboczą.
                    return redirect(reverse("evaluation:form") + "?wyslano=1")
            else:
                response = HttpResponse(pdf, content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{filename}"'
                return _noindex(response)
    else:
        form = EvaluationForm()

    return _noindex(render(
        request,
        "evaluation/form.html",
        {
            "form": form,
            "elements": list(form.elements()),
            "grade_scale": sheet.GRADE_SCALE,
            "grade_rules": sheet.GRADE_RULES,
            "email_recipients": settings.EVALUATION_EMAIL_RECIPIENTS,
            "send_limit": settings.EVALUATION_SEND_LIMIT,
            "honeypot": HONEYPOT,
        },
    ))
