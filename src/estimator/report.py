"""Report generation from pipeline stage outputs."""

from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from estimator.config import AWSBaselinesConfig, RateCardConfig
from estimator.models import (
    ArchitectureResult,
    EstimateResult,
    ExtractionResult,
    GapsResult,
)

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


def render_report(
    extraction: ExtractionResult,
    architecture: ArchitectureResult,
    estimate: EstimateResult,
    gaps: GapsResult,
    rate_card: RateCardConfig,
    aws_baselines: AWSBaselinesConfig,
) -> str:
    """Render the estimation report as Markdown.

    Args:
        extraction: Stage 1 output.
        architecture: Stage 2 output.
        estimate: Stage 3 output.
        gaps: Stage 4 output.
        rate_card: Rate card config for displaying rates.
        aws_baselines: AWS baseline config for reference.

    Returns:
        Rendered Markdown string.
    """
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.md.j2")

    return template.render(
        generated_date=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        extraction=extraction,
        architecture=architecture,
        estimate=estimate,
        gaps=gaps,
        rate_card=rate_card,
        aws_baselines=aws_baselines,
    )
