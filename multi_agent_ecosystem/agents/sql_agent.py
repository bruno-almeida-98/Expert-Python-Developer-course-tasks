from multi_agent_ecosystem.agents.base_agent import BaseAgent
from multi_agent_ecosystem.tools.sql_tools import (
    SQLDatabase,
    execute_sql,
    get_schema,
    SQL_TOOL_DEFINITIONS,
)


class SQLAgent(BaseAgent):
    name = "sql_agent"
    system_prompt = (
        "You are a SQL expert. Use get_schema to understand the database structure, "
        "then execute_sql to answer questions. Format results clearly for the user."
    )

    def __init__(self, db_path: str = "agent_data.db", **kwargs):
        super().__init__(**kwargs)
        self.db = SQLDatabase(db_path)

    @property
    def tools(self) -> list[dict]:
        return SQL_TOOL_DEFINITIONS

    def dispatch_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "execute_sql":
            result = execute_sql(self.db, tool_input["query"])
            if result["error"]:
                return f"Error: {result['error']}"
            header = " | ".join(result["columns"])
            rows = "\n".join(" | ".join(str(v) for v in row) for row in result["rows"])
            return f"{header}\n{rows}" if result["rows"] else "No rows returned."
        if tool_name == "get_schema":
            return get_schema(self.db)
        return f"Unknown tool: {tool_name}"
