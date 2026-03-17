"""Tests for pipeline stages (mocked Claude responses)."""

from unittest.mock import patch

from estimator.models import (
    ArchitectureResult,
    EstimateResult,
    ExtractionResult,
    GapsResult,
)
from estimator.stages.architect import run_architect
from estimator.stages.estimate import run_estimate
from estimator.stages.extract import run_extract
from estimator.stages.gaps import run_gaps


class TestExtractStage:
    @patch("estimator.stages.extract.call_claude")
    def test_returns_extraction_result(self, mock_claude, sample_extraction):
        mock_claude.return_value = sample_extraction.model_dump()
        result = run_extract("fake transcript text")
        assert isinstance(result, ExtractionResult)
        assert result.current_environment.infrastructure_type == "on-prem"

    @patch("estimator.stages.extract.call_claude")
    def test_passes_transcript_as_input(self, mock_claude, sample_extraction):
        mock_claude.return_value = sample_extraction.model_dump()
        run_extract("my transcript content")
        call_kwargs = mock_claude.call_args[1]
        assert call_kwargs["input_text"] == "my transcript content"

    @patch("estimator.stages.extract.call_claude")
    def test_uses_specified_model(self, mock_claude, sample_extraction):
        mock_claude.return_value = sample_extraction.model_dump()
        run_extract("transcript", model="claude-opus-4-6")
        call_kwargs = mock_claude.call_args[1]
        assert call_kwargs["model"] == "claude-opus-4-6"


class TestArchitectStage:
    @patch("estimator.stages.architect.call_claude")
    def test_returns_architecture_result(self, mock_claude, sample_extraction, sample_architecture):
        mock_claude.return_value = sample_architecture.model_dump()
        result = run_architect(sample_extraction)
        assert isinstance(result, ArchitectureResult)
        assert result.migration_strategy == "re-platform"

    @patch("estimator.stages.architect.call_claude")
    def test_includes_extraction_in_prompt(self, mock_claude, sample_extraction, sample_architecture):
        mock_claude.return_value = sample_architecture.model_dump()
        run_architect(sample_extraction)
        call_kwargs = mock_claude.call_args[1]
        assert "EXTRACTED MIGRATION DETAILS" in call_kwargs["prompt"]


class TestEstimateStage:
    @patch("estimator.stages.estimate.call_claude")
    def test_returns_estimate_result(self, mock_claude, sample_extraction, sample_architecture, sample_estimate, rate_card):
        mock_claude.return_value = sample_estimate.model_dump()
        result = run_estimate(sample_extraction, sample_architecture, rate_card)
        assert isinstance(result, EstimateResult)
        assert result.likely.total_first_year > 0

    @patch("estimator.stages.estimate.call_claude")
    def test_includes_rate_card_in_prompt(self, mock_claude, sample_extraction, sample_architecture, sample_estimate, rate_card):
        mock_claude.return_value = sample_estimate.model_dump()
        run_estimate(sample_extraction, sample_architecture, rate_card)
        call_kwargs = mock_claude.call_args[1]
        assert "RATE CARD" in call_kwargs["prompt"]


class TestGapsStage:
    @patch("estimator.stages.gaps.call_claude")
    def test_returns_gaps_result(self, mock_claude, sample_extraction, sample_architecture, sample_estimate, sample_gaps):
        mock_claude.return_value = sample_gaps.model_dump()
        result = run_gaps(sample_extraction, sample_architecture, sample_estimate)
        assert isinstance(result, GapsResult)
        assert len(result.gaps) > 0

    @patch("estimator.stages.gaps.call_claude")
    def test_includes_all_prior_stages(self, mock_claude, sample_extraction, sample_architecture, sample_estimate, sample_gaps):
        mock_claude.return_value = sample_gaps.model_dump()
        run_gaps(sample_extraction, sample_architecture, sample_estimate)
        call_kwargs = mock_claude.call_args[1]
        prompt = call_kwargs["prompt"]
        assert "EXTRACTED DETAILS" in prompt
        assert "TARGET ARCHITECTURE" in prompt
        assert "ESTIMATE" in prompt
