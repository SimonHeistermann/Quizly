import pytest
from django.contrib.admin.sites import AdminSite

from apps.quiz_management_app.admin import QuizAdmin, QuizQuestionAdmin
from apps.quiz_management_app.models import Quiz, QuizQuestion


@pytest.mark.django_db
class TestAdmin:
    def test_quiz_admin_question_count(self, quiz_with_questions):
        site = AdminSite()
        qa = QuizAdmin(Quiz, site)
        assert qa.question_count(quiz_with_questions) == 2

    def test_question_admin_title_short_under_50(self, quiz_with_questions):
        site = AdminSite()
        q_admin = QuizQuestionAdmin(QuizQuestion, site)

        q = quiz_with_questions.questions.first()
        assert q_admin.question_title_short(q) == "Q1?"

    def test_question_admin_title_short_over_50(self, quiz_with_questions):
        site = AdminSite()
        q_admin = QuizQuestionAdmin(QuizQuestion, site)

        q = quiz_with_questions.questions.first()
        q.question_title = "X" * 60
        q.save()

        short = q_admin.question_title_short(q)
        assert short.endswith("...")
        assert len(short) == 53  # 50 + "..."