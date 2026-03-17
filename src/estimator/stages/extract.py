"""Stage 1: Extract migration-relevant information from transcript."""

from pathlib import Path

from estimator.llm import call_claude
from estimator.models import ExtractionResult

_PROMPT_FILE = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "extract.md"


def run_extract(transcript: str, model: str = "claude-opus-4-6") -> ExtractionResult:
    """Extract structured migration details from a sales call transcript.

    Args:
        transcript: Raw transcript text.
        model: Claude model to use.

    Returns:
        ExtractionResult with structured migration details.
    """
    system_prompt = _PROMPT_FILE.read_text(encoding="utf-8")
    schema = ExtractionResult.model_json_schema()

    result = call_claude(
        prompt="Extract all migration-relevant information from the transcript provided via stdin.",
        model=model,
        system_prompt=system_prompt,
        json_schema=schema,
        input_text=transcript,
    )

    return ExtractionResult.model_validate(result)
