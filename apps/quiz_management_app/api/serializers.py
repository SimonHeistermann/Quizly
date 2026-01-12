from rest_framework import serializers

from apps.quiz_management_app.models import Quiz, QuizQuestion



class StrictModelSerializer(serializers.ModelSerializer):
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
    For PATCH on /quizzes/{id}/: only allow updating title/description.
    """

    class Meta:
        model = Quiz
        fields = ["title", "description"]


class CreateQuizRequestSerializer(serializers.Serializer):
    """
    Request body for POST /createQuiz/
    """
    url = serializers.URLField()