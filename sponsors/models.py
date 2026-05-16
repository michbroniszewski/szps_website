from django.db import models


class Sponsor(models.Model):
    TIER_CHOICES = [
        ("gold", "Złoty"),
        ("silver", "Srebrny"),
        ("bronze", "Brązowy"),
        ("partner", "Partner"),
    ]
    name = models.CharField("Nazwa sponsora", max_length=200)
    logo = models.ImageField("Logo", upload_to="sponsors/logos/", blank=True, null=True)
    website_url = models.URLField("Strona WWW", blank=True)
    description = models.TextField("Opis", blank=True)
    tier = models.CharField("Poziom", max_length=20, choices=TIER_CHOICES, default="partner")
    order = models.PositiveIntegerField("Kolejność", default=0)
    is_active = models.BooleanField("Aktywny", default=True)

    class Meta:
        verbose_name = "Sponsor"
        verbose_name_plural = "Sponsorzy"
        ordering = ["tier", "order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_tier_display()})"
