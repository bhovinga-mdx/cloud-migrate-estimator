"""Pydantic models for pipeline stage inputs and outputs."""

from pydantic import BaseModel

# --- Stage 1: Extract ---


class CurrentEnvironment(BaseModel):
    infrastructure_type: str | None = None  # on-prem, cloud, hybrid
    operating_systems: list[str] = []
    databases: list[str] = []
    applications: list[str] = []
    networking: str | None = None
    storage: str | None = None


class MigrationContext(BaseModel):
    drivers: list[str] = []
    pain_points: list[str] = []
    timeline_expectations: str | None = None
    budget_constraints: str | None = None
    compliance_requirements: list[str] = []
    stakeholders_mentioned: list[str] = []


class WorkloadProfile(BaseModel):
    estimated_count: int | None = None
    description: str = ""
    data_volume: str | None = None
    criticality: str | None = None  # high, medium, low
    dependencies: list[str] = []


class ExtractionResult(BaseModel):
    current_environment: CurrentEnvironment = CurrentEnvironment()
    migration_context: MigrationContext = MigrationContext()
    workloads: list[WorkloadProfile] = []
    technical_constraints: list[str] = []
    raw_notes: list[str] = []


# --- Stage 2: Architect ---


class AWSService(BaseModel):
    service: str
    purpose: str
    configuration_notes: str | None = None


class MigrationPhase(BaseModel):
    name: str
    description: str
    order: int


class TShirtSize(BaseModel):
    size: str  # S, M, L, XL
    justification: str
    estimated_monthly_cost_low: int
    estimated_monthly_cost_high: int
    point_estimate_monthly: int  # best guess within range


class ArchitectureResult(BaseModel):
    migration_strategy: str  # lift-and-shift, re-platform, re-architect, mixed
    strategy_justification: str
    target_services: list[AWSService] = []
    architecture_narrative: str = ""
    tshirt_size: TShirtSize
    phases: list[MigrationPhase] = []


# --- Stage 3: Estimate ---


class RoleEstimate(BaseModel):
    role: str  # must match rate card key
    title: str
    hours_optimistic: int
    hours_likely: int
    hours_pessimistic: int
    justification: str


class ScenarioCost(BaseModel):
    labor_cost: int
    aws_monthly_cost: int
    aws_first_year_cost: int
    total_first_year: int


class TimelineScenario(BaseModel):
    duration_weeks: int
    description: str


class EstimateResult(BaseModel):
    roles: list[RoleEstimate] = []
    optimistic: ScenarioCost
    likely: ScenarioCost
    pessimistic: ScenarioCost
    timeline_optimistic: TimelineScenario
    timeline_likely: TimelineScenario
    timeline_pessimistic: TimelineScenario
    confidence_percentage: int  # e.g., 60 means +/- 40%
    key_assumptions: list[str] = []
    spread_justification: str = ""


# --- Stage 4: Gaps ---


class GapItem(BaseModel):
    category: str  # infrastructure, compliance, timeline, etc.
    description: str
    impact: str
    severity: str  # high, medium, low


class FollowUpQuestion(BaseModel):
    question: str
    rationale: str
    priority: str  # high, medium, low


class GapsResult(BaseModel):
    gaps: list[GapItem] = []
    follow_up_questions: list[FollowUpQuestion] = []
    overall_confidence: str = ""
    risk_factors: list[str] = []
