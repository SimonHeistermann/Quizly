import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.quiz_management_app.models import Quiz, QuizQuestion

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="u1",
        email="u1@example.com",
        password="Password123!",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="u2",
        email="u2@example.com",
        password="Password123!",
    )


@pytest.fixture
def auth_client(api_client, user):
    """
    Uses force_authenticate so we don't depend on JWT cookies in unit tests.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def quiz(db, user):
    return Quiz.objects.create(
        title="Quiz 1",
        description="Desc 1",
        video_url="https://www.youtube.com/watch?v=abc123",
        user=user,
    )


@pytest.fixture
def quiz_with_questions(db, user):
    q = Quiz.objects.create(
        title="Quiz With Qs",
        description="Desc",
        video_url="https://www.youtube.com/watch?v=abc123",
        user=user,
    )
    QuizQuestion.objects.create(
        quiz=q,
        question_title="Q1?",
        question_options=["A", "B", "C", "D"],
        answer="A",
    )
    QuizQuestion.objects.create(
        quiz=q,
        question_title="Q2?",
        question_options=["A1", "B1", "C1", "D1"],
        answer="B1",
    )
    return q