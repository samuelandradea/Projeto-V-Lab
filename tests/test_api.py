import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models import Base

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL)
test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with test_session() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

HEADERS = {"X-API-Key": settings.API_KEY}

VALID_PAYLOAD = {
    "id_posto": 1,
    "data_hora": "2024-01-15T10:30:00",
    "tipo_combustivel": "GASOLINA",
    "preco_por_litro": 5.99,
    "volume_abastecido": 40.0,
    "cpf_motorista": "52998224725",
}


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_abastecimento():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/abastecimentos", json=VALID_PAYLOAD, headers=HEADERS
        )
    assert response.status_code == 201
    data = response.json()
    assert data["id_posto"] == 1
    assert data["improper_data"] is False


@pytest.mark.asyncio
async def test_create_abastecimento_with_anomaly():
    payload = {**VALID_PAYLOAD, "preco_por_litro": 10.00}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/abastecimentos", json=payload, headers=HEADERS
        )
    assert response.status_code == 201
    assert response.json()["improper_data"] is True


@pytest.mark.asyncio
async def test_create_abastecimento_invalid_cpf():
    payload = {**VALID_PAYLOAD, "cpf_motorista": "00000000000"}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/abastecimentos", json=payload, headers=HEADERS
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_abastecimento_no_api_key():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/abastecimentos", json=VALID_PAYLOAD
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_abastecimentos():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            "/api/v1/abastecimentos", json=VALID_PAYLOAD, headers=HEADERS
        )
        response = await client.get("/api/v1/abastecimentos")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_historico_motorista():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            "/api/v1/abastecimentos", json=VALID_PAYLOAD, headers=HEADERS
        )
        response = await client.get("/api/v1/motoristas/52998224725/historico")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_historico_motorista_empty():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/motoristas/52998224725/historico")
    assert response.status_code == 200
    assert response.json() == []
