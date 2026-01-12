import pytest
from unittest.mock import patch
from rest_framework import status

from apps.quiz_management_app.models import Quiz, QuizQuestion
from apps.quiz_management_app.utils import QuizCreationError, InvalidYouTubeUrlError


@pytest.mark.django_db
class TestCreateQuizEndpoint:
    url = "/api/createQuiz/"

    def test_requires_auth(self, api_client):
        resp = api_client.post(self.url, {"url": "https://www.youtube.com/watch?v=abc"}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_url_returns_400(self, auth_client):
        resp = auth_client.post(self.url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "url" in resp.data

    @patch("apps.quiz_management_app.api.views.create_quiz_from_url")
    def test_non_youtube_returns_400(self, mocked_create, auth_client, user):
        mocked_create.side_effect = InvalidYouTubeUrlError("Not a YouTube URL.")
        resp = auth_client.post(self.url, {"url": "https://vimeo.com/123"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data["detail"] == "Only YouTube URLs are allowed."

    @patch("apps.quiz_management_app.api.views.create_quiz_from_url")
    def test_quiz_creation_error_returns_500(self, mocked_create, auth_client):
        mocked_create.side_effect = QuizCreationError("boom")
        resp = auth_client.post(self.url, {"url": "https://www.youtube.com/watch?v=abc"}, format="json")
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert resp.data["detail"] == "boom"

    @patch("apps.quiz_management_app.api.views.create_quiz_from_url")
    def test_success_returns_quiz_with_questions(self, mocked_create, auth_client, user):
        quiz = Quiz.objects.create(
            title="T",
            description="D",
            video_url="https://www.youtube.com/watch?v=abc",
            user=user,
        )
        QuizQuestion.objects.create(
            quiz=quiz,
            question_title="Q1?",
            question_options=["A", "B", "C", "D"],
            answer="A",
        )
        mocked_create.return_value = quiz

        resp = auth_client.post(self.url, {"url": "https://www.youtube.com/watch?v=abc"}, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["id"] == quiz.id
        assert resp.data["title"] == "T"
        assert isinstance(resp.data["questions"], list)
        assert len(resp.data["questions"]) == 1