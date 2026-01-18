"""
Database models for the quiz management app.

This module defines the core domain entities:
- Quiz: a quiz generated from a YouTube video for a specific user.
- QuizQuestion: a single multiple-choice question belonging to a quiz.
"""

from django.conf import settings
from django.db import models


class Quiz(models.Model):
    """
    Represents a generated quiz that belongs to a user.

    A quiz is created from a video URL and contains multiple related questions.
    """

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
        """
        Model configuration such as default ordering and useful indexes.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the quiz for admin/debugging.
        """
        return f"{self.title} (#{self.pk})"


class QuizQuestion(models.Model):
    """
    Represents a single multiple-choice question within a quiz.

    Stores four options as JSON and the correct answer as a string that matches
    one of the options.
    """

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
        """
        Model configuration such as default ordering.
        """

        ordering = ("id",)

    def __str__(self) -> str:
        """
        Return a human-readable representation of the question for admin/debugging.
        """
        quiz_id = getattr(self, "quiz_id", None)
        return f"Q{self.pk} for Quiz#{quiz_id}"