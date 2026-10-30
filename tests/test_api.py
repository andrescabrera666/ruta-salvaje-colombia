import csv
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
DATA = Path(os.environ["RSC_DATA_DIR"])

DESTINO = {
    "nombre": "Cerros de Mavecure", "departamento": "Guainía",
    "descripcion": "Destino natural de aventura con cerros y río.",
    "tipo_turismo": "Aventura y naturaleza", "dias_recomendados": 4,
    "costo_transporte_local": 180000, "costo_alojamiento": 250000,
    "costo_alimentacion": 160000, "costo_actividades": 200000,
}
SOLICITUD = {"ciudad_origen": "Bogotá", "presupuesto": 1500000, "dias_disponibles": 4,
             "preferencia_turistica": "Aventura y naturaleza", "numero_personas": 1}
VUELO = {"ciudad_origen": "Bogotá", "ciudad_destino": "Inírida", "precio": 450000,
         "proveedor": "Proveedor X", "url_compra": "https://www.ejemplo.com/"}


def filas(carpeta, nombre):
    with (DATA / carpeta / f"{nombre}.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_inicio():
    r = client.get("/")
    assert r.status_code == 200 and r.json()["documentacion"] == "/docs"


def test_los_csv_se_crean_en_carpetas_activos_y_eliminados():
    for nombre in ("destinos", "solicitudes", "vuelos", "itinerarios"):
        assert (DATA / "activos" / f"{nombre}.csv").exists()
        assert (DATA / "eliminados" / f"{nombre}.csv").exists()


def test_docs_agrupa_endpoints_por_secciones():
    tags = {t for ruta in app.openapi()["paths"].values()
            for op in ruta.values() for t in op["tags"]}
    assert tags == {"Inicio", "Destinos", "Solicitudes", "Vuelos", "Itinerarios", "Recomendaciones"}
    assert "default" not in tags


def test_crear_y_consultar_destino_se_guarda_en_csv():
    creado = client.post("/destinos", json=DESTINO)
    assert creado.status_code == 201
    did = creado.json()["id"]
    assert client.get(f"/destinos/{did}").json()["nombre"] == DESTINO["nombre"]
    assert any(int(f["id"]) == did for f in filas("activos", "destinos"))


def test_actualizar_destino():
    did = client.post("/destinos", json=DESTINO).json()["id"]
    r = client.put(f"/destinos/{did}", json={**DESTINO, "dias_recomendados": 7})
    assert r.status_code == 200 and r.json()["dias_recomendados"] == 7


def test_destino_rechaza_costo_negativo():
    r = client.post("/destinos", json={**DESTINO, "costo_alojamiento": -1})
    assert r.status_code == 422


def test_eliminar_mueve_el_registro_al_csv_de_eliminados():
    did = client.post("/destinos", json={**DESTINO, "nombre": "Para borrar"}).json()["id"]
    assert client.delete(f"/destinos/{did}").status_code == 200
    assert client.get(f"/destinos/{did}").status_code == 404
    assert all(int(f["id"]) != did for f in filas("activos", "destinos"))
    borrados = [f for f in filas("eliminados", "destinos") if int(f["id"]) == did]
    assert len(borrados) == 1 and borrados[0]["nombre"] == "Para borrar"
    assert borrados[0]["fecha_eliminacion"]
    assert any(h["id"] == did for h in client.get("/destinos/historial").json())


def test_eliminar_inexistente_da_404():
    assert client.delete("/destinos/99999").status_code == 404


def test_restaurar_devuelve_el_registro_a_activos():
    did = client.post("/destinos", json={**DESTINO, "nombre": "Restaurable"}).json()["id"]
    client.delete(f"/destinos/{did}")
    r = client.post(f"/destinos/{did}/restaurar")
    assert r.status_code == 200
    assert client.get(f"/destinos/{did}").status_code == 200
    assert all(int(f["id"]) != did for f in filas("eliminados", "destinos"))
    assert client.post(f"/destinos/{did}/restaurar").status_code == 404


def test_los_ids_eliminados_no_se_reutilizan():
    a = client.post("/destinos", json=DESTINO).json()["id"]
    client.delete(f"/destinos/{a}")
    b = client.post("/destinos", json=DESTINO).json()["id"]
    assert b > a


def test_buscar_destinos_por_nombre():
    client.post("/destinos", json={**DESTINO, "nombre": "Caño Cristales"})
    r = client.get("/destinos/buscar", params={"nombre": "cristales"})
    assert r.status_code == 200 and r.json()
    assert all("cristales" in d["nombre"].lower() for d in r.json())


def test_filtrar_destinos_por_atributos():
    client.post("/destinos", json={**DESTINO, "nombre": "Filtro Meta", "departamento": "Meta",
                                   "dias_recomendados": 2})
    r = client.get("/destinos/filtrar", params={"departamento": "meta", "max_dias": 2})
    assert r.status_code == 200 and r.json()
    assert all(d["departamento"] == "Meta" and d["dias_recomendados"] <= 2 for d in r.json())


def test_solicitud_crud_y_borrado_con_historial():
    sid = client.post("/solicitudes", json=SOLICITUD).json()["id"]
    assert client.get(f"/solicitudes/{sid}").status_code == 200
    assert client.put(f"/solicitudes/{sid}", json={**SOLICITUD, "numero_personas": 3}).json()["numero_personas"] == 3
    assert client.delete(f"/solicitudes/{sid}").status_code == 200
    assert any(int(f["id"]) == sid for f in filas("eliminados", "solicitudes"))


def test_vuelo_crud_y_borrado_con_historial():
    vid = client.post("/vuelos", json=VUELO).json()["id"]
    assert client.get(f"/vuelos/{vid}").json()["estado_precio"] == "estimado"
    assert client.delete(f"/vuelos/{vid}").status_code == 200
    assert any(int(f["id"]) == vid for f in filas("eliminados", "vuelos"))
    assert client.post(f"/vuelos/{vid}/restaurar").status_code == 200


def test_itinerario_calcula_total_y_valida_relaciones():
    did = client.post("/destinos", json=DESTINO).json()["id"]
    sid = client.post("/solicitudes", json=SOLICITUD).json()["id"]
    payload = {"solicitud_id": sid, "destino_id": did, "dias": 4, "costo_vuelo": 450000,
               "costo_transporte_local": 100, "costo_alojamiento": 200,
               "costo_alimentacion": 300, "costo_actividades": 400,
               "recomendacion": "Verificar precios antes de viajar."}
    r = client.post("/itinerarios", json=payload)
    assert r.status_code == 201 and r.json()["costo_total"] == 450000 + 1000
    malo = client.post("/itinerarios", json={**payload, "destino_id": 99999})
    assert malo.status_code == 400
    iid = r.json()["id"]
    assert client.delete(f"/itinerarios/{iid}").status_code == 200
    assert client.get("/itinerarios/historial").json()


def test_recomendaciones_filtra_por_presupuesto_y_dias():
    barato = client.post("/destinos", json={**DESTINO, "nombre": "Rec barato", "dias_recomendados": 2,
                                            "costo_transporte_local": 1, "costo_alojamiento": 1,
                                            "costo_alimentacion": 1, "costo_actividades": 1}).json()["id"]
    caro = client.post("/destinos", json={**DESTINO, "nombre": "Rec caro",
                                          "costo_alojamiento": 9_000_000}).json()["id"]
    sid = client.post("/solicitudes", json=SOLICITUD).json()["id"]
    r = client.post(f"/recomendaciones/{sid}")
    assert r.status_code == 200
    ids = [o["destino"]["id"] for o in r.json()["opciones"]]
    assert barato in ids and caro not in ids
    assert client.post("/recomendaciones/99999").status_code == 404
