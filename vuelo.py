"""Clases Pydantic relacionadas con vuelos en Ruta Salvaje Colombia."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

# =========================
# 3. VUELOS
# =========================
class VueloBase(BaseModel):
    """Campos comunes para registrar información de un vuelo."""
    ciudad_origen: str = Field(min_length=2, max_length=100)
    ciudad_destino: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0, description="Precio registrado en COP")
    proveedor: str = Field(min_length=2, max_length=100)
    url_compra: str = Field(min_length=8, max_length=500, description="Enlace al proveedor o búsqueda")
    fecha_consulta: datetime | None = None
    estado_precio: Literal["estimado", "consultado", "desactualizado"] = "estimado"


class VueloCreate(VueloBase):
    """Datos necesarios para crear un registro de vuelo."""


class VueloUpdate(VueloBase):
    """Datos para actualizar un vuelo. Se envían todos los campos."""


class Vuelo(VueloBase):
    """Vuelo completo almacenado, incluido su identificador."""
    id: int = Field(gt=0)
    model_config = ConfigDict(from_attributes=True)

