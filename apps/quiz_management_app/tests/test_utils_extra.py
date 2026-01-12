import json
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

import apps.quiz_management_app.utils as utils
from apps.quiz_management_app.models import Quiz, QuizQuestion


# -----------------------------------------------------------------------------
# Download / cleanup branches
# -----------------------------------------------------------------------------

def test_download_audio_from_video_on_error_cleans_up_and_raises_quizcreationerror():
    tmp = utils.TempAudio(base_path="/tmp/fake-audio")
    with (
        patch("apps.quiz_management_app.utils.yt_dlp.YoutubeDL") as ydl_cls,
        patch("apps.quiz_management_app.utils.cleanup_audio") as cleanup,
    ):
        ydl = MagicMock()
        ydl.download.side_effect = Exception("boom")
        ydl_cls.return_value.__enter__.return_value = ydl

        with pytest.raises(utils.QuizCreationError) as exc:
            utils.download_audio_from_video("https://youtube.com/watch?v=x", tmp)

        assert "Error downloading audio" in str(exc.value)
        cleanup.assert_called_once_with(tmp)


def test_cleanup_audio_calls_safe_remove_for_base_and_mp3():
    tmp = utils.TempAudio(base_path="/tmp/abc")
    with patch("apps.quiz_management_app.utils.safe_remove") as rm:
        utils.cleanup_audio(tmp)
        rm.assert_any_call("/tmp/abc")
        rm.assert_any_call("/tmp/abc.mp3")
        assert rm.call_count == 2


# -----------------------------------------------------------------------------
# Whisper caching + error handling branches
# -----------------------------------------------------------------------------

def test_get_whisper_model_caches_model_and_uses_settings_model_name(settings):
    utils._whisper_model = None
    settings.WHISPER_MODEL = "small"

    with patch("apps.quiz_management_app.utils.whisper.load_model") as load_model:
        fake_model = MagicMock()
        load_model.return_value = fake_model

        m1 = utils.get_whisper_model()
        m2 = utils.get_whisper_model()

        assert m1 is fake_model
        assert m2 is fake_model
        load_model.assert_called_once_with("small")


def test_generate_transcript_on_error_cleans_up_and_raises_quizcreationerror():
    tmp = utils.TempAudio(base_path="/tmp/abc")

    with (
        patch("apps.quiz_management_app.utils.get_whisper_model") as get_model,
        patch("apps.quiz_management_app.utils.cleanup_audio") as cleanup,
    ):
        model = MagicMock()
        model.transcribe.side_effect = Exception("whisper fail")
        get_model.return_value = model

        with pytest.raises(utils.QuizCreationError) as exc:
            utils.generate_transcript(tmp)

        assert "Error transcribing audio" in str(exc.value)
        cleanup.assert_called_once_with(tmp)


# -----------------------------------------------------------------------------
# Gemini client + JSON parsing branches
# -----------------------------------------------------------------------------

def test_gemini_client_missing_key_raises_quizcreationerror(settings):
    if hasattr(settings, "GEMINI_API_KEY"):
        delattr(settings, "GEMINI_API_KEY")

    with pytest.raises(utils.QuizCreationError) as exc:
        utils.gemini_client()

    assert "Missing GEMINI_API_KEY" in str(exc.value)


def test_extract_json_strips_leading_text_and_backticks():
    text = "Sure! ```json\n{ \"title\": \"x\" }\n```"
    extracted = utils.extract_json(text)
    assert extracted.startswith("{")
    assert "`" not in extracted


def test_parse_quiz_json_invalid_json_raises_quizcreationerror():
    with pytest.raises(utils.QuizCreationError) as exc:
        utils.parse_quiz_json("not-json at all")

    assert "Gemini returned invalid JSON" in str(exc.value)


# -----------------------------------------------------------------------------
# Validation negative branches (high value coverage)
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "x",
        123,
    ],
)
def test_validate_quiz_payload_rejects_non_dict(payload):
    with pytest.raises(utils.QuizCreationError):
        utils.validate_quiz_payload(payload)  # type: ignore[arg-type]


def test_validate_quiz_payload_rejects_missing_required_keys():
    with pytest.raises(utils.QuizCreationError) as exc:
        utils.validate_quiz_payload({"title": "t", "description": "d"})
    assert "missing required keys" in str(exc.value).lower()


def test_validate_quiz_payload_rejects_wrong_question_count():
    payload = {
        "title": "t",
        "description": "d",
        "questions": [{"question_title": "q", "question_options": ["a", "b", "c", "d"], "answer": "a"}],
    }
    with pytest.raises(utils.QuizCreationError) as exc:
        utils.validate_quiz_payload(payload)
    assert "exactly 10" in str(exc.value).lower()


def test_validate_question_rejects_empty_title():
    payload = {
        "title": "t",
        "description": "d",
        "questions": [
            {"question_title": "", "question_options": ["a", "b", "c", "d"], "answer": "a"}
            for _ in range(10)
        ],
    }
    with pytest.raises(utils.QuizCreationError) as exc:
        utils.validate_quiz_payload(payload)
    assert "non-empty question_title" in str(exc.value)


def test_validate_question_rejects_non_distinct_options():
    payload = {
        "title": "t",
        "description": "d",
        "questions": [
            {"question_title": "q", "question_options": ["a", "a", "c", "d"], "answer": "a"}
            for _ in range(10)
        ],
    }
    with pytest.raises(utils.QuizCreationError) as exc:
        utils.validate_quiz_payload(payload)
    assert "distinct" in str(exc.value).lower()


def test_validate_question_rejects_answer_not_in_options():
    payload = {
        "title": "t",
        "description": "d",
        "questions": [
            {"question_title": "q", "question_options": ["a", "b", "c", "d"], "answer": "x"}
            for _ in range(10)
        ],
    }
    with pytest.raises(utils.QuizCreationError) as exc:
        utils.validate_quiz_payload(payload)
    assert "answer must be one of the options" in str(exc.value).lower()


# -----------------------------------------------------------------------------
# Orchestrator finally-cleanup branch + persist branch
# -----------------------------------------------------------------------------

def test_create_quiz_from_url_invalid_url_raises_invalidyoutubourlerror():
    with pytest.raises(utils.InvalidYouTubeUrlError):
        utils.create_quiz_from_url("https://vimeo.com/123", user=object())


def test_create_quiz_from_url_always_cleans_up_temp_audio_on_exception(settings, django_user_model):
    """
    Ensures `cleanup_audio(tmp)` is called in finally, even if AI parsing fails.
    """
    user = django_user_model.objects.create_user(username="u1", email="u1@x.de", password="Password123!")

    settings.GEMINI_API_KEY = "dummy"

    with (
        patch("apps.quiz_management_app.utils.make_temp_audio") as make_tmp,
        patch("apps.quiz_management_app.utils.download_audio_from_video") as dl,
        patch("apps.quiz_management_app.utils.generate_transcript") as tr,
        patch("apps.quiz_management_app.utils.get_ai_response") as ai,
        patch("apps.quiz_management_app.utils.cleanup_audio") as cleanup,
    ):
        tmp = utils.TempAudio(base_path="/tmp/abc")
        make_tmp.return_value = tmp
        dl.return_value = None
        tr.return_value = "hello transcript"

        resp = MagicMock()
        resp.text = "not-json"
        ai.return_value = resp

        with pytest.raises(utils.QuizCreationError):
            utils.create_quiz_from_url("https://www.youtube.com/watch?v=abc", user=user)

        cleanup.assert_called_once_with(tmp)


@pytest.mark.django_db
def test_persist_quiz_creates_quiz_and_bulk_questions(django_user_model):
    user = django_user_model.objects.create_user(username="u2", email="u2@x.de", password="Password123!")
    payload = {
        "title": "Quiz title",
        "description": "Quiz description",
        "questions": [
            {
                "question_title": f"Q{i}",
                "question_options": [f"A{i}", f"B{i}", f"C{i}", f"D{i}"],
                "answer": f"A{i}",
            }
            for i in range(10)
        ],
    }
    quiz = utils._persist_quiz(payload, "https://www.youtube.com/watch?v=xyz", user)
    assert isinstance(quiz, Quiz)
    quiz_any = cast(Any, quiz)
    assert quiz_any.user_id == user.id
    assert quiz_any.questions.count() == 10
    assert QuizQuestion.objects.filter(quiz=quiz).count() == 10