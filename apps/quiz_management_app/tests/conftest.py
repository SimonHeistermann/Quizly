"""
Pytest fixtures for the quiz management app test suite.

Provides common test utilities such as:
- DRF API client instances (authenticated and unauthenticated)
- test users
- sample quizzes and quizzes with related questions
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.quiz_management_app.models import Quiz, QuizQuestion

User = get_user_model()


@pytest.fixture
def api_client():
    """
    Return a plain DRF APIClient without authentication.
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Create and return a default test user.
    """
    return User.objects.create_user(
        username="u1",
        email="u1@example.com",
        password="Password123!",
    )


@pytest.fixture
def other_user(db):
    """
    Create and return a second test user.
    """
    return User.objects.create_user(
        username="u2",
        email="u2@example.com",
        password="Password123!",
    )


@pytest.fixture
def auth_client(api_client, user):
    """
    Return an APIClient authenticated as the default user.

    Uses force_authenticate so we don't depend on JWT cookies in unit tests.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def quiz(db, user):
    """
    Create and return a quiz owned by the default user.
    """
    return Quiz.objects.create(
        title="Quiz 1",
        description="Desc 1",
        video_url="https://www.youtube.com/watch?v=abc123",
        user=user,
    )


@pytest.fixture
def quiz_with_questions(db, user):
    """
    Create and return a quiz with two related questions.
    """
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