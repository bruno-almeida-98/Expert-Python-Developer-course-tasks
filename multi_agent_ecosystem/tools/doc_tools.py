import ast


def extract_docstrings(source_code: str) -> dict[str, str | None]:
    """Parse Python source and return {function_name: docstring} mapping."""
    tree = ast.parse(source_code)
    result = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)
            result[node.name] = docstring
    return result


def write_doc_file(file_path: str, content: str) -> None:
    with open(file_path, "w") as f:
        f.write(content)


DOC_TOOL_DEFINITIONS = [
    {
        "name": "extract_docstrings",
        "description": "Extract function names and their docstrings from a Python source file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the Python file."}
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "write_doc_file",
        "description": "Write markdown documentation to a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Output file path."},
                "content": {"type": "string", "description": "Markdown content to write."},
            },
            "required": ["file_path", "content"],
        },
    },
]
