"""Tests for CLI entrypoint."""

from unittest.mock import patch

from typer.testing import CliRunner

from estimator.cli import app

runner = CliRunner()


class TestCLI:
    def test_version(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_validate_config(self):
        result = runner.invoke(app, ["validate-config"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_generate_rejects_unsupported_format(self, tmp_path):
        bad_file = tmp_path / "transcript.pdf"
        bad_file.write_text("content")
        result = runner.invoke(app, ["generate", str(bad_file)])
        assert result.exit_code == 1
        assert "Unsupported" in result.output

    @patch("estimator.cli.run_pipeline")
    def test_generate_calls_pipeline(self, mock_pipeline, tmp_path):
        transcript = tmp_path / "call.txt"
        transcript.write_text("some content")
        report = tmp_path / "report.md"
        report.write_text("# Report")
        mock_pipeline.return_value = report

        result = runner.invoke(app, ["generate", str(transcript)])
        assert result.exit_code == 0
        mock_pipeline.assert_called_once()

    def test_no_args_shows_help(self):
        result = runner.invoke(app, [])
        assert "Usage" in result.output or "usage" in result.output
