from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, model_validator


class DestinoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    departamento: str = Field(min_length=2, max_length=80)
    descripcion: str = Field(min_length=5, max_length=1000)
    tipo_turismo: str = Field(min_length=2, max_length=80)
    dias_recomendados: int = Field(ge=1, le=60)
    costo_transporte_local: float = Field(ge=0)
    costo_alojamiento: float = Field(ge=0)
    costo_alimentacion: float = Field(ge=0)
    costo_actividades: float = Field(ge=0)


class Destino(DestinoCreate):
    id: int = Field(gt=0)


class SolicitudViajeCreate(BaseModel):
    ciudad_origen: str = Field(min_length=2, max_length=100)
    presupuesto: float = Field(gt=0, description="Presupuesto total en pesos colombianos")
    dias_disponibles: int = Field(ge=1, le=90)
    preferencia_turistica: str = Field(min_length=2, max_length=100)
    numero_personas: int = Field(ge=1, le=50)


class SolicitudViaje(SolicitudViajeCreate):
    id: int = Field(gt=0)


class VueloCreate(BaseModel):
    ciudad_origen: str = Field(min_length=2, max_length=100)
    ciudad_destino: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0, description="Precio registrado en COP")
    proveedor: str = Field(min_length=2, max_length=100)
    url_compra: str = Field(min_length=8, max_length=500, description="Enlace al proveedor o búsqueda")
    fecha_consulta: datetime | None = None
    estado_precio: Literal["estimado", "consultado", "desactualizado"] = "estimado"


class Vuelo(VueloCreate):
    id: int = Field(gt=0)


class ItinerarioCreate(BaseModel):
    solicitud_id: int = Field(gt=0)
    destino_id: int = Field(gt=0)
    vuelo_id: int | None = Field(default=None, gt=0)
    dias: int = Field(ge=1, le=90)
    costo_vuelo: float = Field(ge=0, description="Precio del vuelo usado en este cálculo; puede ser 0 si no aplica")
    costo_transporte_local: float = Field(ge=0)
    costo_alojamiento: float = Field(ge=0)
    costo_alimentacion: float = Field(ge=0)
    costo_actividades: float = Field(ge=0)
    recomendacion: str = Field(min_length=5, max_length=1000)


class Itinerario(ItinerarioCreate):
    id: int = Field(gt=0)
    costo_total: float = Field(ge=0)

    @model_validator(mode="before")
    @classmethod
    def calcular_total_si_no_viene(cls, data):
        if isinstance(data, dict) and "costo_total" not in data:
            keys = ["costo_vuelo", "costo_transporte_local", "costo_alojamiento", "costo_alimentacion", "costo_actividades"]
            if all(key in data for key in keys):
                data = {**data, "costo_total": sum(float(data[key]) for key in keys)}
        return data


# Modelos de respuesta que leen los registros desde CSV y los validan con Pydantic.
Destino.model_config = ConfigDict(from_attributes=True)
