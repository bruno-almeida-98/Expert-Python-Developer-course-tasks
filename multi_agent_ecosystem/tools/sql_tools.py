import sqlite3
from dataclasses import dataclass


@dataclass
class SQLDatabase:
    path: str

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)


def execute_sql(db: SQLDatabase, query: str) -> dict:
    try:
        conn = db.connect()
        cursor = conn.execute(query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [list(row) for row in cursor.fetchall()]
        conn.close()
        return {"columns": columns, "rows": rows, "error": None}
    except Exception as e:
        return {"columns": [], "rows": [], "error": str(e)}


def get_schema(db: SQLDatabase) -> str:
    conn = db.connect()
    cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")
    schema_parts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return "\n\n".join(schema_parts) if schema_parts else "No tables found."


SQL_TOOL_DEFINITIONS = [
    {
        "name": "execute_sql",
        "description": "Execute a SQL query against the database and return results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query to execute."}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_schema",
        "description": "Get the database schema showing all tables and their columns.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]
