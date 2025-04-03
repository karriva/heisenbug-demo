import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app, blacklist


@pytest.mark.asyncio
async def test_lost_exceptions():
    """Проверка на потерянные исключения в проверке мошенничества."""
    blacklist.append(9)  # Добавляем ID пользователя в чёрный список
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        await ac.post("/create_user/9")
        response = await ac.post("/fraud_check/9/400")
    await asyncio.sleep(2)
    assert "error" in response.json(), "Lost exception detected: fraud check failed silently"
