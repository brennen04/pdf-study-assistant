from src.answer.parser import ParsedAnswer
from src.answer.result import RetrievedSource


class AnswerValidationError(ValueError):
    """
    Raised when parsed model output conflicts with trusted app state.
    """


def validate_pdf_source_numbers(
    parsed_answer: ParsedAnswer,
    sources: list[RetrievedSource],
) -> None:
    """
    Ensure cited PDF source numbers refer to retrieved PDF sources.
    """
    valid_source_numbers = {source.source_number for source in sources}
    invalid_source_numbers = [
        source_number
        for source_number in parsed_answer.pdf_source_numbers
        if source_number not in valid_source_numbers
    ]

    if invalid_source_numbers:
        raise AnswerValidationError(
            "Model output cited PDF source numbers that were not retrieved: "
            f"{invalid_source_numbers}."
        )
