from multi_agent_ecosystem.agents.base_agent import BaseAgent
from multi_agent_ecosystem.tools.python_tools import execute_python, PYTHON_TOOL_DEFINITIONS


class PythonAgent(BaseAgent):
    name = "python_agent"
    system_prompt = (
        "You are a Python programming expert. When asked to write or run Python code, "
        "use the execute_python tool to run it and show the output. "
        "Always verify your code works before reporting results."
    )

    @property
    def tools(self) -> list[dict]:
        return PYTHON_TOOL_DEFINITIONS

    def dispatch_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "execute_python":
            result = execute_python(tool_input["code"])
            return (
                f"Exit code: {result['exit_code']}\n"
                f"Stdout:\n{result['stdout']}\n"
                f"Stderr:\n{result['stderr']}"
            )
        return f"Unknown tool: {tool_name}"
