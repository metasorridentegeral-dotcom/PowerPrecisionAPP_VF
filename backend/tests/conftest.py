import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from server import app, startup
from database import db


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create event loop for the test session"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db():
    """Initialize database with default data before all tests"""
    await startup()
    yield


@pytest_asyncio.fixture
async def client():
    """Create async test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token(client, initialize_db):
    """Get admin authentication token"""
    response = await client.post("/api/auth/login", json={
        "email": "admin@sistema.pt",
        "password": "admin123"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def consultor_token(client, initialize_db):
    """Get consultor authentication token"""
    response = await client.post("/api/auth/login", json={
        "email": "consultor@sistema.pt",
        "password": "consultor123"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def mediador_token(client, initialize_db):
    """Get mediador authentication token"""
    response = await client.post("/api/auth/login", json={
        "email": "mediador@sistema.pt",
        "password": "mediador123"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(admin_token):
    """Get authorization headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}
