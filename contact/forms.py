from django import forms
from .models import ContactMessage, Survey, Question, Choice


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Imię i nazwisko"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "adres@email.pl"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Temat wiadomości"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Treść wiadomości"}),
        }
        labels = {
            "name": "Imię i nazwisko",
            "email": "Adres e-mail",
            "subject": "Temat",
            "message": "Wiadomość",
        }


class SurveyResponseForm(forms.Form):
    def __init__(self, survey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.survey = survey
        for question in survey.questions.all():
            field_name = f"question_{question.pk}"
            if question.question_type == Question.TYPE_TEXT:
                self.fields[field_name] = forms.CharField(
                    label=question.text,
                    required=question.is_required,
                    widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
                )
            elif question.question_type == Question.TYPE_CHOICE:
                choices = [(c.pk, c.text) for c in question.choices.all()]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    required=question.is_required,
                    widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                )
            elif question.question_type == Question.TYPE_YES_NO:
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    choices=[("tak", "Tak"), ("nie", "Nie")],
                    required=question.is_required,
                    widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                )

    email = forms.EmailField(
        label="Adres e-mail (opcjonalnie)",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "adres@email.pl"}),
    )
