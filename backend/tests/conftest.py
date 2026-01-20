import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from server import app
from database import db


@pytest_asyncio.fixture
async def client():
    """Create async test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token(client):
    """Get admin authentication token"""
    response = await client.post("/api/auth/login", json={
        "email": "admin@sistema.pt",
        "password": "admin123"
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def consultor_token(client):
    """Get consultor authentication token"""
    response = await client.post("/api/auth/login", json={
        "email": "consultor@sistema.pt",
        "password": "consultor123"
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def mediador_token(client):
    """Get mediador authentication token"""
    response = await client.post("/api/auth/login", json={
        "email": "mediador@sistema.pt",
        "password": "mediador123"
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(admin_token):
    """Get authorization headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def cleanup_test_data():
    """Cleanup test data after tests"""
    yield
    # Clean up any test users/processes created during tests
    await db.users.delete_many({"email": {"$regex": "^test_"}})
    await db.processes.delete_many({"client_email": {"$regex": "^test_"}})
