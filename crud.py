import csv
from pathlib import Path
from typing import Type
from pydantic import BaseModel


class CSVRepository:
    """Operaciones CRUD sencillas para guardar modelos Pydantic en un archivo CSV."""

    def __init__(self, file_path: str, model: Type[BaseModel]):
        self.path = Path(file_path)
        self.model = model
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_all([])

    def _read_all(self) -> list[dict]:
        with self.path.open("r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def _write_all(self, rows: list[dict]) -> None:
        fields = list(self.model.model_fields.keys())
        with self.path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fields})

    def _to_model(self, row: dict):
        # CSV representa los valores vacíos como "". Convertimos a None
        # cuando el campo del modelo admite None (por ejemplo fecha_consulta).
        cleaned = dict(row)
        for field_name, field_info in self.model.model_fields.items():
            value = cleaned.get(field_name)
            if value == "" and type(None) in getattr(field_info.annotation, "__args__", ()):
                cleaned[field_name] = None
        return self.model.model_validate(cleaned)

    def list(self) -> list:
        return [self._to_model(row) for row in self._read_all()]

    def get(self, record_id: int):
        for row in self._read_all():
            if int(row["id"]) == record_id:
                return self._to_model(row)
        return None

    def create(self, data: dict):
        rows = self._read_all()
        new_id = max((int(row["id"]) for row in rows), default=0) + 1
        record = {"id": new_id, **data}
        validated = self.model.model_validate(record)
        rows.append(validated.model_dump(mode="json"))
        self._write_all(rows)
        return validated

    def update(self, record_id: int, data: dict):
        rows = self._read_all()
        for index, row in enumerate(rows):
            if int(row["id"]) == record_id:
                validated = self.model.model_validate({"id": record_id, **data})
                rows[index] = validated.model_dump(mode="json")
                self._write_all(rows)
                return validated
        return None

    def delete(self, record_id: int) -> bool:
        rows = self._read_all()
        remaining = [row for row in rows if int(row["id"]) != record_id]
        if len(remaining) == len(rows):
            return False
        self._write_all(remaining)
        return True
