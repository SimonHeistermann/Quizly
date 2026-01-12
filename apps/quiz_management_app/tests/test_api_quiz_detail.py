import pytest
from rest_framework import status

from apps.quiz_management_app.models import Quiz


@pytest.mark.django_db
class TestQuizDetailEndpoint:
    def test_get_success(self, auth_client, quiz_with_questions):
        url = f"/api/quizzes/{quiz_with_questions.id}/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == quiz_with_questions.id
        assert len(resp.data["questions"]) == 2

    def test_get_not_found(self, auth_client):
        resp = auth_client.get("/api/quizzes/999999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.data["detail"].code == "not_found"

    def test_get_forbidden_other_owner(self, auth_client, other_user, quiz):
        auth_client.force_authenticate(user=other_user)
        resp = auth_client.get(f"/api/quizzes/{quiz.id}/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in resp.data

    def test_patch_allows_title_and_description_only(self, auth_client, quiz):
        resp = auth_client.patch(
            f"/api/quizzes/{quiz.id}/",
            {"title": "New", "description": "NewD"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["title"] == "New"
        assert resp.data["description"] == "NewD"

    def test_patch_rejects_unknown_fields(self, auth_client, quiz):
        resp = auth_client.patch(
            f"/api/quizzes/{quiz.id}/",
            {"video_url": "https://www.youtube.com/watch?v=hacked"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        quiz.refresh_from_db()
        assert "hacked" not in quiz.video_url

    def test_patch_forbidden_other_owner(self, auth_client, other_user, quiz):
        auth_client.force_authenticate(user=other_user)
        resp = auth_client.patch(f"/api/quizzes/{quiz.id}/", {"title": "Hacked"}, format="json")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_success(self, auth_client, quiz):
        resp = auth_client.delete(f"/api/quizzes/{quiz.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert resp.content == b""
        assert not Quiz.objects.filter(id=quiz.id).exists()

    def test_delete_forbidden_other_owner(self, auth_client, other_user, quiz):
        auth_client.force_authenticate(user=other_user)
        resp = auth_client.delete(f"/api/quizzes/{quiz.id}/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert Quiz.objects.filter(id=quiz.id).exists()