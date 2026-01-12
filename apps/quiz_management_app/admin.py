from django.contrib import admin

from apps.quiz_management_app.models import Quiz, QuizQuestion


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0
    fields = ("question_title", "question_options", "answer", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at", "updated_at", "question_count")
    list_filter = ("created_at", "user")
    search_fields = ("title", "description", "video_url", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [QuizQuestionInline]

    def question_count(self, obj):
        return obj.questions.count()

    question_count.short_description = "Questions"


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "question_title_short", "created_at")
    list_filter = ("created_at", "quiz")
    search_fields = ("question_title", "quiz__title")
    readonly_fields = ("created_at", "updated_at")

    def question_title_short(self, obj):
        t = obj.question_title or ""
        return (t[:50] + "...") if len(t) > 50 else t

    question_title_short.short_description = "Question"