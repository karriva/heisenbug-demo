import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app, users


@pytest.mark.asyncio
async def test_race_condition():
    """Проверка на race condition при списании средств."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        await ac.post("/create_user/7")
        await ac.post("/deposit/7/500")
        tasks = [ac.post("/withdraw/7/300") for _ in range(10)]
        await asyncio.gather(*tasks)

    await asyncio.sleep(5)  # Задержка, чтобы все операции завершились
    final_balance = users[7]  # Читаем баланс после списаний

    assert final_balance == 200, f"Race condition detected! Expected balance=200, but got {final_balance}"
