import pytest
import sqlite3
import tempfile
import os
from multi_agent_ecosystem.tools.sql_tools import SQLDatabase, execute_sql, get_schema
from multi_agent_ecosystem.agents.sql_agent import SQLAgent
from unittest.mock import MagicMock, AsyncMock
from multi_agent_ecosystem.assessment.self_assessor import AssessmentResult


@pytest.fixture
def tmp_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 25)")
    conn.commit()
    conn.close()
    return db_path


def test_execute_sql_select(tmp_db):
    db = SQLDatabase(tmp_db)
    result = execute_sql(db, "SELECT * FROM users ORDER BY id")
    assert result["rows"] == [[1, "Alice", 30], [2, "Bob", 25]]
    assert result["columns"] == ["id", "name", "age"]
    assert result["error"] is None


def test_execute_sql_invalid_query(tmp_db):
    db = SQLDatabase(tmp_db)
    result = execute_sql(db, "SELECT * FROM nonexistent_table")
    assert result["error"] is not None
    assert "no such table" in result["error"].lower()


def test_get_schema(tmp_db):
    db = SQLDatabase(tmp_db)
    schema = get_schema(db)
    assert "users" in schema
    assert "id" in schema
    assert "name" in schema


def test_sql_agent_dispatch_tool(tmp_db):
    agent = SQLAgent.__new__(SQLAgent)
    agent.db = SQLDatabase(tmp_db)
    result = agent.dispatch_tool("execute_sql", {"query": "SELECT COUNT(*) FROM users"})
    assert "2" in str(result)


def test_sql_agent_dispatch_get_schema(tmp_db):
    agent = SQLAgent.__new__(SQLAgent)
    agent.db = SQLDatabase(tmp_db)
    result = agent.dispatch_tool("get_schema", {})
    assert "users" in result


@pytest.mark.asyncio
async def test_sql_agent_run_with_assessment(tmp_db):
    agent = SQLAgent.__new__(SQLAgent)
    agent.max_retries = 1
    agent.min_score = 7
    agent.memory = None
    agent.db = SQLDatabase(tmp_db)

    agent.assessor = MagicMock()
    agent.assessor.assess = AsyncMock(
        return_value=AssessmentResult(score=8, feedback="Good SQL output", min_score=7)
    )
    agent._run_tool_loop = MagicMock(return_value="The users table has 2 rows.")

    result = await agent.run("How many users are in the database?")
    assert result.assessment.passed is True
