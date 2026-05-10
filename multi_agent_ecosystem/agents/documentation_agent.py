from multi_agent_ecosystem.agents.base_agent import BaseAgent
from multi_agent_ecosystem.tools.doc_tools import (
    extract_docstrings,
    write_doc_file,
    DOC_TOOL_DEFINITIONS,
)


class DocumentationAgent(BaseAgent):
    name = "documentation_agent"
    system_prompt = (
        "You are a technical documentation expert. Use extract_docstrings to analyze "
        "Python files, then generate clear markdown documentation. Use write_doc_file "
        "to save the documentation. Always include function signatures and usage examples."
    )

    @property
    def tools(self) -> list[dict]:
        return DOC_TOOL_DEFINITIONS

    def dispatch_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "extract_docstrings":
            with open(tool_input["file_path"]) as f:
                source = f.read()
            mapping = extract_docstrings(source)
            lines = [f"Function: {name}\nDocstring: {doc or 'None'}" for name, doc in mapping.items()]
            return "\n\n".join(lines)
        if tool_name == "write_doc_file":
            write_doc_file(tool_input["file_path"], tool_input["content"])
            return f"Documentation written to {tool_input['file_path']}"
        return f"Unknown tool: {tool_name}"
