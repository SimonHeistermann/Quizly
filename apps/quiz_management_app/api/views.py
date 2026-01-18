"""
API views for the quiz management app.

This module defines authenticated endpoints for creating quizzes from a video URL,
listing a user's quizzes, and retrieving, updating, or deleting individual quizzes.
"""

from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.quiz_management_app.models import Quiz
from apps.quiz_management_app.api.permissions import IsQuizOwner
from apps.quiz_management_app.utils import create_quiz_from_url, QuizCreationError, InvalidYouTubeUrlError
from .serializers import (
    CreateQuizRequestSerializer,
    QuizSerializer,
    QuizUpdateSerializer,
)


class CreateQuizView(CreateAPIView):
    """
    Create a new quiz from a provided video URL.

    The request must be authenticated and contain a valid YouTube URL.
    The quiz is generated asynchronously via internal utility logic and
    returned in serialized form upon success.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CreateQuizRequestSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests to create a quiz.

        Validates the request payload, attempts quiz creation, and maps
        domain-specific errors to appropriate HTTP responses.
        """

        req = self.get_serializer(data=request.data)
        req.is_valid(raise_exception=True)

        try:
            quiz = create_quiz_from_url(req.validated_data["url"], request.user)
        except InvalidYouTubeUrlError:
            return Response(
                {"detail": "Only YouTube URLs are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except QuizCreationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


class QuizListView(ListAPIView):
    """
    List all quizzes belonging to the authenticated user.

    Returns quizzes with their related questions preloaded for efficiency.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def get_queryset(self):
        """
        Return the queryset of quizzes owned by the current user.
        """

        return Quiz.objects.filter(user=self.request.user).prefetch_related("questions")


class QuizDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a single quiz.

    Access is restricted to the quiz owner. Updates use a restricted serializer
    to limit which fields can be modified.
    """

    permission_classes = [IsAuthenticated, IsQuizOwner]
    queryset = Quiz.objects.all().prefetch_related("questions")

    def get_serializer_class(self):
        """
        Return the appropriate serializer depending on the HTTP method.

        PATCH and PUT requests use a restricted update serializer, while
        read operations use the full quiz serializer.
        """

        if self.request.method in ("PATCH", "PUT"):
            return QuizUpdateSerializer
        return QuizSerializer