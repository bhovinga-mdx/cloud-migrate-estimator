# Development Guide

## Tech Stack

| Component | Choice | Justification |
|-----------|--------|---------------|
| Language | Python 3.12+ | Best AI SDK support, fast prototyping |
| CLI framework | Typer | Modern, less boilerplate than Click |
| Data models | Pydantic v2 | Structured validation, JSON schema generation |
| Report engine | Jinja2 | Template separation, loops/conditionals for tables |
| Console output | Rich | Colored progress output |
| Config format | TOML | Built into Python 3.11+, no dependency |
| Package manager | uv | Fast, simple, modern |
| Linting/formatting | Ruff | Fast, replaces flake8/black/isort |
| Testing | pytest | Standard, with markers for integration tests |
| AI inference | Claude Code CLI | Uses existing auth, no API key needed |

## Project Structure

```
cloud-migrate-estimator/
├── CLAUDE.md              # Project conventions for Claude Code sessions
├── pyproject.toml          # Project config, dependencies, tool settings
├── config/
│   ├── rate_card.toml      # Role titles and hourly rates
│   ├── aws_baselines.toml  # T-shirt size definitions
│   └── settings.toml       # Model tiers, pipeline params
├── prompts/
│   ├── extract.md          # Stage 1 system prompt
│   ├── architect.md        # Stage 2 system prompt
│   ├── estimate.md         # Stage 3 system prompt
│   └── gaps.md             # Stage 4 system prompt
├── templates/
│   └── report.md.j2        # Jinja2 report template
├── src/estimator/
│   ├── __init__.py          # Version
│   ├── cli.py               # Typer CLI entrypoint
│   ├── pipeline.py          # Stage orchestration
│   ├── models.py            # Pydantic data models
│   ├── llm.py               # Claude Code CLI wrapper
│   ├── config.py            # TOML config loading
│   ├── report.py            # Jinja2 report rendering
│   └── stages/
│       ├── extract.py       # Stage 1: transcript → structured data
│       ├── architect.py     # Stage 2: extraction → architecture
│       ├── estimate.py      # Stage 3: extraction + arch → costs
│       └── gaps.py          # Stage 4: all → gaps and risks
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── fixtures/
│   │   └── sample_transcript.txt
│   ├── test_models.py
│   ├── test_config.py
│   ├── test_llm.py
│   ├── test_stages.py
│   ├── test_pipeline.py
│   ├── test_report.py
│   └── test_cli.py
└── docs/                    # Project documentation
```

## Setup

```bash
# Clone the repo
git clone https://github.com/bhovinga-mdx/cloud-migrate-estimator.git
cd cloud-migrate-estimator

# Install dependencies
uv sync

# Verify config
uv run estimate validate-config

# Verify tests pass
uv run pytest
```

### Prerequisites

- Python 3.12+
- uv (package manager): `pip install uv`
- Claude Code CLI: must be installed and authenticated (`claude --version`)

## Usage

```bash
# Generate an estimate from a transcript
uv run estimate generate path/to/transcript.txt

# With verbose progress output
uv run estimate generate path/to/transcript.txt -v

# Custom output directory
uv run estimate generate path/to/transcript.txt -o ./my-output

# Custom config directory
uv run estimate generate path/to/transcript.txt -c ./my-config

# Validate config files
uv run estimate validate-config

# Show version
uv run estimate version
```

## Development Process

### Commit Conventions

[Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description

Optional body

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`

Examples:
- `feat(extract): add support for multi-speaker identification`
- `fix(llm): handle Unicode in Claude CLI output on Windows`
- `refactor(pipeline): simplify stage error handling`

### Testing Strategy

**Unit tests (mocked Claude):**
- Test data models, config loading, report rendering, CLI commands
- Test stage functions with mocked `call_claude` responses
- Test LLM wrapper with mocked `subprocess.run`
- Fast, deterministic, no external dependencies
- Run: `uv run pytest`

**Integration tests (live Claude):**
- Test full pipeline against sample transcript with real Claude calls
- Marked with `@pytest.mark.integration`
- Slow (minutes), non-deterministic, requires Claude Code CLI
- Run: `uv run pytest -m integration`
- Skip: `uv run pytest -m "not integration"`

**Prompt evaluation (manual):**
- Review generated reports for quality
- Compare outputs across runs for consistency
- This is where quality lives or dies — no automated substitute

### Code Style

- **Ruff** for linting and formatting
- Line length: 100 (source), unlimited (tests)
- Type hints on all functions
- Lint rules: E, F, I, N, W, UP

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Auto-fix lint issues
uv run ruff check --fix .
```

### Adding a New Service Type

The pipeline is designed for extensibility. To add a new service type (e.g., App Modernization):

1. Create new prompt files in `prompts/` (or reuse existing ones with modifications)
2. Extend or create new Pydantic models in `models.py` if the service type needs different data structures
3. Create new stage implementations in `stages/` if the estimation logic differs
4. Add a new Jinja2 template in `templates/` if the report format differs
5. Update the CLI to accept a `--service-type` flag
6. Add config for the new type in `config/`

### Modifying Prompts

Stage prompts are stored as Markdown files in `prompts/`. Edit these directly — no Python code changes needed to adjust prompt behavior. The prompts are read at runtime.

### Modifying the Report Template

The report template is `templates/report.md.j2`. It uses Jinja2 syntax with access to all stage output models. Edit the template to change report structure or formatting without touching Python code.

### Modifying Rates

Edit `config/rate_card.toml` directly. No code changes needed. Run `uv run estimate validate-config` to verify.
