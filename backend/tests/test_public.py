import pytest


@pytest.mark.asyncio
async def test_public_client_registration(client):
    """Test public client registration creates user and process"""
    response = await client.post("/api/public/client-registration", json={
        "name": "test_cliente_pytest",
        "email": "test_pytest@email.pt",
        "phone": "+351 999 000 111",
        "process_type": "credito"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "process_id" in data
    assert data["message"] == "Registo criado com sucesso"


@pytest.mark.asyncio
async def test_public_registration_missing_fields(client):
    """Test public registration with missing required fields"""
    response = await client.post("/api/public/client-registration", json={
        "name": "Test User"
        # Missing email, phone, process_type
    })
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_public_registration_invalid_email(client):
    """Test public registration with invalid email format"""
    response = await client.post("/api/public/client-registration", json={
        "name": "Test User",
        "email": "not-an-email",
        "phone": "+351 999 000 111",
        "process_type": "credito"
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_public_registration_with_personal_data(client):
    """Test public registration with optional personal data"""
    response = await client.post("/api/public/client-registration", json={
        "name": "test_cliente_full",
        "email": "test_full@email.pt",
        "phone": "+351 888 777 666",
        "process_type": "ambos",
        "personal_data": {
            "nif": "123456789",
            "address": "Rua de Teste, 123",
            "nationality": "Portuguesa"
        },
        "financial_data": {
            "monthly_income": 2500.00,
            "employment_type": "Conta de outrem"
        }
    })
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_public_registration_all_process_types(client):
    """Test all process types are accepted"""
    for process_type in ["credito", "imobiliaria", "ambos"]:
        response = await client.post("/api/public/client-registration", json={
            "name": f"test_tipo_{process_type}",
            "email": f"test_{process_type}@email.pt",
            "phone": "+351 111 222 333",
            "process_type": process_type
        })
        assert response.status_code == 200, f"Failed for type: {process_type}"
