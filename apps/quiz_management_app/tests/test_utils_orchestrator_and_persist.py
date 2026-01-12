import pytest
from types import SimpleNamespace
from unittest.mock import patch

from apps.quiz_management_app.models import Quiz, QuizQuestion
from apps.quiz_management_app.utils import (
    InvalidYouTubeUrlError,
    QuizCreationError,
    create_quiz_from_url,
)


def _payload():
    return {
        "title": "Generated Title",
        "description": "Generated Desc",
        "questions": [
            {"question_title": f"Q{i}?", "question_options": ["A", "B", "C", "D"], "answer": "A"}
            for i in range(10)
        ],
    }


@pytest.mark.django_db
class TestCreateQuizFromUrl:
    def test_rejects_non_youtube_url(self, user):
        with pytest.raises(InvalidYouTubeUrlError):
            create_quiz_from_url("https://vimeo.com/123", user)

    @patch("apps.quiz_management_app.utils.download_audio_from_video")
    @patch("apps.quiz_management_app.utils.generate_transcript")
    @patch("apps.quiz_management_app.utils.get_ai_response")
    def test_success_persists_quiz_and_questions(
        self, mock_ai, mock_transcript, mock_dl, user
    ):
        mock_transcript.return_value = "transcript"
        mock_ai.return_value = SimpleNamespace(text='{"title":"Generated Title","description":"Generated Desc","questions":' + str(_payload()["questions"]).replace("'", '"') + "}")

        quiz = create_quiz_from_url("https://www.youtube.com/watch?v=abc123", user)

        assert Quiz.objects.filter(id=quiz.id).exists()
        assert QuizQuestion.objects.filter(quiz=quiz).count() == 10
        assert quiz.user_id == user.id

    @patch("apps.quiz_management_app.utils.download_audio_from_video")
    def test_download_error_becomes_quiz_creation_error(self, mock_dl, user):
        mock_dl.side_effect = QuizCreationError("download failed")
        with pytest.raises(QuizCreationError, match="download failed"):
            create_quiz_from_url("https://www.youtube.com/watch?v=abc123", user)