import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from multi_agent_ecosystem.tools.python_tools import execute_python
from multi_agent_ecosystem.agents.python_agent import PythonAgent
from multi_agent_ecosystem.assessment.self_assessor import AssessmentResult


def test_execute_python_hello_world():
    result = execute_python("print('hello world')")
    assert result["stdout"] == "hello world\n"
    assert result["stderr"] == ""
    assert result["exit_code"] == 0


def test_execute_python_captures_error():
    result = execute_python("raise ValueError('oops')")
    assert result["exit_code"] != 0
    assert "ValueError" in result["stderr"]


def test_execute_python_timeout():
    result = execute_python("import time; time.sleep(60)", timeout=1)
    assert result["exit_code"] != 0
    assert "timed out" in result["stderr"].lower() or result["exit_code"] == -1


def test_execute_python_returns_value():
    result = execute_python("x = 2 + 2\nprint(x)")
    assert result["stdout"].strip() == "4"


def test_python_agent_dispatch_tool():
    agent = PythonAgent.__new__(PythonAgent)
    result = agent.dispatch_tool("execute_python", {"code": "print(42)"})
    assert "42" in str(result)


@pytest.mark.asyncio
async def test_python_agent_run_uses_assessment():
    agent = PythonAgent.__new__(PythonAgent)
    agent.max_retries = 1
    agent.min_score = 7
    agent.memory = None

    passed_assessment = AssessmentResult(score=9, feedback="Perfect", min_score=7)
    agent.assessor = MagicMock()
    agent.assessor.assess = AsyncMock(return_value=passed_assessment)
    agent._run_tool_loop = MagicMock(return_value="print('hello')")

    result = await agent.run("Write hello world in Python")
    assert result.output == "print('hello')"
    assert result.assessment.passed is True
