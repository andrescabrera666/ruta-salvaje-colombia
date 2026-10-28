# Ruta Salvaje Colombia

MVP académico de una API para organizar destinos naturales y propuestas de viaje según presupuesto, días y preferencias.

## Requisitos
- Python 3.11 o posterior recomendado
- pip

## Instalar y ejecutar en Windows (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```
Abrir `http://127.0.0.1:8000/docs`.

## Pruebas
```powershell
pytest -v
```

## Modelos
- Destino
- SolicitudViaje
- Itinerario
- Vuelo

Los registros se guardan en `data/*.csv`; no se usa SQL.

## Nota de vuelos
Los precios son estimados o registrados manualmente. El MVP no consulta automáticamente tarifas de Tiquetes Baratos ni garantiza que un precio siga disponible al momento de comprar.
