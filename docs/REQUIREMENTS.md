# Requirements

## Functional Requirements (POC)

### FR1 — Transcript Ingestion
- Accept a transcript file as input
- Supported formats: TXT, MD
- Validate file exists, is readable, and is not empty
- Reject transcripts exceeding configurable size limit (default 400K characters)

### FR2 — Information Extraction
- Extract migration-relevant details from the transcript:
  - Current environment (infrastructure type, OS, databases, applications, networking, storage)
  - Migration drivers and pain points
  - Timeline and budget expectations or constraints
  - Compliance and security requirements
  - Workload details (count, data volumes, criticality, dependencies)
  - Technical constraints or preferences
  - Stakeholders mentioned
- Flag ambiguous or contradictory information
- Do not infer or fabricate missing information — leave fields null

### FR3 — Architecture Design
- Propose a high-level target AWS architecture based on extracted requirements
- Select a migration strategy (lift-and-shift, re-platform, re-architect, or mixed) with justification
- Identify target AWS services and their purpose
- T-shirt size the AWS environment (S/M/L/XL) with:
  - Cost range based on baseline definitions
  - Point estimate within the range with justification
- Define migration phases in logical execution order

### FR4 — Resource Planning
- Determine required roles based on migration scope (from rate card)
- Estimate hours per role for each of three scenarios
- Apply hourly rates from static rate card configuration

### FR5 — Estimate Generation
- Three-scenario estimate: optimistic, likely, pessimistic
  - Optimistic: everything goes smoothly, minimal unknowns
  - Likely: normal friction, some discovery during migration
  - Pessimistic: significant unknowns surface, scope creep, technical debt
  - Pessimistic should typically be 1.5-2.5x the optimistic estimate
- Each scenario includes:
  - Labor cost (hours x rates)
  - AWS monthly run-rate estimate (from t-shirt sizing)
  - AWS first-year cost (monthly x 12)
  - Total first-year cost (labor + AWS first year)
  - Timeline in weeks
- Confidence percentage with justification
- Spread justification explaining why the range is wide or narrow
- List of key assumptions driving the numbers

### FR6 — Report Output
- Structured Markdown report with sections:
  - Executive summary with scenario comparison table
  - Scope and current environment
  - Target architecture (strategy, services, narrative, phases)
  - Resource plan and cost breakdown
  - Timeline with scenario descriptions
  - Assumptions
  - Gap analysis
- Output to a directory: `./estimates/{timestamp}_{client_name}/`
- Include intermediate stage outputs as JSON files for debugging

### FR7 — Gap Analysis
- Identify missing information that would improve estimate confidence
- Categorize gaps by severity (high, medium, low)
- Describe the impact of each gap on the estimate
- Suggest specific, actionable follow-up questions with rationale and priority
- Provide overall confidence narrative
- List risk factors that could significantly impact the estimate

## Non-Functional Requirements (POC)

### NFR1 — Performance
- Generate complete estimate within 2-10 minutes

### NFR2 — Extensibility
- Architecture should allow adding other service types (app modernization, data analytics, etc.) without rewriting core pipeline logic

### NFR3 — Configurability
- Rate card stored as static TOML config (updatable without code changes)
- Model selection per stage stored in config
- AWS t-shirt size baselines stored in config
- Pipeline parameters (retries, timeouts, size limits) stored in config

### NFR4 — Reproducibility
- Same transcript and config should produce consistent (not necessarily identical) estimates
- Intermediate stage outputs saved for debugging and comparison

## Documented for Later

These items are explicitly out of scope for the POC but documented for future consideration:

| Item | Context | Priority |
|------|---------|----------|
| Multiple transcript support | Some prospects have multiple calls before an estimate | Medium |
| Transcript quality detection | Bad audio = bad transcript = bad estimate; warn when quality is low | Low |
| External client research | Research company size, industry, tech stack to inform estimates | Medium |
| Output iteration | Adjust estimates based on follow-up info ("assume 50 servers instead of 20") | Medium |
| Privacy/security legal review | Transcripts contain sensitive client info sent to AI APIs | High (before production) |
| Live call participation | AI joins calls via voice, asks questions in real-time | Long-term vision |
| Other service types | App modernization, data analytics, cloud-native dev, AI dev, managed services | Phase 2+ |
| Historical data training | Use past estimates and actuals to improve accuracy | Phase 2+ |
| Branded proposal templates | Mindex-branded output ready to send to clients | Low |
| Web UI | Browser-based interface for non-technical team members | Phase 2 |

## Input Specification

**Transcript file:**
- Format: Plain text (`.txt`) or Markdown (`.md`)
- Content: Sales call transcript with speaker labels and dialogue
- Size: Up to ~400K characters (configurable)

**Rate card (static config):**
- Format: TOML
- Content: Role keys mapped to title and hourly rate

## Output Specification

**Report:**
- Format: Markdown (`.md`)
- Location: `./estimates/{timestamp}_{client_name}/report.md`

**Intermediate outputs:**
- Format: JSON
- Location: `./estimates/{timestamp}_{client_name}/stages/0{n}_{stage_name}.json`
- Files: `01_extraction.json`, `02_architecture.json`, `03_estimate.json`, `04_gaps.json`
