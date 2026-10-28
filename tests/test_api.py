from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home_returns_welcome_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["documentacion"] == "/docs"


def test_destination_crud_create_and_read():
    payload = {
        "nombre": "Destino de prueba pytest",
        "departamento": "Meta",
        "descripcion": "Destino de prueba para verificar operaciones CRUD.",
        "tipo_turismo": "Aventura y naturaleza",
        "dias_recomendados": 2,
        "costo_transporte_local": 50000,
        "costo_alojamiento": 80000,
        "costo_alimentacion": 40000,
        "costo_actividades": 60000,
    }
    created = client.post("/destinos", json=payload)
    assert created.status_code == 201
    destination_id = created.json()["id"]
    fetched = client.get(f"/destinos/{destination_id}")
    assert fetched.status_code == 200
    assert fetched.json()["nombre"] == payload["nombre"]
    deleted = client.delete(f"/destinos/{destination_id}")
    assert deleted.status_code == 200


def test_destination_rejects_negative_cost():
    payload = {
        "nombre": "Destino inválido",
        "departamento": "Meta",
        "descripcion": "Descripción de prueba para validación.",
        "tipo_turismo": "Naturaleza",
        "dias_recomendados": 2,
        "costo_transporte_local": -1,
        "costo_alojamiento": 80000,
        "costo_alimentacion": 40000,
        "costo_actividades": 60000,
    }
    response = client.post("/destinos", json=payload)
    assert response.status_code == 422
