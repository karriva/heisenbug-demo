import asyncio
import random


async def assign_driver(request_id: int):
    await asyncio.sleep(1)  # Имитация работы
    if random.random() < 0.2:  # Симуляция сбоя
        raise ValueError(f"Failed to assign driver for request {request_id}")
    return f"Driver assigned for request {request_id}"


async def process_request(request_id: int):
    asyncio.create_task(assign_driver(request_id))  # Потерянная ошибка


async def test_process_request_with_failure(caplog):
    asyncio.create_task(assign_driver(9999))  # Создаём задачу, которая может упасть
    await asyncio.sleep(2)  # Даем ей время завершиться

    # Проверяем, есть ли ошибка в логах
    assert "Failed to assign driver" in caplog.text
