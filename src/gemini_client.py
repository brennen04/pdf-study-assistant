import os


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def generate_answer(
    prompt: str,
    api_key: str | None = None,
    use_google_search: bool = False,
    model_name: str = DEFAULT_GEMINI_MODEL,
) -> str:
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

    return response.text or ""
