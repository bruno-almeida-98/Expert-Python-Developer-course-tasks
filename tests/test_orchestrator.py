import pytest
from unittest.mock import AsyncMock, MagicMock
from multi_agent_ecosystem.agents.orchestrator import Orchestrator, TaskType
from multi_agent_ecosystem.agents.base_agent import AgentResult
from multi_agent_ecosystem.assessment.self_assessor import AssessmentResult


def make_mock_result(output: str, score: int = 9) -> AgentResult:
    return AgentResult(
        output=output,
        assessment=AssessmentResult(score=score, feedback="Good", min_score=7),
    )


@pytest.mark.asyncio
async def test_orchestrator_routes_python_task():
    orch = Orchestrator.__new__(Orchestrator)
    orch.python_agent = MagicMock()
    orch.python_agent.run = AsyncMock(return_value=make_mock_result("print('hi')"))
    orch.sql_agent = MagicMock()
    orch.documentation_agent = MagicMock()

    result = await orch.run("Write a Python function to compute factorial")
    orch.python_agent.run.assert_called_once()
    assert result.output == "print('hi')"


@pytest.mark.asyncio
async def test_orchestrator_routes_sql_task():
    orch = Orchestrator.__new__(Orchestrator)
    orch.python_agent = MagicMock()
    orch.sql_agent = MagicMock()
    orch.sql_agent.run = AsyncMock(return_value=make_mock_result("Alice | 30"))
    orch.documentation_agent = MagicMock()

    result = await orch.run("Query all users from the database")
    orch.sql_agent.run.assert_called_once()
    assert "Alice" in result.output


@pytest.mark.asyncio
async def test_orchestrator_routes_doc_task():
    orch = Orchestrator.__new__(Orchestrator)
    orch.python_agent = MagicMock()
    orch.sql_agent = MagicMock()
    orch.documentation_agent = MagicMock()
    orch.documentation_agent.run = AsyncMock(return_value=make_mock_result("# API Docs"))

    result = await orch.run("Generate documentation for the utils.py file")
    orch.documentation_agent.run.assert_called_once()
    assert "API Docs" in result.output


def test_classify_task_python():
    orch = Orchestrator.__new__(Orchestrator)
    assert orch._classify_task("Write a Python script to parse JSON") == TaskType.PYTHON


def test_classify_task_sql():
    orch = Orchestrator.__new__(Orchestrator)
    assert orch._classify_task("SELECT all users from the database") == TaskType.SQL


def test_classify_task_doc():
    orch = Orchestrator.__new__(Orchestrator)
    assert orch._classify_task("Generate documentation for my module") == TaskType.DOC
