"""Pipeline orchestrator — runs all stages in sequence."""

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console

from estimator.config import (
    load_aws_baselines,
    load_rate_card,
    load_settings,
)
from estimator.models import (
    ExtractionResult,
)
from estimator.report import render_report
from estimator.stages.architect import run_architect
from estimator.stages.estimate import run_estimate
from estimator.stages.extract import run_extract
from estimator.stages.gaps import run_gaps

console = Console()


class PipelineError(Exception):
    """Raised when the pipeline fails."""


def _extract_client_name(extraction: ExtractionResult) -> str:
    """Try to extract a client name from the extraction result."""
    stakeholders = extraction.migration_context.stakeholders_mentioned
    if stakeholders:
        return re.sub(r"[^\w\s-]", "", stakeholders[0]).strip().replace(" ", "_")[:30]
    return "unknown_client"


def _save_stage_output(output_dir: Path, stage_name: str, data: dict) -> None:
    """Save intermediate stage output to JSON file."""
    stages_dir = output_dir / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    path = stages_dir / f"{stage_name}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_pipeline(
    transcript_path: Path,
    config_dir: Path | None = None,
    output_dir: Path | None = None,
    verbose: bool = False,
) -> Path:
    """Run the full estimation pipeline.

    Args:
        transcript_path: Path to the transcript file (TXT or MD).
        config_dir: Optional config directory override.
        output_dir: Optional output directory override.
        verbose: Print stage progress to console.

    Returns:
        Path to the generated report.
    """
    # Load config
    settings = load_settings(config_dir)
    rate_card = load_rate_card(config_dir)
    aws_baselines = load_aws_baselines(config_dir)

    # Read transcript
    transcript = transcript_path.read_text(encoding="utf-8")

    # Check transcript size
    if len(transcript) > settings.pipeline.max_transcript_chars:
        raise PipelineError(
            f"Transcript is {len(transcript):,} characters, "
            f"exceeding the {settings.pipeline.max_transcript_chars:,} character limit. "
            "Consider using a shorter transcript or summarizing the call."
        )

    if not transcript.strip():
        raise PipelineError("Transcript file is empty.")

    # Stage 1: Extract
    if verbose:
        console.print("[bold blue]Stage 1/4:[/] Extracting migration details...")
    extraction = run_extract(transcript, model=settings.models.extract)

    # Set up output directory
    client_name = _extract_client_name(extraction)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    if output_dir is None:
        output_dir = Path(settings.output.output_dir) / f"{timestamp}_{client_name}"
    output_dir.mkdir(parents=True, exist_ok=True)

    if settings.output.save_intermediates:
        _save_stage_output(output_dir, "01_extraction", extraction.model_dump())

    if verbose:
        console.print(f"  [green]✓[/] Extracted {len(extraction.workloads)} workload(s)")

    # Stage 2: Architect
    if verbose:
        console.print("[bold blue]Stage 2/4:[/] Designing target architecture...")
    architecture = run_architect(extraction, model=settings.models.architect)

    if settings.output.save_intermediates:
        _save_stage_output(output_dir, "02_architecture", architecture.model_dump())

    if verbose:
        console.print(
            f"  [green]✓[/] Strategy: {architecture.migration_strategy}, "
            f"Size: {architecture.tshirt_size.size}"
        )

    # Stage 3: Estimate
    if verbose:
        console.print("[bold blue]Stage 3/4:[/] Generating cost estimate...")
    estimate = run_estimate(
        extraction, architecture, rate_card, model=settings.models.estimate
    )

    if settings.output.save_intermediates:
        _save_stage_output(output_dir, "03_estimate", estimate.model_dump())

    if verbose:
        console.print(
            f"  [green]✓[/] Likely total: ${estimate.likely.total_first_year:,} "
            f"({estimate.timeline_likely.duration_weeks} weeks)"
        )

    # Stage 4: Gaps
    if verbose:
        console.print("[bold blue]Stage 4/4:[/] Analyzing gaps and risks...")
    gaps = run_gaps(extraction, architecture, estimate, model=settings.models.gaps)

    if settings.output.save_intermediates:
        _save_stage_output(output_dir, "04_gaps", gaps.model_dump())

    if verbose:
        console.print(
            f"  [green]✓[/] Found {len(gaps.gaps)} gap(s), "
            f"{len(gaps.follow_up_questions)} follow-up question(s)"
        )

    # Stage 5: Report
    if verbose:
        console.print("[bold blue]Generating report...[/]")

    report_content = render_report(
        extraction=extraction,
        architecture=architecture,
        estimate=estimate,
        gaps=gaps,
        rate_card=rate_card,
        aws_baselines=aws_baselines,
    )

    report_path = output_dir / "report.md"
    report_path.write_text(report_content, encoding="utf-8")

    if verbose:
        console.print(f"  [green]✓[/] Report saved to {report_path}")

    return report_path
