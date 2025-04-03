import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_deadlock():
    """Проверка на дедлок при переводе средств."""
    client = AsyncClient(transport=ASGITransport(app), base_url="http://test")  # Создаём клиент

    try:
        await client.post("/create_user/1")
        await client.post("/create_user/2")
        await client.post("/deposit/1/1000")
        await client.post("/deposit/2/1000")

        # Запускаем два перевода одновременно, которые могут привести к дедлоку
        task1 = client.post("/transfer/1/2/100")
        task2 = client.post("/transfer/2/1/200")
        await asyncio.wait_for(asyncio.gather(task1, task2), timeout=3)  # ⏳ Тайм-аут 3 секунды
    except asyncio.TimeoutError:
        pytest.fail("❌ Deadlock detected! Test timed out.")  # Тест падает, если дедлок произошёл
    finally:
        await client.aclose()
