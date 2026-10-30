import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from app.routers import crud_router
from crud import CSVRepository
from models import (
    Destino, DestinoCreate, Itinerario, ItinerarioCreate,
    SolicitudViaje, SolicitudViajeCreate, Vuelo, VueloCreate,
)

# Carpeta de datos (se puede cambiar con la variable RSC_DATA_DIR, útil para pruebas)
DATA = Path(os.environ.get("RSC_DATA_DIR", Path(__file__).parent / "data"))

tags_metadata = [
    {"name": "Inicio", "description": "Bienvenida a la API"},
    {"name": "Destinos", "description": "Destinos naturales: CRUD, búsqueda, filtros e historial"},
    {"name": "Solicitudes", "description": "Solicitudes de viaje de los usuarios"},
    {"name": "Vuelos", "description": "Vuelos registrados"},
    {"name": "Itinerarios", "description": "Itinerarios que combinan solicitud, destino y vuelo"},
    {"name": "Recomendaciones", "description": "Destinos sugeridos según presupuesto y días"},
]

app = FastAPI(
    title="Ruta Salvaje Colombia",
    description="API académica para recomendar destinos naturales según presupuesto y días disponibles.",
    version="2.0.0",
    openapi_tags=tags_metadata,
)


def repo(nombre, modelo):
    return CSVRepository(DATA / "activos" / f"{nombre}.csv",
                         DATA / "eliminados" / f"{nombre}.csv", modelo)


destinos = repo("destinos", Destino)
solicitudes = repo("solicitudes", SolicitudViaje)
vuelos = repo("vuelos", Vuelo)
itinerarios = repo("itinerarios", Itinerario)


@app.get("/", tags=["Inicio"], summary="Inicio")
def inicio():
    return {"mensaje": "Bienvenido a Ruta Salvaje Colombia", "documentacion": "/docs"}


# ---------------- DESTINOS ----------------
def extras_destinos(router):
    @router.get("/buscar", response_model=list[Destino], summary="Buscar destinos por nombre")
    def buscar(nombre: str = Query(min_length=1)):
        return [d for d in destinos.list() if nombre.casefold() in d.nombre.casefold()]

    @router.get("/filtrar", response_model=list[Destino], summary="Filtrar destinos por atributos")
    def filtrar(departamento: str | None = None, tipo_turismo: str | None = None,
                max_dias: int | None = Query(None, ge=1), max_costo: float | None = Query(None, ge=0)):
        res = destinos.list()
        if departamento:
            res = [d for d in res if departamento.casefold() in d.departamento.casefold()]
        if tipo_turismo:
            res = [d for d in res if tipo_turismo.casefold() in d.tipo_turismo.casefold()]
        if max_dias is not None:
            res = [d for d in res if d.dias_recomendados <= max_dias]
        if max_costo is not None:
            res = [d for d in res if d.costo_transporte_local + d.costo_alojamiento
                   + d.costo_alimentacion + d.costo_actividades <= max_costo]
        return res


app.include_router(crud_router(prefix="/destinos", tag="Destinos", repo=destinos, Model=Destino,
                               Create=DestinoCreate, singular="destino", extra=extras_destinos))

# ---------------- SOLICITUDES ----------------
app.include_router(crud_router(prefix="/solicitudes", tag="Solicitudes", repo=solicitudes,
                               Model=SolicitudViaje, Create=SolicitudViajeCreate,
                               singular="solicitud", femenino=True))

# ---------------- VUELOS ----------------
app.include_router(crud_router(prefix="/vuelos", tag="Vuelos", repo=vuelos, Model=Vuelo,
                               Create=VueloCreate, singular="vuelo"))


# ---------------- ITINERARIOS ----------------
def preparar_itinerario(datos: ItinerarioCreate) -> dict:
    if solicitudes.get(datos.solicitud_id) is None:
        raise HTTPException(400, "La solicitud asociada no existe")
    if destinos.get(datos.destino_id) is None:
        raise HTTPException(400, "El destino asociado no existe")
    if datos.vuelo_id is not None and vuelos.get(datos.vuelo_id) is None:
        raise HTTPException(400, "El vuelo asociado no existe")
    total = (datos.costo_vuelo + datos.costo_transporte_local + datos.costo_alojamiento
             + datos.costo_alimentacion + datos.costo_actividades)
    return {**datos.model_dump(), "costo_total": total}


app.include_router(crud_router(prefix="/itinerarios", tag="Itinerarios", repo=itinerarios,
                               Model=Itinerario, Create=ItinerarioCreate, singular="itinerario",
                               before_save=preparar_itinerario))


# ---------------- RECOMENDACIONES ----------------
@app.post("/recomendaciones/{solicitud_id}", tags=["Recomendaciones"],
          summary="Recomendar destinos para una solicitud")
def recomendar_destinos(solicitud_id: int):
    solicitud = solicitudes.get(solicitud_id)
    if solicitud is None:
        raise HTTPException(404, "Solicitud no encontrada")
    pref = solicitud.preferencia_turistica.casefold().strip()
    opciones = []
    for d in destinos.list():
        costo = d.costo_transporte_local + d.costo_alojamiento + d.costo_alimentacion + d.costo_actividades
        if costo <= solicitud.presupuesto and d.dias_recomendados <= solicitud.dias_disponibles:
            tipo = d.tipo_turismo.casefold()
            opciones.append({"destino": d, "costo_base_estimado_por_persona": costo,
                             "coincide_preferencia": pref in tipo or tipo in pref})
    opciones.sort(key=lambda x: (not x["coincide_preferencia"], x["costo_base_estimado_por_persona"]))
    return {"solicitud_id": solicitud.id, "cantidad_opciones": len(opciones),
            "nota": "Costos estimados por persona; no incluyen una tarifa aérea actual. "
                    "Verifica precios y logística antes de reservar.",
            "opciones": opciones}
