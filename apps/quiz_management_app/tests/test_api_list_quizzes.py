import pytest
from rest_framework import status

from apps.quiz_management_app.models import Quiz


@pytest.mark.django_db
class TestQuizListEndpoint:
    url = "/api/quizzes/"

    def test_requires_auth(self, api_client):
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_only_own_quizzes(self, auth_client, user, other_user):
        Quiz.objects.create(
            title="Mine",
            description="D",
            video_url="https://www.youtube.com/watch?v=1",
            user=user,
        )
        Quiz.objects.create(
            title="Not mine",
            description="D",
            video_url="https://www.youtube.com/watch?v=2",
            user=other_user,
        )

        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["title"] == "Mine"

    def test_empty_list(self, auth_client):
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == []