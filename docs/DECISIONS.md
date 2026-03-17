# Decision Log

## Key Design Decisions

### 1. Staged Pipeline over Single Prompt

**Decision:** Break the estimation into 4 sequential Claude calls (Extract → Architect → Estimate → Gaps) instead of a single monolithic prompt.

**Options considered:**
| Option | Pros | Cons |
|--------|------|------|
| Single prompt | Simpler, fewer API calls | Lower quality, hard to debug, can't tier models |
| Staged pipeline | Better quality per stage, debuggable, testable, supports model tiering | More API calls, slightly slower |

**Outcome:** Staged pipeline. Quality is the top priority, and the pipeline maps cleanly to requirements. Each stage does one thing well and is independently testable.

---

### 2. Claude Code CLI over Anthropic Python SDK

**Decision:** Use `claude -p` for LLM inference instead of the `anthropic` Python SDK.

**Options considered:**
| Option | Pros | Cons |
|--------|------|------|
| Anthropic SDK | Full parameter control, typed exceptions, easy to mock | Requires separate API key setup |
| Claude Code CLI | Uses existing auth, no API key, team already has it | No temperature/max_tokens control, subprocess management |

**Outcome:** CLI, per user preference. The team already has Claude Code installed and authenticated.

**Concerns noted (revisit if):**
- Output consistency becomes an issue (no temperature control)
- Complex JSON schemas cause parsing failures
- Performance bottlenecks from subprocess overhead

**Workarounds implemented:**
- Full prompt built in Python to avoid Windows command line length limits
- JSON schema embedded in prompt text instead of `--json-schema` flag
- Markdown code fence stripping on responses
- Retry logic on failures

---

### 3. Opus for Extract/Estimate, Sonnet for Architect/Gaps

**Decision:** Use higher-tier models for the stages with the most impact on output quality.

**Rationale:**
- **Extract (Opus):** Most critical — missed information is permanently lost since the transcript is dropped after this stage
- **Estimate (Opus):** Core deliverable — cost/timeline accuracy directly determines the tool's value
- **Architect (Sonnet):** Well-bounded by extraction data, Sonnet handles this adequately
- **Gaps (Sonnet):** Review and critique work, Sonnet is sufficient

**Override:** User specified "default to too high of a tier, quality is more important than cost minimization." If in doubt, use Opus.

---

### 4. Drop Raw Transcript After Extraction

**Decision:** Stage 1 extracts structured data, and downstream stages never see the raw transcript.

**Options considered:**
| Option | Pros | Cons |
|--------|------|------|
| Pass full transcript to all stages | Downstream can recover missed info | Context grows unbounded, expensive |
| Drop after extraction | Context stays manageable, stages work with clean data | Extractor misses = permanent loss |
| Configurable | Flexible | Complexity |

**Outcome:** Drop after extraction. Mitigated by:
- Using Opus for extraction (highest quality)
- Including a `raw_notes` catch-all field for anything that doesn't fit the schema
- Thorough extraction prompt design

---

### 5. Three-Scenario Estimates with Spread Guidelines

**Decision:** Optimistic / Likely / Pessimistic with spread guidelines and required justification.

**Options considered:**
| Option | Pros | Cons |
|--------|------|------|
| Single estimate with +/- % | Simpler | Less useful for discussion |
| Three scenarios | More nuanced, better for internal review | AI spread could be arbitrary |

**Outcome:** Three scenarios with guidelines (pessimistic typically 1.5-2.5x optimistic) and required justification for the spread. This makes estimates internally consistent and explainable.

---

### 6. TOML over YAML for Configuration

**Decision:** Use TOML for all config files.

**Options considered:**
| Option | Pros | Cons |
|--------|------|------|
| YAML | Widely used, readable | Requires PyYAML dependency |
| TOML | Built into Python 3.11+, no dependency, readable | Less familiar to some |
| JSON | No dependency | Worse for human editing, no comments |

**Outcome:** TOML. Eliminates a dependency, built into Python, and perfectly readable for config files.

---

### 7. T-Shirt Sizing with Point Estimates

**Decision:** AI picks a t-shirt size AND provides a specific monthly cost estimate within the range.

**Options considered:**
| Option | Pros | Cons |
|--------|------|------|
| T-shirt size only (range) | Simple | Ranges too broad to be useful (S is $1K-$5K = 5x) |
| Point estimate only | Precise | False precision without enough data |
| Both | Best of both worlds | Slightly more complex |

**Outcome:** Both. The range communicates uncertainty, the point estimate gives a best guess for calculations.

---

### 8. CLI Tool over Web App

**Decision:** Build a command-line tool, not a web application.

**Options considered:**
| Option | Pros | Cons |
|--------|------|------|
| CLI | Simplest to build, fastest POC | Technical users only |
| Web app | Accessible to anyone | More infrastructure |
| API + frontend | Clean separation | More work |

**Outcome:** CLI. User decided to limit to technical team members. A web UI is documented for later if non-technical users need access.

**Pushback given:** CLI limits adoption to technical staff. User accepted the tradeoff.

---

### 9. Python + Typer

**Decision:** Python with Typer for the CLI framework.

**Options considered:**
| Option | Pros | Cons |
|--------|------|------|
| Python | Best AI SDK support, fast to prototype | Slower runtime |
| Node/TypeScript | Good SDK, strong if team is JS-heavy | Less natural for CLI |
| Go | Fast binaries, great CLI libs | Community SDK, more boilerplate |

**Outcome:** Python. Natural choice for an AI-heavy CLI — best SDK support, fastest to prototype. Runtime performance is irrelevant since the bottleneck is API latency.

CLI framework: Typer (modern, less boilerplate than Click).

---

### 10. Jinja2 for Report Generation

**Decision:** Use Jinja2 templates for the Markdown report, not Python string formatting.

**Rationale:** The report has loops (roles table, services table), conditionals (optional sections), and formatting (number formatting). Jinja2 handles this cleanly and keeps the template editable without touching Python code.

---

### 11. Intermediate Output Persistence

**Decision:** Always save stage JSON outputs alongside the report.

**Rationale:** Essential for debugging which stage produced unexpected results. Also enables future resume-from-stage functionality. The disk cost is negligible.

---

### 12. Gap Analysis as Core Feature

**Decision:** Gap analysis (Stage 4) is a required, non-optional part of every estimate.

**Rationale:** User explicitly identified this as "very important." The follow-up questions and risk identification are arguably as valuable as the estimate itself — they guide the next conversation with the client and improve estimate confidence over iterations.

## Identified Risks and Mitigations

These were identified during the design review ("poking holes") phase:

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Windows command line length limits with long prompts | Build full prompt in Python, pass via `-p` | Resolved |
| 2 | No temperature/max_tokens control via CLI | Accept for POC; switch to SDK if consistency issues arise | Accepted |
| 3 | Complex JSON schema validation failures | Schema embedded in prompt + Pydantic validation + retry | Resolved |
| 4 | Pipeline stage failure with no recovery | Intermediate outputs saved to disk for debugging | Resolved |
| 5 | Jinja2 dependency justified? | Yes — report has loops, conditionals, formatting | Resolved |
| 6 | YAML dependency unnecessary | Switched to TOML (built into Python 3.11+) | Resolved |
| 7 | Generated sample transcript too clean | Created deliberately messy, realistic transcript | Resolved |
| 8 | T-shirt sizing ranges too broad | Added point estimate within range with justification | Resolved |
| 9 | Three-scenario spread arbitrary | Added spread guidelines + required justification | Resolved |
| 10 | No debugging for bad stage output | Always save intermediate JSON + `--verbose` flag | Resolved |
| 11 | Output file location undefined | `./estimates/{timestamp}_{client_name}/` | Resolved |
| 12 | Project structure over-engineered for POC | Kept — stages are independently testable, extensibility is a requirement | Accepted |
| 13 | Transcript size limits | Fail with clear error on oversized transcripts | Resolved |
| 14 | CLI lacks `validate-config` and `version` commands | Added both | Resolved |
