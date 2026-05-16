def build_grounded_answer_prompt(
    question: str,
    retrieved_chunks: list[tuple[str, float]],
    internet_context_enabled: bool = False,
    web_context: list[str] | None = None,
) -> str:
    """
    Build the prompt that will be sent to a language model.

    PDF context is the primary source. Optional web context can supplement the
    answer, but it must not replace or override what the PDF says.
    """
    cleaned_question = question.strip()
    web_context = web_context or []

    if not cleaned_question:
        raise ValueError("question must not be empty.")

    if not retrieved_chunks:
        raise ValueError("retrieved_chunks must not be empty.")

    context_sections = []

    for index, (chunk, score) in enumerate(retrieved_chunks, start=1):
        context_sections.append(
            f"Source {index} (similarity: {score:.3f}):\n{chunk.strip()}"
        )

    context = "\n\n".join(context_sections)
    web_context_text = "\n\n".join(
        f"Web source {index}:\n{source.strip()}"
        for index, source in enumerate(web_context, start=1)
        if source.strip()
    )

    if web_context_text:
        internet_instruction = (
            "After the PDF-based answer, add a separate Internet supplement "
            "using the internet context below."
        )
        web_section = web_context_text
    elif internet_context_enabled:
        internet_instruction = (
            "After the PDF-based answer, use Google Search grounding to add a "
            "separate Internet supplement if useful."
        )
        web_section = (
            "Internet context is enabled through Google Search grounding. "
            "Use web information only in the separate Internet supplement."
        )
    else:
        internet_instruction = (
            "Do not add internet information because internet context is disabled."
        )
        web_section = "Internet context is disabled."

    return f"""You are a study assistant.

Answer the question in two stages:
1. First, answer using the PDF context.
2. {internet_instruction}

Rules:
- Treat the PDF as the primary source.
- Treat internet context as a supplement that can add useful information but must not contradict or replace what the PDF says.
- Do not use internet context to replace or hide what the PDF says.
- If the PDF context does not contain enough information, say that clearly before using internet context.
- Keep PDF-based information and internet-based information separate.
- If the PDF and internet context disagree, point out the disagreement.
Keep the answer clear, concise, and useful for studying.
- If the question cannot be answered based on the PDF context, say that clearly and do not attempt to answer based on internet context alone.

Question:
{cleaned_question}

PDF context:
{context}

Internet context:
{web_section}

Answer:"""
