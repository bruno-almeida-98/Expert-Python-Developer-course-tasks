# Multi-Agent Ecosystem

Integrated multi-agent system built with the Anthropic SDK. Three specialized agents share memory, execute tasks, and self-assess their own outputs using Claude.

## Agents

| Agent | Responsibility | Tools |
|---|---|---|
| **PythonAgent** | Executes Python code tasks | `execute_python` (subprocess sandbox) |
| **SQLAgent** | Answers database queries | `execute_sql`, `get_schema` |
| **DocumentationAgent** | Generates markdown documentation | `extract_docstrings`, `write_doc_file` |
| **Orchestrator** | Routes tasks to the right agent | — |

## Architecture

```
User Task
    │
    ▼
Orchestrator (keyword classification)
    │
    ├── PythonAgent ──┐
    ├── SQLAgent      ├── BaseAgent (tool-use loop + self-assessment retry)
    └── DocAgent ─────┘
                           │
                           ├── Claude API (tool calls)
                           ├── SelfAssessor (grades output 1–10)
                           └── SharedMemory (SQLite)
```

**Self-assessment loop:** after each agent response, `SelfAssessor` asks Claude to grade the output (1–10). If score < 7, the agent retries with the feedback — up to 3 attempts.

**Shared memory:** all agents read/write a SQLite-backed key-value store. Last result from each agent is persisted under `<agent_name>:last_result`.

## Stack

- Python 3.13
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) — Claude tool-use and self-assessment
- `aiosqlite` — async SQLite for shared memory
- Pydantic v2 — data models
- pytest + pytest-asyncio — test suite

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

## Run the Demo

```bash
python3 -m multi_agent_ecosystem.main
```

Runs three tasks through the ecosystem:
1. **Python:** recursive Fibonacci function, tested with n=10
2. **SQL:** query products with stock below 60
3. **Documentation:** generate markdown docs for a Python function

Output includes Claude's response and the self-assessment score for each task.

## Tests

```bash
pytest tests/ -v
```

33 tests covering all components — no API key required (Claude calls are mocked).

## Project Structure

```
multi_agent_ecosystem/
├── agents/
│   ├── base_agent.py          # Abstract agent: tool-use loop + retry
│   ├── python_agent.py
│   ├── sql_agent.py
│   ├── documentation_agent.py
│   └── orchestrator.py        # Task routing
├── assessment/
│   └── self_assessor.py       # Claude-based output grader
├── memory/
│   └── shared_memory.py       # SQLite key-value + history
├── tools/
│   ├── python_tools.py        # subprocess execution
│   ├── sql_tools.py           # SQLite query tools
│   └── doc_tools.py           # AST docstring extraction
└── main.py                    # CLI demo entry point
tests/
├── test_shared_memory.py
├── test_self_assessor.py
├── test_python_agent.py
├── test_sql_agent.py
├── test_documentation_agent.py
└── test_orchestrator.py
```
