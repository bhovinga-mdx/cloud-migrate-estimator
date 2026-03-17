"""CLI entrypoint using Typer."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from estimator import __version__
from estimator.config import validate_config
from estimator.pipeline import PipelineError, run_pipeline

app = typer.Typer(
    name="estimate",
    help="Generate cloud migration cost/timeline estimates from sales call transcripts.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def generate(
    transcript: Annotated[
        Path,
        typer.Argument(
            help="Path to the transcript file (TXT or MD).",
            exists=True,
            readable=True,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory for the report."),
    ] = None,
    config_dir: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Config directory override."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show stage progress."),
    ] = True,
) -> None:
    """Generate a cloud migration estimate from a sales call transcript."""
    suffix = transcript.suffix.lower()
    if suffix not in (".txt", ".md"):
        console.print(f"[red]Error:[/] Unsupported file type '{suffix}'. Use .txt or .md.")
        raise typer.Exit(code=1)

    try:
        report_path = run_pipeline(
            transcript_path=transcript,
            config_dir=config_dir,
            output_dir=output,
            verbose=verbose,
        )
        console.print(f"\n[bold green]Report generated:[/] {report_path}")
    except PipelineError as e:
        console.print(f"[red]Pipeline error:[/] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/] {e}")
        raise typer.Exit(code=1)


@app.command(name="validate-config")
def validate_config_cmd(
    config_dir: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Config directory override."),
    ] = None,
) -> None:
    """Validate configuration files."""
    errors = validate_config(config_dir)
    if errors:
        console.print("[red]Configuration errors:[/]")
        for error in errors:
            console.print(f"  - {error}")
        raise typer.Exit(code=1)
    else:
        console.print("[green]All configuration files are valid.[/]")


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"cloud-migrate-estimator v{__version__}")


if __name__ == "__main__":
    app()
