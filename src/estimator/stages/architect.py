"""Stage 2: Propose target AWS architecture based on extraction."""

import json
from pathlib import Path

from estimator.llm import call_claude
from estimator.models import ArchitectureResult, ExtractionResult

_PROMPT_FILE = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "architect.md"


def run_architect(
    extraction: ExtractionResult, model: str = "claude-sonnet-4-6"
) -> ArchitectureResult:
    """Propose a target AWS architecture based on extracted migration details.

    Args:
        extraction: Structured extraction from stage 1.
        model: Claude model to use.

    Returns:
        ArchitectureResult with proposed architecture.
    """
    system_prompt = _PROMPT_FILE.read_text(encoding="utf-8")
    schema = ArchitectureResult.model_json_schema()

    extraction_json = json.dumps(extraction.model_dump(), indent=2)

    result = call_claude(
        prompt=(
            "Based on the following extracted migration details, "
            "propose a target AWS architecture.\n\n"
            f"EXTRACTED MIGRATION DETAILS:\n{extraction_json}"
        ),
        model=model,
        system_prompt=system_prompt,
        json_schema=schema,
    )

    return ArchitectureResult.model_validate(result)
