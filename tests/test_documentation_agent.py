import pytest
import textwrap
from multi_agent_ecosystem.tools.doc_tools import extract_docstrings, write_doc_file
from multi_agent_ecosystem.agents.documentation_agent import DocumentationAgent
from unittest.mock import MagicMock, AsyncMock
from multi_agent_ecosystem.assessment.self_assessor import AssessmentResult


SAMPLE_CODE = textwrap.dedent("""
    def add(a: int, b: int) -> int:
        \"\"\"Return the sum of a and b.\"\"\"
        return a + b

    def subtract(a: int, b: int) -> int:
        \"\"\"Return a minus b.\"\"\"
        return a - b

    def no_doc():
        pass
""")


def test_extract_docstrings_finds_functions():
    result = extract_docstrings(SAMPLE_CODE)
    assert "add" in result
    assert "Return the sum of a and b." in result["add"]
    assert "subtract" in result
    assert "no_doc" in result
    assert result["no_doc"] is None


def test_write_doc_file(tmp_path):
    doc_path = str(tmp_path / "output.md")
    write_doc_file(doc_path, "# Title\n\nContent here.")
    with open(doc_path) as f:
        content = f.read()
    assert "# Title" in content
    assert "Content here." in content


def test_documentation_agent_dispatch_extract(tmp_path):
    code_file = tmp_path / "sample.py"
    code_file.write_text(SAMPLE_CODE)
    agent = DocumentationAgent.__new__(DocumentationAgent)
    result = agent.dispatch_tool("extract_docstrings", {"file_path": str(code_file)})
    assert "add" in result
    assert "Return the sum" in result


def test_documentation_agent_dispatch_write(tmp_path):
    doc_path = str(tmp_path / "docs.md")
    agent = DocumentationAgent.__new__(DocumentationAgent)
    agent.dispatch_tool("write_doc_file", {"file_path": doc_path, "content": "# API Docs"})
    with open(doc_path) as f:
        assert "# API Docs" in f.read()


@pytest.mark.asyncio
async def test_documentation_agent_run_with_assessment():
    agent = DocumentationAgent.__new__(DocumentationAgent)
    agent.max_retries = 1
    agent.min_score = 7
    agent.memory = None
    agent.assessor = MagicMock()
    agent.assessor.assess = AsyncMock(
        return_value=AssessmentResult(score=8, feedback="Good docs", min_score=7)
    )
    agent._run_tool_loop = MagicMock(return_value="# Module Docs\n\n## add\nReturns sum.")
    result = await agent.run("Document the add function")
    assert result.assessment.passed is True
    assert "# Module Docs" in result.output
