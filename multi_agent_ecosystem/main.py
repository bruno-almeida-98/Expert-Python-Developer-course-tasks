import asyncio
import os
import sqlite3
from dotenv import load_dotenv
from multi_agent_ecosystem.agents.orchestrator import Orchestrator
from multi_agent_ecosystem.memory.shared_memory import SharedMemory

load_dotenv()

DEMO_DB = "demo_agent_data.db"
DEMO_MEMORY = "demo_shared_memory.db"


def seed_demo_database() -> None:
    conn = sqlite3.connect(DEMO_DB)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        );
        DELETE FROM products;
        INSERT INTO products VALUES (1, 'Widget A', 9.99, 100);
        INSERT INTO products VALUES (2, 'Widget B', 19.99, 50);
        INSERT INTO products VALUES (3, 'Gadget X', 49.99, 25);
    """)
    conn.commit()
    conn.close()


async def main() -> None:
    print("=== Multi-Agent Ecosystem Demo ===\n")

    seed_demo_database()

    memory = SharedMemory(DEMO_MEMORY)
    await memory.initialize()

    orchestrator = Orchestrator(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        db_path=DEMO_DB,
        memory_path=DEMO_MEMORY,
    )

    tasks = [
        "Write a Python function that computes the nth Fibonacci number recursively and test it with n=10",
        "Query all products from the database and show me which ones have stock below 60",
        "Generate documentation for this Python function: def greet(name: str) -> str: '''Return a greeting message.''' return f'Hello, {name}!'",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"--- Task {i} ---")
        print(f"Input: {task}\n")
        result = await orchestrator.run(task)
        print(f"Output (score: {result.assessment.score if result.assessment else 'N/A'}/10):")
        print(result.output)
        print()

    print("=== Shared Memory Keys ===")
    keys = await memory.list_keys()
    for key in keys:
        value = await memory.retrieve(key)
        print(f"  {key}: {value[:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
