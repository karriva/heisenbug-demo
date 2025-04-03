import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_zombie_coroutines():
    """Проверка на зомби-корутину при возврате средств."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        await ac.post("/create_user/8")
        await ac.post("/refund/8/300")
        await asyncio.sleep(1.5)
        await ac.post("/withdraw/8/300")
        tasks = asyncio.all_tasks()
        # Проверяем, что в списке задач осталась только одна - текущая тестовая
        assert len(tasks) == 1, "Zombie coroutine detected: refund is still in progress"
