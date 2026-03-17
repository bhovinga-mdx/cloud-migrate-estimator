"""Tests for Claude Code CLI wrapper."""

import json
from unittest.mock import MagicMock, patch

import pytest

from estimator.llm import LLMError, call_claude


class TestCallClaude:
    @patch("estimator.llm.subprocess.run")
    def test_successful_json_response(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": '{"key": "value"}'}).encode(),
            stderr=b"",
        )
        result = call_claude("test prompt", model="claude-sonnet-4-6")
        assert result == {"key": "value"}

    @patch("estimator.llm.subprocess.run")
    def test_structured_output_response(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "result": "some text",
                "structured_output": {"name": "test", "value": 42},
            }).encode(),
            stderr=b"",
        )
        result = call_claude(
            "test prompt",
            json_schema={"type": "object"},
        )
        assert result == {"name": "test", "value": 42}

    @patch("estimator.llm.subprocess.run")
    def test_nonzero_exit_code_raises(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=b"",
            stderr=b"Something went wrong",
        )
        with pytest.raises(LLMError, match="exited with code 1"):
            call_claude("test prompt", max_retries=0)

    @patch("estimator.llm.subprocess.run")
    def test_retry_on_failure(self, mock_run):
        # First call fails, second succeeds
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=b"", stderr=b"error"),
            MagicMock(
                returncode=0,
                stdout=json.dumps({"result": '{"ok": true}'}).encode(),
                stderr=b"",
            ),
        ]
        result = call_claude("test prompt", max_retries=1)
        assert result == {"ok": True}
        assert mock_run.call_count == 2

    @patch("estimator.llm.subprocess.run")
    def test_max_retries_exhausted(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1, stdout=b"", stderr=b"error"
        )
        with pytest.raises(LLMError, match="Failed after 2 attempts"):
            call_claude("test prompt", max_retries=1)

    @patch("estimator.llm.subprocess.run")
    def test_invalid_json_raises(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=b"not json at all",
            stderr=b"",
        )
        with pytest.raises(LLMError, match="Failed to parse"):
            call_claude("test prompt", max_retries=0)

    @patch("estimator.llm.subprocess.run")
    def test_model_passed_to_cli(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": '{"ok": true}'}).encode(),
            stderr=b"",
        )
        call_claude("test prompt", model="claude-opus-4-6")
        cmd = mock_run.call_args[0][0]
        assert "--model" in cmd
        assert "claude-opus-4-6" in cmd

    @patch("estimator.llm.subprocess.run")
    def test_stdin_passed_when_input_text_provided(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": '{"ok": true}'}).encode(),
            stderr=b"",
        )
        call_claude("test prompt", input_text="some transcript text")
        assert mock_run.call_args[1]["input"] == b"some transcript text"
