"""Stage 4: Identify gaps, risks, and follow-up questions."""

import json
from pathlib import Path

from estimator.llm import call_claude
from estimator.models import (
    ArchitectureResult,
    EstimateResult,
    ExtractionResult,
    GapsResult,
)

_PROMPT_FILE = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "gaps.md"


def run_gaps(
    extraction: ExtractionResult,
    architecture: ArchitectureResult,
    estimate: EstimateResult,
    model: str = "claude-sonnet-4-6",
) -> GapsResult:
    """Identify information gaps, risks, and follow-up questions.

    Args:
        extraction: Structured extraction from stage 1.
        architecture: Architecture proposal from stage 2.
        estimate: Cost/timeline estimate from stage 3.
        model: Claude model to use.

    Returns:
        GapsResult with gaps, follow-up questions, and risk assessment.
    """
    system_prompt = _PROMPT_FILE.read_text(encoding="utf-8")
    schema = GapsResult.model_json_schema()

    prompt = (
        "Review the following cloud migration estimate for completeness and risk.\n\n"
        f"EXTRACTED DETAILS:\n{json.dumps(extraction.model_dump(), indent=2)}\n\n"
        f"TARGET ARCHITECTURE:\n{json.dumps(architecture.model_dump(), indent=2)}\n\n"
        f"ESTIMATE:\n{json.dumps(estimate.model_dump(), indent=2)}"
    )

    result = call_claude(
        prompt=prompt,
        model=model,
        system_prompt=system_prompt,
        json_schema=schema,
    )

    return GapsResult.model_validate(result)
