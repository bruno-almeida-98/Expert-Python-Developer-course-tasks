import re
from enum import Enum
from multi_agent_ecosystem.agents.base_agent import AgentResult
from multi_agent_ecosystem.agents.python_agent import PythonAgent
from multi_agent_ecosystem.agents.sql_agent import SQLAgent
from multi_agent_ecosystem.agents.documentation_agent import DocumentationAgent
from multi_agent_ecosystem.memory.shared_memory import SharedMemory


class TaskType(Enum):
    PYTHON = "python"
    SQL = "sql"
    DOC = "doc"
    UNKNOWN = "unknown"


PYTHON_KEYWORDS = re.compile(
    r"\b(python|script|function|code|implement|def |class |execute|run|compute|algorithm)\b",
    re.IGNORECASE,
)
SQL_KEYWORDS = re.compile(
    r"\b(sql|select|query|database|table|insert|update|delete|schema|db)\b",
    re.IGNORECASE,
)
DOC_KEYWORDS = re.compile(
    r"\b(document|documentation|docs|readme|docstring|explain|describe)\b",
    re.IGNORECASE,
)


class Orchestrator:
    def __init__(
        self,
        api_key: str | None = None,
        db_path: str = "agent_data.db",
        memory_path: str = "shared_memory.db",
    ):
        self.memory = SharedMemory(memory_path)
        self.python_agent = PythonAgent(api_key=api_key, memory=self.memory)
        self.sql_agent = SQLAgent(api_key=api_key, db_path=db_path, memory=self.memory)
        self.documentation_agent = DocumentationAgent(api_key=api_key, memory=self.memory)

    def _classify_task(self, task: str) -> TaskType:
        doc_score = len(DOC_KEYWORDS.findall(task))
        sql_score = len(SQL_KEYWORDS.findall(task))
        python_score = len(PYTHON_KEYWORDS.findall(task))

        if doc_score == 0 and sql_score == 0 and python_score == 0:
            return TaskType.UNKNOWN
        best = max(
            [(TaskType.DOC, doc_score), (TaskType.SQL, sql_score), (TaskType.PYTHON, python_score)],
            key=lambda x: x[1],
        )
        return best[0]

    async def run(self, task: str) -> AgentResult:
        task_type = self._classify_task(task)
        agent_map = {
            TaskType.PYTHON: self.python_agent,
            TaskType.SQL: self.sql_agent,
            TaskType.DOC: self.documentation_agent,
            TaskType.UNKNOWN: self.python_agent,
        }
        agent = agent_map[task_type]
        return await agent.run(task)
