# Cloud Migration Estimator

## Project Overview
CLI tool that generates cloud migration cost/timeline estimates from sales call transcripts using Claude AI via Claude Code CLI.

## Tech Stack
- Python 3.12+ with Typer (CLI), Pydantic (models), Jinja2 (reports), Rich (output)
- Claude Code CLI (`claude -p`) for AI inference
- TOML for configuration
- uv for package management
- Ruff for linting/formatting
- pytest for testing

## Project Structure
```
src/estimator/       — Main package
  cli.py             — Typer CLI entrypoint
  pipeline.py        — Orchestrates stages
  models.py          — Pydantic data models
  llm.py             — Claude Code CLI wrapper
  config.py          — Config loading
  report.py          — Markdown report generation
  stages/            — Pipeline stages (extract, architect, estimate, gaps)
config/              — TOML config files (rate card, AWS baselines, settings)
prompts/             — System prompt files for each stage
templates/           — Jinja2 report template
tests/               — pytest tests
```

## Conventions
- Conventional Commits: `type(scope): description` (feat, fix, refactor, test, docs, chore, build)
- TDD: write tests before implementation
- Type hints on all functions
- Ruff for linting and formatting (line length 100)
- Quality over cost — default to higher-tier models

## Commands
```bash
uv run estimate generate <transcript_file>   # Generate estimate
uv run estimate validate-config              # Verify config
uv run estimate version                      # Show version
uv run pytest                                # Run tests
uv run pytest -m "not integration"           # Skip Claude CLI tests
uv run ruff check .                          # Lint
uv run ruff format .                         # Format
```

## Architecture
Staged pipeline: Extract → Architect → Estimate → Gaps → Report
- Each stage produces structured Pydantic output (JSON)
- Raw transcript is dropped after Extract — downstream stages use structured data only
- Intermediate outputs saved to disk for debugging/resume
- Stage failures retry once before bailing

## Key Design Decisions
- Claude Code CLI over Anthropic SDK (uses existing auth, no API key needed)
- Opus for Extract/Estimate stages, Sonnet for Architect/Gaps
- Three-scenario estimates (optimistic/likely/pessimistic) with spread guidelines
- T-shirt sizing with point estimates within ranges
- TOML config (built-in Python 3.11+, no extra dependency)
- Gap analysis is a core feature, not optional
