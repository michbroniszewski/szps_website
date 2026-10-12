import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from . import sheet
from .forms import EvaluationForm
from .pdf import build_pdf, pdf_filename

log = logging.getLogger(__name__)


def _noindex(response):
    # Podstrona celowo niepodlinkowana — dodatkowo prosimy wyszukiwarki,
    # żeby jej nie indeksowały, gdyby adres gdzieś wyciekł.
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


def _send_email(data, pdf: bytes, filename: str):
    date = data["match_date"].strftime("%d.%m.%Y")
    msg = EmailMessage(
        subject=f"[Arkusz ewaluacyjny] {data['referee_name']} — {data['teams']} ({date})",
        body=(
            f"Obserwator: {data['observer']}\n"
            f"Rozgrywki: {sheet.choice_label(sheet.COMPETITIONS, data['competition'])}\n"
            f"Mecz: {data['teams']} — {data['result']} ({date})\n"
            f"Oceniany: {data['referee_name']} "
            f"({sheet.choice_label(sheet.POSITIONS, data['position'])})\n\n"
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


@never_cache
def evaluation_form(request):
    if request.method == "POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            pdf = build_pdf(data)
            filename = pdf_filename(data)

            if request.POST.get("action") == "email":
                try:
                    _send_email(data, pdf, filename)
                except Exception:
                    log.exception("Nie udało się wysłać arkusza ewaluacyjnego")
                    messages.error(
                        request,
                        "Nie udało się wysłać e-maila. Pobierz PDF i wyślij go ręcznie.",
                    )
                else:
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
        },
    ))
