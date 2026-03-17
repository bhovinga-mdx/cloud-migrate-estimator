"""Tests for pipeline orchestration."""

from unittest.mock import patch

import pytest

from estimator.pipeline import PipelineError, run_pipeline


class TestPipeline:
    def test_rejects_empty_transcript(self, tmp_path):
        transcript = tmp_path / "empty.txt"
        transcript.write_text("")
        with pytest.raises(PipelineError, match="empty"):
            run_pipeline(transcript)

    def test_rejects_oversized_transcript(self, tmp_path):
        transcript = tmp_path / "huge.txt"
        transcript.write_text("x" * 500_000)
        with pytest.raises(PipelineError, match="exceeding"):
            run_pipeline(transcript)

    @patch("estimator.pipeline.run_gaps")
    @patch("estimator.pipeline.run_estimate")
    @patch("estimator.pipeline.run_architect")
    @patch("estimator.pipeline.run_extract")
    def test_full_pipeline_produces_report(
        self,
        mock_extract,
        mock_architect,
        mock_estimate,
        mock_gaps,
        sample_extraction,
        sample_architecture,
        sample_estimate,
        sample_gaps,
        tmp_path,
    ):
        mock_extract.return_value = sample_extraction
        mock_architect.return_value = sample_architecture
        mock_estimate.return_value = sample_estimate
        mock_gaps.return_value = sample_gaps

        transcript = tmp_path / "call.txt"
        transcript.write_text("Some transcript content here.")

        output_dir = tmp_path / "output"
        report_path = run_pipeline(transcript, output_dir=output_dir, verbose=False)

        assert report_path.exists()
        assert report_path.suffix == ".md"
        content = report_path.read_text()
        assert "Executive Summary" in content

    @patch("estimator.pipeline.run_gaps")
    @patch("estimator.pipeline.run_estimate")
    @patch("estimator.pipeline.run_architect")
    @patch("estimator.pipeline.run_extract")
    def test_saves_intermediate_outputs(
        self,
        mock_extract,
        mock_architect,
        mock_estimate,
        mock_gaps,
        sample_extraction,
        sample_architecture,
        sample_estimate,
        sample_gaps,
        tmp_path,
    ):
        mock_extract.return_value = sample_extraction
        mock_architect.return_value = sample_architecture
        mock_estimate.return_value = sample_estimate
        mock_gaps.return_value = sample_gaps

        transcript = tmp_path / "call.txt"
        transcript.write_text("Some transcript content.")

        output_dir = tmp_path / "output"
        run_pipeline(transcript, output_dir=output_dir, verbose=False)

        stages_dir = output_dir / "stages"
        assert (stages_dir / "01_extraction.json").exists()
        assert (stages_dir / "02_architecture.json").exists()
        assert (stages_dir / "03_estimate.json").exists()
        assert (stages_dir / "04_gaps.json").exists()
