"""Clases Pydantic relacionadas con destinos turísticos."""
from pydantic import BaseModel, Field, ConfigDict

# =========================
# 1. DESTINOS
# =========================
class DestinoBase(BaseModel):
    """Campos comunes de un destino turístico."""
    nombre: str = Field(min_length=2, max_length=100)
    departamento: str = Field(min_length=2, max_length=80)
    descripcion: str = Field(min_length=5, max_length=1000)
    tipo_turismo: str = Field(min_length=2, max_length=80)
    dias_recomendados: int = Field(ge=1, le=60)
    costo_transporte_local: float = Field(ge=0)
    costo_alojamiento: float = Field(ge=0)
    costo_alimentacion: float = Field(ge=0)
    costo_actividades: float = Field(ge=0)


class DestinoCreate(DestinoBase):
    """Datos necesarios para crear un destino. Hereda de DestinoBase."""


class DestinoUpdate(DestinoBase):
    """Datos para actualizar un destino. En esta API se actualizan todos sus campos."""


class Destino(DestinoBase):
    """Destino completo almacenado, incluido su identificador."""
    id: int = Field(gt=0)
    model_config = ConfigDict(from_attributes=True)

