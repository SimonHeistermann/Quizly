import pytest

from apps.quiz_management_app.models import Quiz, QuizQuestion


@pytest.mark.django_db
class TestModels:
    def test_quiz_str(self, user):
        quiz = Quiz.objects.create(
            title="My Quiz",
            description="Desc",
            video_url="https://www.youtube.com/watch?v=abc123",
            user=user,
        )
        assert str(quiz) == f"My Quiz (#{quiz.pk})"

    def test_question_str(self, user):
        quiz = Quiz.objects.create(
            title="My Quiz",
            description="Desc",
            video_url="https://www.youtube.com/watch?v=abc123",
            user=user,
        )
        qq = QuizQuestion.objects.create(
            quiz=quiz,
            question_title="Q?",
            question_options=["A", "B", "C", "D"],
            answer="A",
        )
        assert str(qq) == f"Q{qq.pk} for Quiz#{quiz.pk}"