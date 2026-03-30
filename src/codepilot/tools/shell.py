"""
tools/shell.py — Run a shell command and return its output.
"""

import subprocess
from src.codepilot.tools.base import make_schema

SCHEMA = make_schema(
    name="run_shell",
    description=(
        "Execute a shell command and return stdout + stderr. "
        "Use for running tests, installing packages, compiling code, etc."
    ),
    properties={
        "command": {
            "type": "string",
            "description": "The shell command to run.",
        },
        "timeout": {
            "type": "integer",
            "description": "Timeout in seconds. Defaults to 30.",
        },
    },
    required=["command"],
)


def run_shell(command: str, timeout: int = 30) -> str:
    """Run a shell command and return combined stdout/stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += result.stderr
        if not output:
            output = f"Command exited with code {result.returncode}"
        return output.strip()
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error running command: {e}"