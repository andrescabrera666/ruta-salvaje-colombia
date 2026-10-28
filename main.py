from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from models import (
    Destino, DestinoCreate,
    SolicitudViaje, SolicitudViajeCreate,
    Itinerario, ItinerarioCreate,
    Vuelo, VueloCreate,
)
from crud import CSVRepository

DATA = Path(__file__).parent / "data"
app = FastAPI(
    title="Ruta Salvaje Colombia",
    description="API académica para recomendar destinos naturales según presupuesto y días disponibles.",
    version="1.0.0",
)

destinos = CSVRepository(str(DATA / "destinos.csv"), Destino)
solicitudes = CSVRepository(str(DATA / "solicitudes.csv"), SolicitudViaje)
itinerarios = CSVRepository(str(DATA / "itinerarios.csv"), Itinerario)
vuelos = CSVRepository(str(DATA / "vuelos.csv"), Vuelo)

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a Ruta Salvaje Colombia", "documentacion": "/docs"}


def registrar_crud(router_name: str):
    """Función de referencia para explicar la convención CRUD; los endpoints están definidos explícitamente abajo."""
    return router_name

# DESTINOS
@app.post("/destinos", response_model=Destino, status_code=status.HTTP_201_CREATED)
def crear_destino(datos: DestinoCreate):
    return destinos.create(datos.model_dump())

@app.get("/destinos", response_model=list[Destino])
def listar_destinos():
    return destinos.list()

@app.get("/destinos/{record_id}", response_model=Destino)
def obtener_destino(record_id: int):
    item = destinos.get(record_id)
    if item is None:
        raise HTTPException(404, "Destino no encontrado")
    return item

@app.put("/destinos/{record_id}", response_model=Destino)
def actualizar_destino(record_id: int, datos: DestinoCreate):
    item = destinos.update(record_id, datos.model_dump())
    if item is None:
        raise HTTPException(404, "Destino no encontrado")
    return item

@app.delete("/destinos/{record_id}")
def eliminar_destino(record_id: int):
    if not destinos.delete(record_id):
        raise HTTPException(404, "Destino no encontrado")
    return {"mensaje": "Destino eliminado correctamente"}

# SOLICITUDES
@app.post("/solicitudes", response_model=SolicitudViaje, status_code=status.HTTP_201_CREATED)
def crear_solicitud(datos: SolicitudViajeCreate):
    return solicitudes.create(datos.model_dump())

@app.get("/solicitudes", response_model=list[SolicitudViaje])
def listar_solicitudes():
    return solicitudes.list()

@app.get("/solicitudes/{record_id}", response_model=SolicitudViaje)
def obtener_solicitud(record_id: int):
    item = solicitudes.get(record_id)
    if item is None:
        raise HTTPException(404, "Solicitud no encontrada")
    return item

@app.put("/solicitudes/{record_id}", response_model=SolicitudViaje)
def actualizar_solicitud(record_id: int, datos: SolicitudViajeCreate):
    item = solicitudes.update(record_id, datos.model_dump())
    if item is None:
        raise HTTPException(404, "Solicitud no encontrada")
    return item

@app.delete("/solicitudes/{record_id}")
def eliminar_solicitud(record_id: int):
    if not solicitudes.delete(record_id):
        raise HTTPException(404, "Solicitud no encontrada")
    return {"mensaje": "Solicitud eliminada correctamente"}

# VUELOS
@app.post("/vuelos", response_model=Vuelo, status_code=status.HTTP_201_CREATED)
def crear_vuelo(datos: VueloCreate):
    return vuelos.create(datos.model_dump())

@app.get("/vuelos", response_model=list[Vuelo])
def listar_vuelos():
    return vuelos.list()

@app.get("/vuelos/{record_id}", response_model=Vuelo)
def obtener_vuelo(record_id: int):
    item = vuelos.get(record_id)
    if item is None:
        raise HTTPException(404, "Vuelo no encontrado")
    return item

@app.put("/vuelos/{record_id}", response_model=Vuelo)
def actualizar_vuelo(record_id: int, datos: VueloCreate):
    item = vuelos.update(record_id, datos.model_dump())
    if item is None:
        raise HTTPException(404, "Vuelo no encontrado")
    return item

@app.delete("/vuelos/{record_id}")
def eliminar_vuelo(record_id: int):
    if not vuelos.delete(record_id):
        raise HTTPException(404, "Vuelo no encontrado")
    return {"mensaje": "Vuelo eliminado correctamente"}

# ITINERARIOS
@app.post("/itinerarios", response_model=Itinerario, status_code=status.HTTP_201_CREATED)
def crear_itinerario(datos: ItinerarioCreate):
    if solicitudes.get(datos.solicitud_id) is None:
        raise HTTPException(400, "La solicitud asociada no existe")
    if destinos.get(datos.destino_id) is None:
        raise HTTPException(400, "El destino asociado no existe")
    if datos.vuelo_id is not None and vuelos.get(datos.vuelo_id) is None:
        raise HTTPException(400, "El vuelo asociado no existe")
    total = sum([datos.costo_vuelo, datos.costo_transporte_local, datos.costo_alojamiento, datos.costo_alimentacion, datos.costo_actividades])
    payload = {**datos.model_dump(), "costo_total": total}
    return itinerarios.create(payload)

@app.get("/itinerarios", response_model=list[Itinerario])
def listar_itinerarios():
    return itinerarios.list()

@app.get("/itinerarios/{record_id}", response_model=Itinerario)
def obtener_itinerario(record_id: int):
    item = itinerarios.get(record_id)
    if item is None:
        raise HTTPException(404, "Itinerario no encontrado")
    return item

@app.put("/itinerarios/{record_id}", response_model=Itinerario)
def actualizar_itinerario(record_id: int, datos: ItinerarioCreate):
    if solicitudes.get(datos.solicitud_id) is None:
        raise HTTPException(400, "La solicitud asociada no existe")
    if destinos.get(datos.destino_id) is None:
        raise HTTPException(400, "El destino asociado no existe")
    if datos.vuelo_id is not None and vuelos.get(datos.vuelo_id) is None:
        raise HTTPException(400, "El vuelo asociado no existe")
    total = sum([datos.costo_vuelo, datos.costo_transporte_local, datos.costo_alojamiento, datos.costo_alimentacion, datos.costo_actividades])
    payload = {**datos.model_dump(), "costo_total": total}
    item = itinerarios.update(record_id, payload)
    if item is None:
        raise HTTPException(404, "Itinerario no encontrado")
    return item

@app.delete("/itinerarios/{record_id}")
def eliminar_itinerario(record_id: int):
    if not itinerarios.delete(record_id):
        raise HTTPException(404, "Itinerario no encontrado")
    return {"mensaje": "Itinerario eliminado correctamente"}

# RECOMENDACIONES
@app.post("/recomendaciones/{solicitud_id}")
def recomendar_destinos(solicitud_id: int):
    solicitud = solicitudes.get(solicitud_id)
    if solicitud is None:
        raise HTTPException(404, "Solicitud no encontrada")
    opciones = []
    preferencia = solicitud.preferencia_turistica.casefold().strip()
    for destino in destinos.list():
        costo_sin_vuelo = destino.costo_transporte_local + destino.costo_alojamiento + destino.costo_alimentacion + destino.costo_actividades
        # Este primer algoritmo compara costos base por persona; el vuelo puede agregarse como itinerario cuando se registre.
        if costo_sin_vuelo <= solicitud.presupuesto and destino.dias_recomendados <= solicitud.dias_disponibles:
            coincide = preferencia in destino.tipo_turismo.casefold() or destino.tipo_turismo.casefold() in preferencia
            opciones.append({"destino": destino, "costo_base_estimado_por_persona": costo_sin_vuelo, "coincide_preferencia": coincide})
    opciones.sort(key=lambda x: (not x["coincide_preferencia"], x["costo_base_estimado_por_persona"]))
    return {"solicitud_id": solicitud.id, "cantidad_opciones": len(opciones), "nota": "Costos estimados por persona; no incluyen automáticamente una tarifa aérea actual. Verifica precios y logística antes de reservar.", "opciones": opciones}
