import json

import pytest
from pydantic import ValidationError

from triage.schema import TriageDecision, TriageValidationError, validate_decision

VALID = {
    "category": "billing",
    "priority": "P2",
    "route": "billing-team",
    "rationale": "A double charge is a money problem.",
}


def test_accepts_a_valid_decision_as_dict_or_json():
    assert validate_decision(VALID) == TriageDecision(**VALID)
    assert validate_decision(json.dumps(VALID)).priority == "P2"
    assert validate_decision(json.dumps(VALID).encode()).priority == "P2"


@pytest.mark.parametrize(
    "rationale",
    ["This is e.g. a valid rationale.", "The value is 3.14 units."],
)
def test_accepts_abbreviations_and_decimal_points_in_one_sentence(rationale):
    assert validate_decision({**VALID, "rationale": rationale}).rationale == rationale


@pytest.mark.parametrize(
    "change, field",
    [
        ({"category": "sales"}, "category"),
        ({"priority": "P5"}, "priority"),
        ({"route": "finance-team"}, "route"),
        ({"rationale": "   "}, "rationale"),
        ({"rationale": "First sentence. Second sentence."}, "rationale"),
        ({"rationale": "First sentence.Second sentence"}, "rationale"),
        ({"rationale": "..."}, "rationale"),
        ({"extra": "field"}, "extra"),
    ],
)
def test_rejects_bad_fields_with_a_message_naming_the_field(change, field):
    with pytest.raises(TriageValidationError, match=field):
        validate_decision({**VALID, **change})


@pytest.mark.parametrize("field", ["category", "priority", "route", "rationale"])
def test_rejects_a_missing_field(field):
    payload = {k: v for k, v in VALID.items() if k != field}
    with pytest.raises(TriageValidationError, match=field):
        validate_decision(payload)


@pytest.mark.parametrize(
    "field, value",
    [("category", None), ("priority", 2), ("route", None), ("rationale", 42)],
)
def test_rejects_invalid_field_types_and_nulls(field, value):
    with pytest.raises(TriageValidationError, match=field):
        validate_decision({**VALID, field: value})


@pytest.mark.parametrize("payload", ["not json", b"\x80\x81", "[1, 2]", "42"])
def test_rejects_non_objects(payload):
    with pytest.raises(TriageValidationError):
        validate_decision(payload)


def test_decisions_are_immutable():
    decision = validate_decision(VALID)
    with pytest.raises(ValidationError, match="frozen"):
        decision.priority = "P1"


def test_reports_all_validation_errors():
    with pytest.raises(TriageValidationError) as error:
        validate_decision({"category": "sales", "priority": "P5", "route": "finance-team"})

    message = str(error.value)
    assert "category" in message
    assert "priority" in message
    assert "route" in message
