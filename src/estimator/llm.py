"""Claude Code CLI wrapper for LLM inference."""

import json
import subprocess
import tempfile
from pathlib import Path

from pydantic import BaseModel


class LLMError(Exception):
    """Raised when Claude Code CLI call fails."""


class LLMResponse(BaseModel):
    result: str
    model: str = ""
    session_id: str = ""


def call_claude(
    prompt: str,
    model: str = "claude-sonnet-4-6",
    system_prompt: str | None = None,
    json_schema: dict | None = None,
    input_text: str | None = None,
    max_retries: int = 1,
) -> dict:
    """Call Claude Code CLI and return parsed JSON response.

    Args:
        prompt: The user prompt to send.
        model: Model to use (e.g., claude-opus-4-6, claude-sonnet-4-6).
        system_prompt: Optional system prompt (written to temp file to avoid CLI length limits).
        json_schema: Optional JSON schema for structured output.
        input_text: Optional text to pipe via stdin (e.g., transcript content).
        max_retries: Number of retries on failure.

    Returns:
        Parsed structured output dict if json_schema provided, otherwise raw result dict.
    """
    attempts = 0
    last_error: Exception | None = None

    while attempts <= max_retries:
        try:
            return _execute_claude(prompt, model, system_prompt, json_schema, input_text)
        except LLMError as e:
            last_error = e
            attempts += 1

    raise LLMError(f"Failed after {attempts} attempts: {last_error}")


def _execute_claude(
    prompt: str,
    model: str,
    system_prompt: str | None,
    json_schema: dict | None,
    input_text: str | None,
) -> dict:
    """Execute a single Claude Code CLI call."""
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json"]
    temp_files: list[Path] = []

    try:
        if system_prompt:
            sp_file = tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            )
            sp_file.write(system_prompt)
            sp_file.close()
            temp_files.append(Path(sp_file.name))
            cmd.extend(["--system-prompt-file", sp_file.name])

        if json_schema:
            schema_str = json.dumps(json_schema)
            cmd.extend(["--json-schema", schema_str])

        stdin_data = input_text.encode("utf-8") if input_text else None

        result = subprocess.run(
            cmd,
            capture_output=True,
            stdin=subprocess.PIPE if stdin_data else None,
            input=stdin_data,
            timeout=300,  # 5 minute timeout per stage
        )

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            raise LLMError(f"Claude CLI exited with code {result.returncode}: {stderr}")

        stdout = result.stdout.decode("utf-8", errors="replace")

        try:
            response = json.loads(stdout)
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse CLI JSON output: {e}\nRaw output: {stdout[:500]}")

        if json_schema and "structured_output" in response:
            return response["structured_output"]

        if "result" in response:
            # Try to parse result as JSON (for non-schema responses)
            try:
                return json.loads(response["result"])
            except (json.JSONDecodeError, TypeError):
                return response

        return response

    finally:
        for f in temp_files:
            f.unlink(missing_ok=True)
