from django.contrib import admin
from .models import ContactMessage, Survey, Question, Choice, SurveyResponse, Answer


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["subject", "name", "email", "created_at", "is_read"]
    list_filter = ["is_read"]
    search_fields = ["name", "email", "subject", "message"]
    list_editable = ["is_read"]
    readonly_fields = ["name", "email", "subject", "message", "created_at"]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "created_at", "closes_at", "response_count"]
    list_filter = ["is_active"]
    search_fields = ["title", "description"]
    list_editable = ["is_active"]
    inlines = [QuestionInline]

    def response_count(self, obj):
        return obj.responses.count()
    response_count.short_description = "Odpowiedzi"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "survey", "question_type", "order", "is_required"]
    list_filter = ["question_type", "is_required", "survey"]
    inlines = [ChoiceInline]


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ["survey", "submitted_at", "respondent_email"]
    list_filter = ["survey"]
    readonly_fields = ["survey", "submitted_at", "respondent_email"]
