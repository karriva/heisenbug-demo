from fastapi import FastAPI, HTTPException
import asyncio
import random

app = FastAPI()

# Эмуляция базы данных пользователей и их балансов
users: dict[int, int] = {}  # user_id -> balance
blacklist: list[int] = []  # Заблокированные пользователи
locks: dict = {}


def get_lock(user_id: int) -> asyncio.Lock:
    """Возвращает Lock для пользователя, создавая новый при необходимости."""
    if user_id not in locks:
        locks[user_id] = asyncio.Lock()
    return locks[user_id]


@app.post("/create_user/{user_id}")
async def create_user(user_id: int):
    """Создание пользователя с начальным балансом 0."""
    if user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user_id] = 0
    return {"user_id": user_id, "status": "created", "balance": 0}


@app.post("/deposit/{user_id}/{amount}")
async def deposit(user_id: int, amount: int):
    """Пополнение баланса."""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    async with get_lock(user_id):  # Блокировка доступа к балансу
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Имитация задержки
        users[user_id] += amount
    return {"user_id": user_id, "balance": users[user_id]}


@app.post("/withdraw/{user_id}/{amount}")
async def withdraw(user_id: int, amount: int):
    """Списание средств"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    async def update_balance():
        await asyncio.sleep(random.uniform(0.1, 0.5))
        if users[user_id] >= amount:
            await asyncio.sleep(random.uniform(0.1, 0.5))
            users[user_id] -= amount
        else:
            print("Insufficient funds")
            raise HTTPException(status_code=400, detail="Insufficient funds")

    asyncio.create_task(update_balance())
    return {"user_id": user_id, "status": "processing", "balance": users[user_id]}


@app.post("/refund/{user_id}/{amount}")
async def refund(user_id: int, amount: int):
    """Возврат средств"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    async def refund_task():
        await asyncio.sleep(5)  # Имитация долгого возврата
        users[user_id] += amount

    asyncio.create_task(refund_task())
    return {"user_id": user_id, "status": "refund_processing", "balance": users[user_id]}


@app.post("/fraud_check/{user_id}/{amount}")
async def fraud_check(user_id: int, amount: int):
    """Фоновая проверка на мошенничество"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    async def fraud_detection_task():
        await asyncio.sleep(1)  # Имитация проверки
        if user_id in blacklist:
            raise ValueError("User blocked!")
    asyncio.create_task(fraud_detection_task())
    return {"user_id": user_id, "status": "fraud_checking"}


@app.post("/transfer/{from_user}/{to_user}/{amount}")
async def transfer(from_user: int, to_user: int, amount: int):
    """
    Перевод средств между пользователями.
    """
    if from_user not in users or to_user not in users:
        raise HTTPException(status_code=404, detail="One or both users not found")

    lock1 = get_lock(from_user)
    lock2 = get_lock(to_user)

    async with lock1:  # Захватываем lock для первого пользователя
        await asyncio.sleep(random.uniform(0.1, 0.3))  # Имитация задержки

        async with lock2:  # Захватываем lock для второго пользователя
            if users[from_user] >= amount:
                users[from_user] -= amount
                users[to_user] += amount
            else:
                raise HTTPException(status_code=400, detail="Insufficient funds")

    return {"from_user": from_user, "to_user": to_user, "amount": amount, "status": "completed"}
