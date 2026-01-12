import pytest
import json

from apps.quiz_management_app.utils import (
    QuizCreationError,
    parse_quiz_json,
    validate_quiz_payload,
)


def _good_payload():
    return {
        "title": "T",
        "description": "D",
        "questions": [
            {"question_title": f"Q{i}?", "question_options": ["A", "B", "C", "D"], "answer": "A"}
            for i in range(10)
        ],
    }


def test_parse_quiz_json_valid():
    payload = _good_payload()
    parsed = parse_quiz_json(json.dumps(payload))
    assert parsed["title"] == "T"
    assert len(parsed["questions"]) == 10


def test_parse_quiz_json_invalid_raises():
    with pytest.raises(QuizCreationError):
        parse_quiz_json("not json")


def test_validate_quiz_payload_ok():
    validate_quiz_payload(_good_payload())


def test_validate_quiz_payload_requires_10_questions():
    bad = _good_payload()
    bad["questions"] = bad["questions"][:2]
    with pytest.raises(QuizCreationError, match="exactly 10 questions"):
        validate_quiz_payload(bad)


def test_validate_question_requires_4_distinct_options():
    bad = _good_payload()
    bad["questions"][0]["question_options"] = ["A", "A", "B", "C"]
    with pytest.raises(QuizCreationError, match="distinct"):
        validate_quiz_payload(bad)


def test_validate_question_answer_must_be_in_options():
    bad = _good_payload()
    bad["questions"][0]["answer"] = "Z"
    with pytest.raises(QuizCreationError, match="Answer must be one of the options"):
        validate_quiz_payload(bad)