from django.db import models


class RateLimitHit(models.Model):
    """Jedno zdarzenie liczone do limitu (wysyłka arkusza, błędny kod).

    Licznik w bazie, a nie w cache: na hostingu aplikacja może działać
    w kilku procesach, a domyślny cache (LocMem) jest osobny dla każdego.
    Adres IP zapisujemy tylko jako skrót HMAC — do limitu wystarczy
    porównywanie, a pełny adres nie jest potrzebny.
    """

    SEND = "send"
    CODE = "code"
    KINDS = [(SEND, "Wysyłka arkusza"), (CODE, "Błędny kod dostępu")]

    kind = models.CharField(max_length=10, choices=KINDS)
    client = models.CharField("Skrót adresu IP", max_length=64)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["kind", "client", "created_at"])]
        verbose_name = "Zdarzenie limitu"
        verbose_name_plural = "Zdarzenia limitu"
