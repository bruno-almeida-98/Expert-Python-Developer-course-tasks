import pytest
from multi_agent_ecosystem.memory.shared_memory import SharedMemory

@pytest.mark.asyncio
async def test_store_and_retrieve(tmp_db_path):
    mem = SharedMemory(tmp_db_path)
    await mem.initialize()
    await mem.store("my_key", "my_value", agent="python_agent")
    result = await mem.retrieve("my_key")
    assert result == "my_value"

@pytest.mark.asyncio
async def test_retrieve_missing_key_returns_none(tmp_db_path):
    mem = SharedMemory(tmp_db_path)
    await mem.initialize()
    result = await mem.retrieve("nonexistent")
    assert result is None

@pytest.mark.asyncio
async def test_store_overwrites_existing_key(tmp_db_path):
    mem = SharedMemory(tmp_db_path)
    await mem.initialize()
    await mem.store("k", "v1", agent="a")
    await mem.store("k", "v2", agent="b")
    result = await mem.retrieve("k")
    assert result == "v2"

@pytest.mark.asyncio
async def test_list_keys(tmp_db_path):
    mem = SharedMemory(tmp_db_path)
    await mem.initialize()
    await mem.store("alpha", "1", agent="a")
    await mem.store("beta", "2", agent="b")
    keys = await mem.list_keys()
    assert set(keys) == {"alpha", "beta"}

@pytest.mark.asyncio
async def test_append_and_get_history(tmp_db_path):
    mem = SharedMemory(tmp_db_path)
    await mem.initialize()
    await mem.append_history("python_agent", "user", "solve this")
    await mem.append_history("python_agent", "assistant", "done")
    history = await mem.get_history("python_agent")
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "solve this"}
    assert history[1] == {"role": "assistant", "content": "done"}

@pytest.mark.asyncio
async def test_clear_history(tmp_db_path):
    mem = SharedMemory(tmp_db_path)
    await mem.initialize()
    await mem.append_history("sql_agent", "user", "query")
    await mem.clear_history("sql_agent")
    history = await mem.get_history("sql_agent")
    assert history == []
