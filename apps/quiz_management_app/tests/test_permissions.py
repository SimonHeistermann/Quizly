import pytest
from types import SimpleNamespace

from apps.quiz_management_app.api.permissions import IsQuizOwner


@pytest.mark.django_db
class TestIsQuizOwner:
    def test_allows_owner(self, user):
        perm = IsQuizOwner()
        req = SimpleNamespace(user=user)
        obj = SimpleNamespace(user_id=user.id)
        assert perm.has_object_permission(req, None, obj) is True

    def test_denies_other_user(self, user, other_user):
        perm = IsQuizOwner()
        req = SimpleNamespace(user=other_user)
        obj = SimpleNamespace(user_id=user.id)
        assert perm.has_object_permission(req, None, obj) is False