import os
from dataclasses import dataclass, field
from urllib.parse import urlparse

from src.answer.result import WebCitation


DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"


@dataclass(frozen=True)
class GeneratedContent:
    text: str
    web_citations: list[WebCitation] = field(default_factory=list)


def generate_answer(
    prompt: str,
    api_key: str | None = None,
    use_google_search: bool = False,
    model_name: str = DEFAULT_GEMINI_MODEL,
) -> GeneratedContent:
    """
    Generate an answer with Gemini.

    Google Search grounding is optional because the app's first responsibility is
    to answer from the uploaded PDF. Search should be enabled only when we want
    an internet supplement.
    """
    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        raise ValueError("prompt must not be empty.")

    api_key = api_key or os.getenv("LLM_API_KEY")

    if not api_key:
        raise ValueError(
            "LLM API key is missing. Add LLM_API_KEY to your .env file "
            "or set it in your shell environment before running the app."
        )

    try:
        from google import genai
        from google.genai import types
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "The google-genai package is required. Install it with "
            "`pip install google-genai`."
        ) from error

    client = genai.Client(api_key=api_key)

    config = None

    if use_google_search:
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])

    response = client.models.generate_content(
        model=model_name,
        contents=cleaned_prompt,
        config=config,
    )

    answer_text = response.text or ""

    if not answer_text.strip():
        raise ValueError("Gemini returned an empty response.")

    return GeneratedContent(
        text=answer_text,
        web_citations=_extract_web_citations(response),
    )


def _extract_web_citations(response: object) -> list[WebCitation]:
    """Extract unique, absolute web sources from Gemini grounding metadata."""
    candidates = getattr(response, "candidates", None) or []

    if not candidates:
        return []

    grounding_metadata = getattr(candidates[0], "grounding_metadata", None)
    grounding_chunks = getattr(grounding_metadata, "grounding_chunks", None) or []
    citations: list[WebCitation] = []
    seen_uris: set[str] = set()

    for chunk in grounding_chunks:
        web = getattr(chunk, "web", None)

        if web is None:
            continue

        uri = (getattr(web, "uri", None) or "").strip()
        parsed_uri = urlparse(uri)

        if (
            parsed_uri.scheme not in {"http", "https"}
            or not parsed_uri.netloc
            or uri in seen_uris
        ):
            continue

        title = (getattr(web, "title", None) or "").strip()
        citations.append(
            WebCitation(
                title=title or parsed_uri.netloc.removeprefix("www."),
                uri=uri,
            )
        )
        seen_uris.add(uri)

    return citations
