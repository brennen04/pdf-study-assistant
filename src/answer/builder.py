from src.rag.task_intent import TaskIntent
from src.rag.document import DocumentChunk


def build_grounded_answer_prompt(
    question: str,
    retrieved_chunks: list[tuple[DocumentChunk, float | None]],
    task_intent: TaskIntent = TaskIntent.FACTUAL_LOOKUP,
) -> str:
    """Build the PDF-only prompt that must pass citation validation."""
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("question must not be empty.")

    if not retrieved_chunks:
        raise ValueError("retrieved_chunks must not be empty.")

    context_sections = []

    for index, (chunk, score) in enumerate(retrieved_chunks, start=1):
        source_label = (
            f"similarity: {score:.3f}"
            if score is not None
            else "broad document context"
        )
        context_sections.append(
            f"Source {index} ({chunk.filename}, page {chunk.page_number}, "
            f"chunk {chunk.chunk_id}; {source_label}):\n{chunk.text.strip()}"
        )

    context = "\n\n".join(context_sections)
    return f"""You are a study assistant.

Answer the question using only the PDF context below.

Rules:
- Do not use outside or internet information.
- For study transformations such as summaries, notes, outlines, flashcards, explanations, or study guides, synthesize from the PDF context instead of looking for an existing summary or note inside the PDF.
- For factual lookup questions, if the PDF context does not contain enough information, say that clearly.
- Keep the answer clear, concise, and useful for studying.
- Return only valid JSON. Do not wrap it in Markdown.
- The JSON object must use this schema:
  {{
    "pdf_answer": "Answer grounded only in the PDF context. Say when the PDF does not contain enough information.",
    "pdf_source_numbers": [1, 2]
  }}
- Always include one or more PDF source numbers from the PDF context above.
- If the PDF does not contain enough information, say that in pdf_answer and cite
  the one or more closest retrieved PDF sources you used to reach that conclusion.
  Never return an empty pdf_source_numbers list for an unsupported question.

Question:
{cleaned_question}

Task intent:
{task_intent.value}

PDF context:
{context}

Answer:"""


def build_internet_supplement_prompt(
    question: str,
    pdf_answer: str,
) -> str:
    """Build the separate Google Search prompt used after PDF validation."""
    cleaned_question = question.strip()
    cleaned_pdf_answer = pdf_answer.strip()

    if not cleaned_question:
        raise ValueError("question must not be empty.")

    if not cleaned_pdf_answer:
        raise ValueError("pdf_answer must not be empty.")

    return f"""You are adding a separate internet supplement to a PDF-grounded answer.

Use Google Search to add useful outside context, fill gaps, or provide current
information. Do not rewrite the PDF answer or present web information as if it
came from the PDF. If the web and PDF disagree, describe the disagreement.

Return only valid JSON. Do not wrap it in Markdown. Use this schema:
{{
  "internet_supplement": "Useful outside context, or a clear statement that search added nothing useful.",
  "disagreement_note": "PDF/internet disagreement, or null when there is no disagreement."
}}

Do not invent or return citation URLs. The application reads web sources directly
from Google Search grounding metadata.

Question:
{cleaned_question}

Validated PDF answer:
{cleaned_pdf_answer}

Internet supplement:"""
