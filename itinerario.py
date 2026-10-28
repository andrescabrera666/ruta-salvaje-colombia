
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
)


class ItinerarioBase(BaseModel):
    """Campos comunes de un itinerario."""

    solicitud_id: int = Field(gt=0)
    destino_id: int = Field(gt=0)
    vuelo_id: int | None = Field(default=None, gt=0)
    dias: int = Field(ge=1, le=90)

    costo_vuelo: float = Field(ge=0)
    costo_transporte_local: float = Field(ge=0)
    costo_alojamiento: float = Field(ge=0)
    costo_alimentacion: float = Field(ge=0)
    costo_actividades: float = Field(ge=0)

    recomendacion: str = Field(min_length=5, max_length=1000)


class ItinerarioCreate(ItinerarioBase):
    """Datos para crear un itinerario."""
    pass


class ItinerarioUpdate(ItinerarioBase):
    """Datos para actualizar un itinerario."""
    pass


class Itinerario(ItinerarioBase):
    """Itinerario completo con identificador y costo total."""

    id: int = Field(gt=0)
    costo_total: float = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def calcular_total_si_no_viene(cls, data):
        if isinstance(data, dict) and "costo_total" not in data:
            campos_costo = [
                "costo_vuelo",
                "costo_transporte_local",
                "costo_alojamiento",
                "costo_alimentacion",
                "costo_actividades",
            ]

            if all(campo in data for campo in campos_costo):
                data = {
                    **data,
                    "costo_total": sum(
                        float(data[campo])
                        for campo in campos_costo
                    ),
                }

        return data
