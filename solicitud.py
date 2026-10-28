"""Clases Pydantic relacionadas con solicitudes de viaje."""
from pydantic import BaseModel, Field, ConfigDict

# =========================
# 2. SOLICITUDES DE VIAJE
# =========================
class SolicitudViajeBase(BaseModel):
    """Campos comunes de una solicitud de viaje."""
    ciudad_origen: str = Field(min_length=2, max_length=100)
    presupuesto: float = Field(gt=0, description="Presupuesto total en pesos colombianos")
    dias_disponibles: int = Field(ge=1, le=90)
    preferencia_turistica: str = Field(min_length=2, max_length=100)
    numero_personas: int = Field(ge=1, le=50)


class SolicitudViajeCreate(SolicitudViajeBase):
    """Datos necesarios para registrar una solicitud de viaje."""


class SolicitudViajeUpdate(SolicitudViajeBase):
    """Datos para actualizar una solicitud. Se envían todos los campos."""


class SolicitudViaje(SolicitudViajeBase):
    """Solicitud completa almacenada, incluido su identificador."""
    id: int = Field(gt=0)
    model_config = ConfigDict(from_attributes=True)

