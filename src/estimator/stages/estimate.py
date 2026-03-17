"""Stage 3: Generate three-scenario cost and timeline estimate."""

import json
from pathlib import Path

from estimator.config import RateCardConfig
from estimator.llm import call_claude
from estimator.models import ArchitectureResult, EstimateResult, ExtractionResult

_PROMPT_FILE = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "estimate.md"


def run_estimate(
    extraction: ExtractionResult,
    architecture: ArchitectureResult,
    rate_card: RateCardConfig,
    model: str = "claude-opus-4-6",
) -> EstimateResult:
    """Generate a three-scenario cost and timeline estimate.

    Args:
        extraction: Structured extraction from stage 1.
        architecture: Architecture proposal from stage 2.
        rate_card: Rate card configuration with role rates.
        model: Claude model to use.

    Returns:
        EstimateResult with three-scenario costs and timeline.
    """
    system_prompt = _PROMPT_FILE.read_text(encoding="utf-8")
    schema = EstimateResult.model_json_schema()

    rate_card_formatted = {
        role_key: {"title": role.title, "hourly_rate": role.hourly_rate}
        for role_key, role in rate_card.roles.items()
    }

    prompt = (
        "Produce a three-scenario cost and timeline estimate based on the following.\n\n"
        f"RATE CARD:\n{json.dumps(rate_card_formatted, indent=2)}\n\n"
        f"EXTRACTED DETAILS:\n{json.dumps(extraction.model_dump(), indent=2)}\n\n"
        f"TARGET ARCHITECTURE:\n{json.dumps(architecture.model_dump(), indent=2)}"
    )

    result = call_claude(
        prompt=prompt,
        model=model,
        system_prompt=system_prompt,
        json_schema=schema,
    )

    return EstimateResult.model_validate(result)
