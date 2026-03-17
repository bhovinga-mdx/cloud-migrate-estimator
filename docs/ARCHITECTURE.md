# Architecture

## Overview

The estimator uses a staged pipeline architecture where each stage performs one focused task, produces structured output, and passes it downstream. The raw transcript is dropped after the first stage — all subsequent stages work from structured Pydantic data only.

## Pipeline

```
Transcript File (.txt/.md)
        |
        v
+---------------+
|  1. EXTRACT   |  Claude Opus — Parse transcript into structured migration facts
+-------+-------+
        |  ExtractionResult (JSON)
        v
+---------------+
|  2. ARCHITECT |  Claude Sonnet — Propose target AWS architecture, t-shirt size
+-------+-------+
        |  ArchitectureResult (JSON)
        v
+---------------+
|  3. ESTIMATE  |  Claude Opus — Roles, hours, 3 scenarios, costs
+-------+-------+
        |  EstimateResult (JSON)
        v
+---------------+
|   4. GAPS     |  Claude Sonnet — Missing info, follow-up questions, risks
+-------+-------+
        |  GapsResult (JSON)
        v
+---------------+
|  5. REPORT    |  No LLM — Jinja2 template assembly
+---------------+
        |
        v
  report.md + stage JSON files
```

## Stage Details

### Stage 1: Extract (Opus)

**Purpose:** Parse raw transcript into structured migration facts.

**Input:** Raw transcript text (piped as part of the prompt)

**Output:** `ExtractionResult` — current environment, migration context, workloads, constraints, raw notes

**Why Opus:** This is the most critical stage. Everything downstream depends on thorough, accurate extraction. Missing information here is lost forever since the raw transcript is dropped.

**Key behavior:**
- Captures ambiguous information in `raw_notes` rather than making assumptions
- Leaves fields null rather than fabricating data
- Extracts implicit information (e.g., mentioning "Oracle" implies licensing costs)

### Stage 2: Architect (Sonnet)

**Purpose:** Propose a target AWS architecture based on the extraction.

**Input:** `ExtractionResult` from stage 1

**Output:** `ArchitectureResult` — strategy, services, narrative, t-shirt size with point estimate, phases

**Why Sonnet:** Architecture proposals are well-bounded by the extraction data. Sonnet provides sufficient quality at lower cost.

**Key behavior:**
- Practical recommendations, not aspirational
- Respects client constraints and preferences
- T-shirt size includes a specific point estimate within the range, not just a band
- Migration phases ordered logically

### Stage 3: Estimate (Opus)

**Purpose:** Produce three-scenario cost and timeline estimates.

**Input:** `ExtractionResult` + `ArchitectureResult` + rate card config

**Output:** `EstimateResult` — roles with hours per scenario, costs, timelines, confidence, assumptions

**Why Opus:** Cost estimation requires careful reasoning about scope, uncertainty, and tradeoffs. Quality directly impacts the usefulness of the tool.

**Key behavior:**
- Only includes roles justified by the scope
- Follows spread guidelines (pessimistic typically 1.5-2.5x optimistic)
- Justifies the spread between scenarios
- Honest about uncertainty — wide range with clear assumptions over false precision

### Stage 4: Gaps (Sonnet)

**Purpose:** Review the estimate for completeness and risk.

**Input:** `ExtractionResult` + `ArchitectureResult` + `EstimateResult`

**Output:** `GapsResult` — gaps, follow-up questions, risk factors, confidence assessment

**Why Sonnet:** Gap analysis is review and critique — Sonnet handles this well.

**Key behavior:**
- Gaps prioritized by impact severity
- Follow-up questions are specific and actionable (not generic)
- Risk factors focus on things that could blow up the estimate
- Honest confidence assessment

### Stage 5: Report (No LLM)

**Purpose:** Assemble all stage outputs into a readable Markdown report.

**Implementation:** Jinja2 template rendering from structured Pydantic data

**Output:** `report.md` with all sections

## Data Flow

```
Stage 1: transcript (large) --> ExtractionResult (compact)
Stage 2: ExtractionResult --> ArchitectureResult
Stage 3: ExtractionResult + ArchitectureResult + RateCard --> EstimateResult
Stage 4: ExtractionResult + ArchitectureResult + EstimateResult --> GapsResult
Stage 5: All results --> report.md (template rendering, no LLM)
```

The raw transcript is only used in Stage 1. After extraction, all stages work with structured Pydantic models. This:
- Keeps context sizes manageable
- Makes stages independently testable
- Prevents downstream stages from being influenced by transcript noise

If the extractor misses something, a `raw_notes` field captures anything relevant that doesn't fit the structured schema.

## Claude Code CLI Integration

The tool uses Claude Code CLI (`claude -p`) for LLM inference rather than the Anthropic Python SDK.

**How it works:**
1. The full prompt (system prompt + JSON schema + user prompt + input text) is assembled in Python
2. Passed to `claude -p <prompt> --model <model> --output-format json`
3. Response JSON is parsed and validated with Pydantic

**Why CLI over SDK:**
- Uses existing Claude Code authentication (no separate API key)
- Simpler setup for team members who already have Claude Code installed

**Mitigations for CLI limitations:**
- Full prompt built in Python and passed via `-p` to avoid Windows command line length limits
- JSON schema embedded in the prompt text (not via `--json-schema` flag) to avoid argument length issues
- Markdown code fences stripped from responses before JSON parsing
- Retry logic (configurable, default 1 retry) on stage failure
- 10-minute timeout per stage

**Known limitation:** No control over temperature or max_tokens. If output consistency becomes an issue, switching to the Anthropic SDK is the recommended fix.

## Configuration

All configuration is in TOML format (built into Python 3.11+, no extra dependency).

```
config/
  rate_card.toml       # Role titles and hourly rates
  aws_baselines.toml   # T-shirt size definitions and cost ranges
  settings.toml        # Model tiers, pipeline params, output settings
```

### Rate Card (`rate_card.toml`)
```toml
[roles.solutions_architect]
title = "Solutions Architect"
hourly_rate = 250
```

### AWS Baselines (`aws_baselines.toml`)
```toml
[sizes.M]
label = "Medium"
description = "10-50 workloads, moderate complexity"
monthly_cost_low = 5000
monthly_cost_high = 25000
```

### Settings (`settings.toml`)
```toml
[models]
extract = "claude-opus-4-6"    # Highest quality for extraction
architect = "claude-sonnet-4-6"
estimate = "claude-opus-4-6"   # Highest quality for estimation
gaps = "claude-sonnet-4-6"

[pipeline]
max_retries = 1
max_transcript_chars = 400000

[output]
output_dir = "estimates"
save_intermediates = true
```

## Output Structure

```
estimates/
  {timestamp}_{client_name}/
    report.md                  # Final Markdown report
    stages/
      01_extraction.json       # Stage 1 structured output
      02_architecture.json     # Stage 2 structured output
      03_estimate.json         # Stage 3 structured output
      04_gaps.json             # Stage 4 structured output
```

Intermediate outputs are always saved (configurable). This enables:
- Debugging which stage produced unexpected results
- Resuming from a specific stage if one fails
- Comparing outputs across runs

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Empty transcript | Fail with clear error before any Claude calls |
| Oversized transcript | Fail with error showing character count vs limit |
| Claude CLI returns non-zero | Retry up to `max_retries` times, then fail with stderr |
| Claude returns invalid JSON | Retry once, then fail with raw response snippet |
| Stage timeout (10 min) | Fail with timeout error for that stage |
| Unsupported file format | Fail before pipeline starts |

## Data Models

All stage inputs and outputs are defined as Pydantic v2 models in `src/estimator/models.py`. Key models:

- `ExtractionResult` — Stage 1 output (environment, context, workloads, constraints)
- `ArchitectureResult` — Stage 2 output (strategy, services, t-shirt size, phases)
- `EstimateResult` — Stage 3 output (roles, three-scenario costs, timelines, assumptions)
- `GapsResult` — Stage 4 output (gaps, questions, risks, confidence)

Each model supports:
- JSON serialization/deserialization (`model_dump_json()` / `model_validate_json()`)
- JSON schema generation (`model_json_schema()`) for prompt embedding
- Default values for optional fields to handle missing information gracefully
