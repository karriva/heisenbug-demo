import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from fastapi import status
from main import app
from httpx import ASGITransport

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_user():
    response = client.post("/create_user/1")
    assert response.status_code == status.HTTP_200_OK
    assert "user_id" in response.json()


@pytest.mark.asyncio
async def test_deposit():
    response = client.post("/create_user/2")
    assert response.status_code == status.HTTP_200_OK

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        deposit_resp = await ac.post("/deposit/2/300")
    assert deposit_resp.status_code == status.HTTP_200_OK
    assert "balance" in deposit_resp.json()


@pytest.mark.asyncio
async def test_withdraw():
    response = client.post("/create_user/3")
    assert response.status_code == status.HTTP_200_OK

    client.post("/deposit/3/500")

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        withdraw_resp = await ac.post("/withdraw/3/200")
    assert withdraw_resp.status_code == status.HTTP_200_OK
    assert "status" in withdraw_resp.json()


@pytest.mark.asyncio
async def test_refund():
    response = client.post("/create_user/4")
    assert response.status_code == status.HTTP_200_OK
    client.post("/deposit/4/1000")

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        refund_resp = await ac.post("/refund/4/300")
    assert refund_resp.status_code == status.HTTP_200_OK
    assert "status" in refund_resp.json()


@pytest.mark.asyncio
async def test_fraud_check():
    response = client.post("/create_user/5")
    assert response.status_code == status.HTTP_200_OK

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        fraud_resp = await ac.post("/fraud_check/5/500")
    assert fraud_resp.status_code == status.HTTP_200_OK
    assert "status" in fraud_resp.json()


@pytest.mark.asyncio
async def test_transfer():
    response = client.post("/create_user/6")
    assert response.status_code == status.HTTP_200_OK
    client.post("/deposit/6/500")

    response = client.post("/create_user/7")
    assert response.status_code == status.HTTP_200_OK
    client.post("/deposit/7/500")

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        transfer_resp = await ac.post("/transfer/6/7/100")
    assert transfer_resp.status_code == status.HTTP_200_OK
    assert "status" in transfer_resp.json()


@pytest.mark.asyncio
async def test_multiple_operations():
    response = client.post("/create_user/8")
    assert response.status_code == status.HTTP_200_OK
    client.post("/deposit/8/500")
    client.post("/withdraw/8/200")
    client.post("/refund/8/100")

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        fraud_resp = await ac.post("/fraud_check/8/300")
    assert fraud_resp.status_code == status.HTTP_200_OK
    assert "status" in fraud_resp.json()

