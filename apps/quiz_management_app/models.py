from django.conf import settings
from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} (#{self.pk})"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_title = models.CharField(max_length=255)
    question_options = models.JSONField()
    answer = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        quiz_id = getattr(self, "quiz_id", None)
        return f"Q{self.pk} for Quiz#{quiz_id}"