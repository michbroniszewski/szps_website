from django.db import models


class BoardMember(models.Model):
    """Członek wydziału sędziowskiego."""

    first_name = models.CharField("Imię", max_length=100)
    last_name = models.CharField("Nazwisko", max_length=100)
    role = models.CharField(
        "Funkcja",
        max_length=150,
        help_text="np. Przewodniczący, Sekretarz, Członek",
    )
    photo = models.ImageField("Zdjęcie", upload_to="board/", blank=True)
    email = models.EmailField("E-mail", blank=True)
    phone = models.CharField("Telefon", max_length=30, blank=True)
    bio = models.TextField("Krótki opis", blank=True)
    order = models.PositiveSmallIntegerField(
        "Kolejność",
        default=0,
        help_text="Niższa liczba = wyżej na liście.",
    )
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        ordering = ["order", "last_name", "first_name"]
        verbose_name = "Członek wydziału"
        verbose_name_plural = "Skład wydziału"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
