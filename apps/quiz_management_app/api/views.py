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
    permission_classes = [IsAuthenticated]
    serializer_class = CreateQuizRequestSerializer

    def create(self, request, *args, **kwargs):
        req = self.get_serializer(data=request.data)
        req.is_valid(raise_exception=True)

        try:
            quiz = create_quiz_from_url(req.validated_data["url"], request.user)
        except InvalidYouTubeUrlError:
            return Response({"detail": "Only YouTube URLs are allowed."}, status=status.HTTP_400_BAD_REQUEST)
        except QuizCreationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


class QuizListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def get_queryset(self):
        return Quiz.objects.filter(user=self.request.user).prefetch_related("questions")


class QuizDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsQuizOwner]
    queryset = Quiz.objects.all().prefetch_related("questions")

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return QuizUpdateSerializer
        return QuizSerializer