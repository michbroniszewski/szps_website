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
    return render(request, "contact/contact.html", {"form": form})


def surveys_list(request):
    active_surveys = Survey.objects.filter(is_active=True)
    return render(request, "contact/surveys.html", {"surveys": active_surveys})


def survey_detail(request, pk):
    # Prefetch questions and their choices to avoid N+1 in form building and answer saving
    survey = get_object_or_404(
        Survey.objects.prefetch_related("questions__choices"),
        pk=pk,
        is_active=True,
    )
    if survey.closes_at and survey.closes_at < timezone.now():
        messages.error(request, "Ta ankieta jest już zamknięta.")
        return redirect("surveys:list")

    if request.method == "POST":
        form = SurveyResponseForm(survey, request.POST)
        if form.is_valid():
            resp = SurveyResponse.objects.create(
                survey=survey,
                respondent_email=form.cleaned_data.get("email", ""),
            )
            # Collect all answers first, then insert in a single query
            answers = []
            choice_pks = []
            questions_needing_choice = []
            for question in survey.questions.all():
                field_name = f"question_{question.pk}"
                value = form.cleaned_data.get(field_name, "")
                if question.question_type in (Question.TYPE_TEXT, Question.TYPE_YES_NO):
                    answers.append(
                        Answer(response=resp, question=question, text_answer=value)
                    )
                elif question.question_type == Question.TYPE_CHOICE:
                    try:
                        choice_pks.append(int(value))
                        questions_needing_choice.append(question)
                    except (TypeError, ValueError):
                        pass

            if choice_pks:
                choices_by_pk = {
                    c.pk: c for c in Choice.objects.filter(pk__in=choice_pks)
                }
                for question, pk_val in zip(questions_needing_choice, choice_pks):
                    choice = choices_by_pk.get(pk_val)
                    if choice:
                        answers.append(
                            Answer(response=resp, question=question, choice_answer=choice)
                        )

            Answer.objects.bulk_create(answers)
            messages.success(request, "Dziękujemy za wypełnienie ankiety!")
            return redirect("surveys:done")
    else:
        form = SurveyResponseForm(survey)

    return render(request, "contact/survey.html", {"survey": survey, "form": form})


def survey_done(request):
    return render(request, "contact/survey_done.html")
