"""Shared test fixtures."""

from pathlib import Path
from unittest.mock import patch

import pytest

from estimator.config import (
    AWSBaselinesConfig,
    ModelsConfig,
    OutputConfig,
    PipelineConfig,
    RateCardConfig,
    RoleConfig,
    SettingsConfig,
    TShirtSizeConfig,
)
from estimator.models import (
    ArchitectureResult,
    AWSService,
    CurrentEnvironment,
    EstimateResult,
    ExtractionResult,
    FollowUpQuestion,
    GapItem,
    GapsResult,
    MigrationContext,
    MigrationPhase,
    RoleEstimate,
    ScenarioCost,
    TimelineScenario,
    TShirtSize,
    WorkloadProfile,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_transcript() -> str:
    return (FIXTURES_DIR / "sample_transcript.txt").read_text(encoding="utf-8")


@pytest.fixture
def rate_card() -> RateCardConfig:
    return RateCardConfig(
        roles={
            "solutions_architect": RoleConfig(title="Solutions Architect", hourly_rate=250),
            "cloud_engineer": RoleConfig(title="Cloud Engineer", hourly_rate=200),
            "devops_engineer": RoleConfig(title="DevOps Engineer", hourly_rate=200),
            "project_manager": RoleConfig(title="Project Manager", hourly_rate=175),
        }
    )


@pytest.fixture
def aws_baselines() -> AWSBaselinesConfig:
    return AWSBaselinesConfig(
        sizes={
            "S": TShirtSizeConfig(
                label="Small",
                description="< 10 workloads",
                monthly_cost_low=1000,
                monthly_cost_high=5000,
                typical_workload_count="1-9",
            ),
            "M": TShirtSizeConfig(
                label="Medium",
                description="10-50 workloads",
                monthly_cost_low=5000,
                monthly_cost_high=25000,
                typical_workload_count="10-50",
            ),
        }
    )


@pytest.fixture
def settings() -> SettingsConfig:
    return SettingsConfig(
        models=ModelsConfig(),
        pipeline=PipelineConfig(),
        output=OutputConfig(output_dir="test_estimates", save_intermediates=True),
    )


@pytest.fixture
def sample_extraction() -> ExtractionResult:
    return ExtractionResult(
        current_environment=CurrentEnvironment(
            infrastructure_type="on-prem",
            operating_systems=["Windows Server 2016", "Red Hat Enterprise Linux 7"],
            databases=["SQL Server 2016", "Oracle 12c"],
            applications=["ERP System", "Customer Portal", "Internal HR App"],
            networking="Traditional VLAN-based, single data center",
            storage="NetApp SAN, ~50TB total",
        ),
        migration_context=MigrationContext(
            drivers=["Data center lease expiring Q4 2026", "Cost reduction"],
            pain_points=["Hardware refresh overdue", "Scaling difficulties"],
            timeline_expectations="Complete by Q4 2026",
            budget_constraints="Under $500K total",
            compliance_requirements=["SOC 2 Type II"],
            stakeholders_mentioned=["Acme Corp", "John Smith (CTO)"],
        ),
        workloads=[
            WorkloadProfile(
                estimated_count=15,
                description="Mixed application portfolio",
                data_volume="~50TB",
                criticality="high",
                dependencies=["Active Directory", "On-prem DNS"],
            )
        ],
        technical_constraints=["Must maintain VPN connectivity during migration"],
        raw_notes=["CTO mentioned potential Oracle license renegotiation"],
    )


@pytest.fixture
def sample_architecture() -> ArchitectureResult:
    return ArchitectureResult(
        migration_strategy="re-platform",
        strategy_justification="Re-platforming allows leveraging managed AWS services while minimizing application rewrite effort.",
        target_services=[
            AWSService(service="EC2", purpose="Application hosting", configuration_notes="m6i instances, multi-AZ"),
            AWSService(service="RDS", purpose="SQL Server and PostgreSQL databases", configuration_notes="Multi-AZ deployment"),
            AWSService(service="S3", purpose="Object storage and backups"),
            AWSService(service="VPC", purpose="Network isolation and VPN connectivity"),
        ],
        architecture_narrative="The target architecture uses a multi-AZ VPC with managed RDS for databases and EC2 for application hosting.",
        tshirt_size=TShirtSize(
            size="M",
            justification="15 workloads with moderate complexity and 50TB data",
            estimated_monthly_cost_low=5000,
            estimated_monthly_cost_high=25000,
            point_estimate_monthly=12000,
        ),
        phases=[
            MigrationPhase(name="Assessment", description="Detailed discovery and planning", order=1),
            MigrationPhase(name="Pilot", description="Migrate 2-3 non-critical workloads", order=2),
            MigrationPhase(name="Migration", description="Migrate remaining workloads in waves", order=3),
            MigrationPhase(name="Optimization", description="Post-migration tuning", order=4),
        ],
    )


@pytest.fixture
def sample_estimate() -> EstimateResult:
    return EstimateResult(
        roles=[
            RoleEstimate(
                role="solutions_architect", title="Solutions Architect",
                hours_optimistic=120, hours_likely=160, hours_pessimistic=240,
                justification="Architecture design and migration planning",
            ),
            RoleEstimate(
                role="cloud_engineer", title="Cloud Engineer",
                hours_optimistic=300, hours_likely=450, hours_pessimistic=650,
                justification="Infrastructure setup and workload migration",
            ),
        ],
        optimistic=ScenarioCost(labor_cost=90000, aws_monthly_cost=10000, aws_first_year_cost=120000, total_first_year=210000),
        likely=ScenarioCost(labor_cost=130000, aws_monthly_cost=12000, aws_first_year_cost=144000, total_first_year=274000),
        pessimistic=ScenarioCost(labor_cost=200000, aws_monthly_cost=15000, aws_first_year_cost=180000, total_first_year=380000),
        timeline_optimistic=TimelineScenario(duration_weeks=12, description="Smooth migration"),
        timeline_likely=TimelineScenario(duration_weeks=18, description="Normal friction"),
        timeline_pessimistic=TimelineScenario(duration_weeks=28, description="Significant issues"),
        confidence_percentage=60,
        key_assumptions=["Client provides timely access to systems", "No major application refactoring needed"],
        spread_justification="Wide spread due to unknown application dependencies and Oracle licensing complexity.",
    )


@pytest.fixture
def sample_gaps() -> GapsResult:
    return GapsResult(
        gaps=[
            GapItem(
                category="infrastructure",
                description="No details on network bandwidth requirements",
                impact="Could affect data transfer timeline and costs",
                severity="high",
            ),
        ],
        follow_up_questions=[
            FollowUpQuestion(
                question="What is the current peak network throughput between data center and cloud?",
                rationale="Determines data transfer strategy and timeline",
                priority="high",
            ),
        ],
        overall_confidence="Moderate confidence. Key unknowns around Oracle licensing and application dependencies could significantly shift the estimate.",
        risk_factors=["Oracle license migration complexity", "Unknown application interdependencies"],
    )


def mock_claude_response(return_data: dict):
    """Create a patch for call_claude that returns specified data."""
    return patch("estimator.llm.call_claude", return_value=return_data)
