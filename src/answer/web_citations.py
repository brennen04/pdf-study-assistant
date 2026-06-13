from urllib.parse import urlparse


GOOGLE_GROUNDING_REDIRECT_HOST = "vertexaisearch.cloud.google.com"
GOOGLE_GROUNDING_REDIRECT_PATH_PREFIX = "/grounding-api-redirect/"


def format_web_citation(citation: str, citation_number: int) -> str:
    """
    Return a readable Markdown representation for a web citation.
    """
    cleaned_citation = citation.strip()

    if not cleaned_citation:
        return ""

    if cleaned_citation.startswith("[") and "](" in cleaned_citation:
        return cleaned_citation

    parsed_url = urlparse(cleaned_citation)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        return cleaned_citation

    label = _citation_label(parsed_url.netloc, parsed_url.path, citation_number)
    return f"[{label}]({cleaned_citation})"


def _citation_label(hostname: str, path: str, citation_number: int) -> str:
    normalized_hostname = hostname.lower()

    if (
        normalized_hostname == GOOGLE_GROUNDING_REDIRECT_HOST
        and path.startswith(GOOGLE_GROUNDING_REDIRECT_PATH_PREFIX)
    ):
        return f"Google Search result {citation_number}"

    return normalized_hostname.removeprefix("www.")
