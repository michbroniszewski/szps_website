from html import unescape

from django import template
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.html import strip_tags

register = template.Library()


@register.filter
@stringfilter
def plaintext(value):
    """HTML → czysty tekst: usuwa tagi i dekoduje encje (&oacute;, &nbsp;…).

    Samo `striptags` zostawia encje, które autoescape zamienia potem
    w widoczne „&amp;oacute;”. Wynik jest zwykłym tekstem, więc Django
    i tak go poprawnie wyescapuje.
    """
    return unescape(strip_tags(value)).replace("\xa0", " ")


PRIVACY_POLICY_SLUG = "polityka-prywatnosci"


@register.simple_tag
def privacy_policy_url():
    """Adres polityki prywatności albo "" — dopóki strona nie jest
    opublikowana, linki do niej (stopka, zgoda RODO) się nie wyświetlają."""
    from pages.models import StaticPage

    if StaticPage.objects.filter(slug=PRIVACY_POLICY_SLUG, is_published=True).exists():
        return reverse("pages:static_page", args=[PRIVACY_POLICY_SLUG])
    return ""
