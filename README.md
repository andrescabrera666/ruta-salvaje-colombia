# Ruta Salvaje Colombia

API académica (FastAPI) para organizar destinos naturales y recomendar viajes según presupuesto, días y preferencias.
Sin SQL: todo se guarda en archivos CSV.

## Estructura
```
main.py            API: endpoints agrupados por secciones (Destinos, Solicitudes, Vuelos, Itinerarios, Recomendaciones)
crud.py            Repositorio CSV con borrado conservando historial
models.py          Modelos Pydantic (Destino, SolicitudViaje, Vuelo, Itinerario)
app/routers.py     Fábrica de routers CRUD
data/activos/      CSV con los registros vigentes
data/eliminados/   CSV con los registros borrados (incluyen fecha_eliminacion)
tests/             Pruebas con pytest (usan carpeta temporal, no tocan data/)
```

## Lógica de borrado
`DELETE /<entidad>/{id}` **no destruye** el registro: lo mueve de `data/activos/<entidad>.csv`
a `data/eliminados/<entidad>.csv` con su `fecha_eliminacion`.
- `GET /<entidad>/historial` lista lo eliminado.
- `POST /<entidad>/{id}/restaurar` lo devuelve a activos.
- Los IDs eliminados nunca se reutilizan.

## Instalar y ejecutar (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```
Abrir http://127.0.0.1:8000/docs

## Pruebas
```powershell
pytest -v
```
