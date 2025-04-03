import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main2 import app, users, blacklist


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


@pytest.mark.asyncio
async def test_zombie_coroutines():
    """Проверка на зомби-корутину при возврате средств."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        await ac.post("/create_user/8")
        await ac.post("/refund/8/300")
        await asyncio.sleep(5)
        await ac.post("/withdraw/8/300")
        tasks = asyncio.all_tasks()
        # Проверяем, что в списке задач осталась только одна - текущая тестовая
        assert len(tasks) == 1, "Zombie coroutine detected: refund is still in progress"


@pytest.mark.asyncio
async def test_lost_exceptions():
    """Проверка на потерянные исключения в проверке мошенничества."""
    blacklist.append(9)  # Добавляем ID пользователя в чёрный список
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        await ac.post("/create_user/9")
        response = await ac.post("/fraud_check/9/400")
    await asyncio.sleep(2)
    assert "error" in response.json(), "Lost exception detected: fraud check failed silently"


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
