from django.db import models


class ContactMessage(models.Model):
    name = models.CharField("Imię i nazwisko", max_length=200)
    email = models.EmailField("Adres e-mail")
    subject = models.CharField("Temat", max_length=300)
    message = models.TextField("Wiadomość")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField("Przeczytana", default=False)

    class Meta:
        verbose_name = "Wiadomość kontaktowa"
        verbose_name_plural = "Wiadomości kontaktowe"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name}"


class Survey(models.Model):
    title = models.CharField("Tytuł ankiety", max_length=300)
    description = models.TextField("Opis", blank=True)
    is_active = models.BooleanField("Aktywna", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField("Zamknięcie", null=True, blank=True)

    class Meta:
        verbose_name = "Ankieta"
        verbose_name_plural = "Ankiety"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Question(models.Model):
    TYPE_TEXT = "text"
    TYPE_CHOICE = "choice"
    TYPE_YES_NO = "yesno"
    TYPE_CHOICES = [
        (TYPE_TEXT, "Odpowiedź tekstowa"),
        (TYPE_CHOICE, "Wybór spośród opcji"),
        (TYPE_YES_NO, "Tak / Nie"),
    ]
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions", verbose_name="Ankieta")
    text = models.CharField("Pytanie", max_length=500)
    question_type = models.CharField("Typ pytania", max_length=10, choices=TYPE_CHOICES, default=TYPE_TEXT)
    order = models.PositiveIntegerField("Kolejność", default=0)
    is_required = models.BooleanField("Wymagane", default=True)

    class Meta:
        verbose_name = "Pytanie"
        verbose_name_plural = "Pytania"
        ordering = ["order"]

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices", verbose_name="Pytanie")
    text = models.CharField("Opcja", max_length=300)
    order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        verbose_name = "Opcja odpowiedzi"
        verbose_name_plural = "Opcje odpowiedzi"
        ordering = ["order"]

    def __str__(self):
        return self.text


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses", verbose_name="Ankieta")
    submitted_at = models.DateTimeField(auto_now_add=True)
    respondent_email = models.EmailField("E-mail respondenta", blank=True)

    class Meta:
        verbose_name = "Odpowiedź na ankietę"
        verbose_name_plural = "Odpowiedzi na ankiety"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f'Odpowiedź #{self.pk} dla „{self.survey}”'


class Answer(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Pytanie")
    text_answer = models.TextField("Odpowiedź tekstowa", blank=True)
    choice_answer = models.ForeignKey(
        Choice, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Wybrana opcja"
    )

    class Meta:
        verbose_name = "Odpowiedź"
        verbose_name_plural = "Odpowiedzi"

    def __str__(self):
        return f"Odpowiedź na: {self.question}"
