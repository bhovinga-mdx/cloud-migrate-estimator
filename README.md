# Cloud Migration Estimator

CLI tool that generates cloud migration cost and timeline estimates from sales call transcripts using Claude AI. Takes a transcript file, runs it through a multi-stage AI pipeline, and produces a structured Markdown report with three-scenario estimates, architecture proposals, and gap analysis.

## Quick Start

```bash
# Prerequisites: Python 3.12+, uv, Claude Code CLI (authenticated)
uv sync
uv run estimate generate path/to/transcript.txt -v
```

## What It Does

Given a sales call transcript for a cloud migration engagement, the tool:

1. **Extracts** migration-relevant details (environment, workloads, constraints, timeline)
2. **Proposes** a target AWS architecture with t-shirt-sized cost estimates
3. **Generates** three-scenario cost and timeline estimates (optimistic / likely / pessimistic)
4. **Identifies** information gaps, follow-up questions, and risk factors
5. **Produces** a structured Markdown report for internal review

## Usage

```bash
uv run estimate generate <transcript_file>     # Generate estimate
uv run estimate generate <file> -v             # With progress output
uv run estimate generate <file> -o ./output    # Custom output directory
uv run estimate validate-config                # Verify config files
uv run estimate version                        # Show version
```

## Output

Reports are saved to `./estimates/{timestamp}_{client_name}/` containing:

- `report.md` -- The full estimation report
- `stages/01_extraction.json` -- Extracted migration details
- `stages/02_architecture.json` -- Proposed architecture
- `stages/03_estimate.json` -- Cost and timeline estimates
- `stages/04_gaps.json` -- Gap analysis and risks

## Configuration

Edit TOML files in `config/`:

- `rate_card.toml` -- Role titles and hourly rates
- `aws_baselines.toml` -- AWS t-shirt size definitions and cost ranges
- `settings.toml` -- Model selection per stage, pipeline parameters

## Documentation

- [Problem Statement](docs/PROBLEM.md) -- Why this tool exists
- [Requirements](docs/REQUIREMENTS.md) -- What it needs to do
- [Architecture](docs/ARCHITECTURE.md) -- How it works
- [Decisions](docs/DECISIONS.md) -- Why it works this way
- [Development Guide](docs/DEVELOPMENT.md) -- How to work on it

## Development

```bash
uv run pytest                          # Run tests
uv run pytest -m "not integration"     # Skip live Claude tests
uv run ruff check .                    # Lint
uv run ruff format .                   # Format
```
