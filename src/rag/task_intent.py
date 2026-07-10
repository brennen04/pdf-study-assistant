from enum import StrEnum


class TaskIntent(StrEnum):
    """
    High-level shape of the user's PDF-grounded task.
    """
    FACTUAL_LOOKUP = "factual_lookup"
    STUDY_TRANSFORMATION = "study_transformation"


STUDY_TRANSFORMATION_PHRASES = (
    "summarise",
    "summarize",
    "summary",
    "note",
    "notes",
    "outline",
    "flashcard",
    "flashcards",
    "study guide",
    "simplify",
    "teach me",
    "key points",
    "main ideas",
    "takeaways",
    "what is this about",
    "what's this about",
    "what is it about",
    "what this is about",
)


def classify_task_intent(question: str) -> TaskIntent:
    """
    Classify whether a question asks for a lookup or a study transformation.

    This is intentionally heuristic for now. It keeps routing deterministic and
    testable while the product is still learning what user requests look like.
    """
    normalized_question = question.strip().lower()

    if any(phrase in normalized_question for phrase in STUDY_TRANSFORMATION_PHRASES):
        return TaskIntent.STUDY_TRANSFORMATION

    return TaskIntent.FACTUAL_LOOKUP
