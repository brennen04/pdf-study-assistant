from dataclasses import dataclass

from src.evaluation.models import EvaluationCase
from src.rag.document import PdfPage


@dataclass(frozen=True)
class EvaluationDocument:
    document_id: str
    filename: str
    pages: tuple[PdfPage, ...]


DOCUMENTS = (
    EvaluationDocument(
        document_id="cyber_hygiene_short",
        filename="cyber-hygiene-short.pdf",
        pages=(
            PdfPage(1, "Passwords protect accounts. Use a unique passphrase for every account and store passphrases in a password manager."),
            PdfPage(2, "Multi-factor authentication adds a second verification step. Enable it for email, banking, and administrator accounts."),
            PdfPage(3, "Software updates install security patches. Configure devices and applications to update automatically when possible."),
        ),
    ),
    EvaluationDocument(
        document_id="explainable_ai_medium",
        filename="explainable-ai-medium.pdf",
        pages=(
            PdfPage(1, "Explainable artificial intelligence helps people understand why a system produced an outcome."),
            PdfPage(2, "Explanation means an AI system supplies evidence or reasons for its output."),
            PdfPage(3, "Meaningful explanations are understandable to the intended user and fit that user's knowledge and task."),
            PdfPage(4, "Explanation accuracy means the explanation correctly reflects how the system generated its output."),
            PdfPage(5, "Knowledge limits require a system to operate only within conditions for which it was designed and to identify low confidence."),
            PdfPage(6, "Evaluation should consider whether explanations are useful, accurate, and appropriate for different users."),
        ),
    ),
    EvaluationDocument(
        document_id="ai_governance_long",
        filename="ai-governance-long.pdf",
        pages=(
            PdfPage(1, "AI governance establishes accountability for how an organization designs, deploys, and monitors AI systems."),
            PdfPage(2, "Risk framing identifies possible benefits, harms, affected people, and the operational context of an AI system."),
            PdfPage(3, "Data quality review checks whether training and evaluation data represent the intended context and population."),
            PdfPage(4, "Documentation records system purpose, data sources, model limits, owners, and important design decisions."),
            PdfPage(5, "Human oversight defines when people review outputs, approve actions, or intervene when automated behavior is unsafe."),
            PdfPage(6, "Measurement uses tests, monitoring, and incident reports to assess reliability, bias, security, and performance."),
            PdfPage(7, "Risk prioritization considers likelihood, severity, affected groups, and whether harms can be reversed."),
            PdfPage(8, "Mitigation can include changing data, restricting use cases, adding review controls, or declining deployment."),
            PdfPage(9, "Incident response defines reporting channels, investigation steps, communication responsibilities, and recovery actions."),
            PdfPage(10, "Continuous monitoring detects model drift, changing contexts, new failure patterns, and unexpected user behavior."),
            PdfPage(11, "Periodic review revisits system goals, stakeholder feedback, residual risk, and whether deployment remains justified."),
            PdfPage(12, "Transparent communication explains important limitations, risk controls, and how affected people can raise concerns."),
        ),
    ),
)


CASES = (
    EvaluationCase("short-passwords", "cyber_hygiene_short", "What protects accounts?", (1,), 1, "answerable"),
    EvaluationCase("short-mfa", "cyber_hygiene_short", "What does multi-factor authentication add?", (2,), 1, "answerable"),
    EvaluationCase("short-updates", "cyber_hygiene_short", "Why should software update automatically?", (3,), 1, "answerable"),
    EvaluationCase("short-unsupported", "cyber_hygiene_short", "What is the incident response process?", (), 0, "unsupported_by_pdf"),
    EvaluationCase("medium-evidence", "explainable_ai_medium", "What does explanation require from an AI system?", (2,), 1, "answerable"),
    EvaluationCase("medium-meaningful", "explainable_ai_medium", "Who should an explanation be understandable to?", (3,), 1, "answerable"),
    EvaluationCase("medium-accuracy", "explainable_ai_medium", "What is explanation accuracy?", (4,), 1, "answerable"),
    EvaluationCase("medium-limits", "explainable_ai_medium", "What do knowledge limits require?", (5,), 1, "answerable"),
    EvaluationCase("medium-evaluation", "explainable_ai_medium", "What should explanation evaluation consider?", (6,), 1, "answerable"),
    EvaluationCase("medium-unsupported", "explainable_ai_medium", "How should an organization respond to a data breach?", (), 0, "unsupported_by_pdf"),
    EvaluationCase("long-governance", "ai_governance_long", "What does AI governance establish?", (1,), 1, "answerable"),
    EvaluationCase("long-data", "ai_governance_long", "What does data quality review check?", (3,), 1, "answerable"),
    EvaluationCase("long-oversight", "ai_governance_long", "When should people intervene in AI behavior?", (5,), 1, "answerable"),
    EvaluationCase("long-measurement", "ai_governance_long", "What does AI measurement assess?", (6,), 1, "answerable"),
    EvaluationCase("long-mitigation", "ai_governance_long", "Give examples of risk mitigation.", (8,), 1, "answerable"),
    EvaluationCase("long-monitoring", "ai_governance_long", "What can continuous monitoring detect?", (10,), 1, "answerable"),
    EvaluationCase("long-review", "ai_governance_long", "What does periodic review revisit?", (11,), 1, "answerable"),
    EvaluationCase("long-transparency", "ai_governance_long", "What should transparent communication explain?", (12,), 1, "answerable"),
    EvaluationCase("long-summary", "ai_governance_long", "Summarise this document.", (1, 6, 12), 3, "study_transformation"),
    EvaluationCase("long-unsupported", "ai_governance_long", "What password manager should employees use?", (), 0, "unsupported_by_pdf"),
)
