from src.answer.result import AnswerError


def map_answer_generation_error(error: Exception) -> AnswerError:
    """
    Convert provider/runtime exceptions into stable application error states.
    """
    error_text = str(error)

    if isinstance(error, ValueError) and "LLM API key is missing" in error_text:
        return AnswerError(
            code="missing_api_key",
            message=(
                "The app is not configured with a model API key. Add the key "
                "in the deployment or local environment before generating answers."
            ),
            details=repr(error),
        )

    if isinstance(error, ValueError) and "empty response" in error_text.lower():
        return AnswerError(
            code="empty_model_response",
            message=(
                "The model provider returned an empty answer. Try again shortly."
            ),
            details=repr(error),
        )

    if isinstance(error, ModuleNotFoundError):
        return AnswerError(
            code="provider_dependency_missing",
            message=(
                "A required model provider dependency is not installed in this environment."
            ),
            details=repr(error),
        )

    return AnswerError(
        code="provider_unavailable",
        message=(
            "The model provider did not return a usable answer. Try again shortly."
        ),
        details=repr(error),
    )
