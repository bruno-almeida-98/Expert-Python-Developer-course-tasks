import subprocess
import sys


def execute_python(code: str, timeout: int = 10) -> dict:
    """Execute Python code in a subprocess and return stdout, stderr, exit_code."""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds.",
            "exit_code": -1,
        }


PYTHON_TOOL_DEFINITIONS = [
    {
        "name": "execute_python",
        "description": "Execute Python code in a sandboxed subprocess. Returns stdout, stderr, and exit code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Valid Python code to execute.",
                }
            },
            "required": ["code"],
        },
    }
]
