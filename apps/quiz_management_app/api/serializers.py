"""
Serializers for the quiz management app.

This module contains DRF serializers used to validate and transform request/response
payloads for quizzes and quiz questions.
"""

from rest_framework import serializers

from apps.quiz_management_app.models import Quiz, QuizQuestion


class StrictModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that rejects unexpected input fields.

    DRF normally ignores unknown fields in incoming data. This serializer enforces
    a strict contract by raising a ValidationError if the request includes fields
    that are not defined on the serializer.
    """

    def to_internal_value(self, data):
        allowed = set(self.fields.keys())
        received = set(data.keys())
        unexpected = received - allowed
        if unexpected:
            raise serializers.ValidationError(
                {"non_field_errors": [f"Unexpected fields: {', '.join(sorted(unexpected))}"]}
            )
        return super().to_internal_value(data)


class QuizQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for quiz questions.

    Exposes question content (title/options/answer) and audit timestamps.
    """

    class Meta:
        model = QuizQuestion
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for quizzes including nested, read-only quiz questions.

    The related questions are returned in the `questions` field and are not writable
    through this serializer.
    """

    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "video_url", "questions"]


class QuizUpdateSerializer(StrictModelSerializer):
    """
    Serializer for partial updates of a Quiz.

    Intended for PATCH on /quizzes/{id}/ and only allows updating `title` and
    `description`. Any unexpected fields are rejected via StrictModelSerializer.
    """

    class Meta:
        model = Quiz
        fields = ["title", "description"]


class CreateQuizRequestSerializer(serializers.Serializer):
    """
    Serializer for the request body of POST /createQuiz/.

    Validates the video URL used to generate a quiz.
    """

    url = serializers.URLField()