import json
from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import Any


class AnswerParseError(ValueError):
    """
    Raised when model output does not match the answer contract.
    """


@dataclass(frozen=True)
class ParsedAnswer:
    pdf_answer: str
    internet_supplement: str | None = None
    pdf_source_numbers: list[int] = field(default_factory=list)
    web_citations: list[str] = field(default_factory=list)
    disagreement_note: str | None = None


def parse_answer_output(raw_output: str) -> ParsedAnswer:
    """
    Parse model output into the app's structured answer contract.
    """
    cleaned_output = raw_output.strip()

    if not cleaned_output:
        raise AnswerParseError("Model output was empty.")

    try:
        payload = json.loads(_strip_json_code_fence(cleaned_output))
    except JSONDecodeError as error:
        raise AnswerParseError("Model output was not valid JSON.") from error

    if not isinstance(payload, dict):
        raise AnswerParseError("Model output JSON must be an object.")

    pdf_answer = _required_string(payload, "pdf_answer")
    internet_supplement = _optional_string(payload, "internet_supplement")
    disagreement_note = _optional_string(payload, "disagreement_note")
    pdf_source_numbers = _integer_list(payload.get("pdf_source_numbers", []))
    web_citations = _string_list(payload.get("web_citations", []))

    return ParsedAnswer(
        pdf_answer=pdf_answer,
        internet_supplement=internet_supplement,
        pdf_source_numbers=pdf_source_numbers,
        web_citations=web_citations,
        disagreement_note=disagreement_note,
    )


def _strip_json_code_fence(output: str) -> str:
    if not output.startswith("```"):
        return output

    lines = output.splitlines()

    if len(lines) < 3 or lines[-1].strip() != "```":
        return output

    first_line = lines[0].strip().lower()

    if first_line not in {"```", "```json"}:
        return output

    return "\n".join(lines[1:-1]).strip()


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)

    if not isinstance(value, str) or not value.strip():
        raise AnswerParseError(f"Model output must include a non-empty {key}.")

    return value.strip()


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)

    if value is None:
        return None

    if not isinstance(value, str):
        raise AnswerParseError(f"Model output {key} must be a string or null.")

    cleaned_value = value.strip()
    return cleaned_value or None


def _integer_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        raise AnswerParseError("Model output pdf_source_numbers must be a list.")

    if not all(isinstance(item, int) for item in value):
        raise AnswerParseError("Model output pdf_source_numbers must contain integers.")

    return value


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise AnswerParseError("Model output web_citations must be a list.")

    if not all(isinstance(item, str) for item in value):
        raise AnswerParseError("Model output web_citations must contain strings.")

    return [item.strip() for item in value if item.strip()]
