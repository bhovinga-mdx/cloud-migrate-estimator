"""Tests for Pydantic data models."""

from estimator.models import (
    ArchitectureResult,
    EstimateResult,
    ExtractionResult,
    GapsResult,
)


class TestExtractionResult:
    def test_defaults(self):
        result = ExtractionResult()
        assert result.current_environment.infrastructure_type is None
        assert result.workloads == []
        assert result.raw_notes == []

    def test_full_construction(self, sample_extraction):
        assert sample_extraction.current_environment.infrastructure_type == "on-prem"
        assert len(sample_extraction.current_environment.databases) == 2
        assert len(sample_extraction.workloads) == 1
        assert sample_extraction.workloads[0].estimated_count == 15

    def test_json_roundtrip(self, sample_extraction):
        json_str = sample_extraction.model_dump_json()
        reloaded = ExtractionResult.model_validate_json(json_str)
        assert reloaded == sample_extraction

    def test_schema_generation(self):
        schema = ExtractionResult.model_json_schema()
        assert "properties" in schema
        assert "current_environment" in schema["properties"]


class TestArchitectureResult:
    def test_tshirt_point_estimate(self, sample_architecture):
        ts = sample_architecture.tshirt_size
        assert ts.estimated_monthly_cost_low <= ts.point_estimate_monthly <= ts.estimated_monthly_cost_high

    def test_phases_ordered(self, sample_architecture):
        orders = [p.order for p in sample_architecture.phases]
        assert orders == sorted(orders)

    def test_json_roundtrip(self, sample_architecture):
        json_str = sample_architecture.model_dump_json()
        reloaded = ArchitectureResult.model_validate_json(json_str)
        assert reloaded == sample_architecture


class TestEstimateResult:
    def test_three_scenarios_exist(self, sample_estimate):
        assert sample_estimate.optimistic.total_first_year > 0
        assert sample_estimate.likely.total_first_year > 0
        assert sample_estimate.pessimistic.total_first_year > 0

    def test_scenarios_ordered(self, sample_estimate):
        assert (
            sample_estimate.optimistic.total_first_year
            <= sample_estimate.likely.total_first_year
            <= sample_estimate.pessimistic.total_first_year
        )

    def test_timelines_ordered(self, sample_estimate):
        assert (
            sample_estimate.timeline_optimistic.duration_weeks
            <= sample_estimate.timeline_likely.duration_weeks
            <= sample_estimate.timeline_pessimistic.duration_weeks
        )

    def test_confidence_range(self, sample_estimate):
        assert 0 < sample_estimate.confidence_percentage <= 100

    def test_json_roundtrip(self, sample_estimate):
        json_str = sample_estimate.model_dump_json()
        reloaded = EstimateResult.model_validate_json(json_str)
        assert reloaded == sample_estimate


class TestGapsResult:
    def test_has_gaps(self, sample_gaps):
        assert len(sample_gaps.gaps) > 0
        assert sample_gaps.gaps[0].severity in ("high", "medium", "low")

    def test_has_questions(self, sample_gaps):
        assert len(sample_gaps.follow_up_questions) > 0

    def test_json_roundtrip(self, sample_gaps):
        json_str = sample_gaps.model_dump_json()
        reloaded = GapsResult.model_validate_json(json_str)
        assert reloaded == sample_gaps
