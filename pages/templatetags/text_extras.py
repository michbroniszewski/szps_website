from html import unescape

from django import template
from django.template.defaultfilters import stringfilter
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
