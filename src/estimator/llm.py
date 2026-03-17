"""Claude Code CLI wrapper for LLM inference."""

import json
import subprocess
import tempfile
from pathlib import Path


class LLMError(Exception):
    """Raised when Claude Code CLI call fails."""


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
        json_schema: Optional JSON schema to embed in prompt for structured output.
        input_text: Optional text to pipe via stdin (e.g., transcript content).
        max_retries: Number of retries on failure.

    Returns:
        Parsed JSON dict from Claude's response.
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


def _build_full_prompt(
    prompt: str,
    system_prompt: str | None,
    json_schema: dict | None,
    input_text: str | None,
) -> str:
    """Build the full prompt file content, combining system prompt, schema, and user prompt."""
    parts = []

    if system_prompt:
        parts.append(system_prompt)

    if json_schema:
        schema_str = json.dumps(json_schema, indent=2)
        parts.append(
            "Respond ONLY with valid JSON matching this exact schema. "
            "No markdown, no code fences, no explanation — just the JSON object.\n\n"
            f"JSON SCHEMA:\n{schema_str}"
        )

    parts.append(prompt)

    if input_text:
        parts.append(f"\n---\nINPUT:\n{input_text}")

    return "\n\n".join(parts)


def _execute_claude(
    prompt: str,
    model: str,
    system_prompt: str | None,
    json_schema: dict | None,
    input_text: str | None,
) -> dict:
    """Execute a single Claude Code CLI call."""
    # Build full prompt and write to temp file to avoid command line length limits
    full_prompt = _build_full_prompt(prompt, system_prompt, json_schema, input_text)

    prompt_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    )
    prompt_file.write(full_prompt)
    prompt_file.close()
    prompt_file_path = Path(prompt_file.name)

    try:
        # Read prompt from file via stdin to avoid Windows CLI length limits
        with open(prompt_file_path, encoding="utf-8") as f:
            prompt_content = f.read()

        cmd = [
            "claude",
            "-p",
            prompt_content,
            "--model",
            model,
            "--output-format",
            "json",
        ]

        env = {**subprocess.os.environ, "PYTHONIOENCODING": "utf-8"}
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=600,  # 10 minute timeout per stage
            env=env,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            raise LLMError(
                f"Claude CLI exited with code {result.returncode}: {stderr[:500]}"
            )

        stdout = result.stdout.decode("utf-8", errors="replace")

        try:
            response = json.loads(stdout)
        except json.JSONDecodeError as e:
            raise LLMError(
                f"Failed to parse CLI JSON output: {e}\nRaw output: {stdout[:500]}"
            )

        if "result" in response:
            result_text = response["result"]
            # Strip markdown code fences if present
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                # Remove first and last lines (fences)
                lines = [line for line in lines if not line.startswith("```")]
                result_text = "\n".join(lines)
            try:
                return json.loads(result_text)
            except (json.JSONDecodeError, TypeError):
                raise LLMError(
                    f"Claude response is not valid JSON:\n{result_text[:500]}"
                )

        return response

    finally:
        prompt_file_path.unlink(missing_ok=True)
