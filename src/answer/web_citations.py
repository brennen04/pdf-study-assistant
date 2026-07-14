from urllib.parse import urlparse

from src.answer.result import WebCitation

GOOGLE_GROUNDING_REDIRECT_HOST = "vertexaisearch.cloud.google.com"
GOOGLE_GROUNDING_REDIRECT_PATH_PREFIX = "/grounding-api-redirect/"


def format_web_citation(citation: WebCitation, citation_number: int) -> str:
    """
    Return a readable Markdown representation for a web citation.
    """
    cleaned_citation = citation.uri.strip()

    if not cleaned_citation:
        return ""

    parsed_url = urlparse(cleaned_citation)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        return citation.title.strip()

    label = " ".join(citation.title.split()) or _citation_label(
        parsed_url.netloc,
        parsed_url.path,
        citation_number,
    )
    label = label.replace("[", "\\[").replace("]", "\\]")
    return f"[{label}]({cleaned_citation})"


def _citation_label(hostname: str, path: str, citation_number: int) -> str:
    normalized_hostname = hostname.lower()

    if (
        normalized_hostname == GOOGLE_GROUNDING_REDIRECT_HOST
        and path.startswith(GOOGLE_GROUNDING_REDIRECT_PATH_PREFIX)
    ):
        return f"Google Search result {citation_number}"

    return normalized_hostname.removeprefix("www.")
