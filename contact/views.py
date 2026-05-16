from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import ContactMessage, Survey, SurveyResponse, Answer, Question, Choice
from .forms import ContactForm, SurveyResponseForm


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Wiadomość została wysłana. Dziękujemy!")
            return redirect("contact:contact")
    else:
        form = ContactForm()
    active_surveys = Survey.objects.filter(is_active=True)
    return render(request, "contact/contact.html", {"form": form, "surveys": active_surveys})


def survey_detail(request, pk):
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    if survey.closes_at and survey.closes_at < timezone.now():
        messages.error(request, "Ta ankieta jest już zamknięta.")
        return redirect("contact:contact")

    if request.method == "POST":
        form = SurveyResponseForm(survey, request.POST)
        if form.is_valid():
            resp = SurveyResponse.objects.create(
                survey=survey,
                respondent_email=form.cleaned_data.get("email", ""),
            )
            for question in survey.questions.all():
                field_name = f"question_{question.pk}"
                value = form.cleaned_data.get(field_name, "")
                if question.question_type == Question.TYPE_TEXT:
                    Answer.objects.create(response=resp, question=question, text_answer=value)
                elif question.question_type == Question.TYPE_YES_NO:
                    Answer.objects.create(response=resp, question=question, text_answer=value)
                elif question.question_type == Question.TYPE_CHOICE:
                    try:
                        choice = Choice.objects.get(pk=int(value))
                        Answer.objects.create(response=resp, question=question, choice_answer=choice)
                    except (Choice.DoesNotExist, ValueError):
                        pass
            messages.success(request, "Dziękujemy za wypełnienie ankiety!")
            return redirect("contact:survey_done")
    else:
        form = SurveyResponseForm(survey)

    return render(request, "contact/survey.html", {"survey": survey, "form": form})


def survey_done(request):
    return render(request, "contact/survey_done.html")
