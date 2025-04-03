import asyncio


async def long_running_task():
    await asyncio.sleep(10)  # Имитация долгой операции
    print("Task completed")


def lambda_handler(event, context):
    asyncio.create_task(long_running_task())  # Задача уходит в фон и не контролируется
    return {"status": "Lambda finished"}
