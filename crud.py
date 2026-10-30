"""Repositorio CSV con borrado lógico (el borrado conserva historial).

Cada entidad usa dos archivos:
  data/activos/<entidad>.csv      -> registros vigentes
  data/eliminados/<entidad>.csv   -> registros borrados (con fecha_eliminacion)
"""
import csv
from datetime import datetime
from pathlib import Path
from typing import Type

from pydantic import BaseModel

CAMPO_FECHA = "fecha_eliminacion"


class CSVRepository:
    def __init__(self, active_path, deleted_path, model: Type[BaseModel]):
        self.active_path = Path(active_path)
        self.deleted_path = Path(deleted_path)
        self.model = model
        self.fields = list(model.model_fields.keys())
        for path, fields in ((self.active_path, self.fields),
                             (self.deleted_path, self.fields + [CAMPO_FECHA])):
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                self._write(path, [], fields)

    # ---------- utilidades de archivo ----------
    @staticmethod
    def _read(path: Path) -> list[dict]:
        with path.open("r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def _write(path: Path, rows: list[dict], fields: list[str]) -> None:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fields})

    def _to_model(self, row: dict):
        cleaned = {k: row.get(k) for k in self.fields}
        for name, info in self.model.model_fields.items():
            if cleaned[name] == "" and type(None) in getattr(info.annotation, "__args__", ()):
                cleaned[name] = None
        return self.model.model_validate(cleaned)

    def _next_id(self) -> int:
        # Considera también los eliminados para no reutilizar nunca un id.
        ids = [int(r["id"]) for r in self._read(self.active_path) + self._read(self.deleted_path)]
        return max(ids, default=0) + 1

    # ---------- activos ----------
    def list(self) -> list:
        return [self._to_model(r) for r in self._read(self.active_path)]

    def get(self, record_id: int):
        for row in self._read(self.active_path):
            if int(row["id"]) == record_id:
                return self._to_model(row)
        return None

    def create(self, data: dict):
        rows = self._read(self.active_path)
        validated = self.model.model_validate({"id": self._next_id(), **data})
        rows.append(validated.model_dump(mode="json"))
        self._write(self.active_path, rows, self.fields)
        return validated

    def update(self, record_id: int, data: dict):
        rows = self._read(self.active_path)
        for i, row in enumerate(rows):
            if int(row["id"]) == record_id:
                validated = self.model.model_validate({"id": record_id, **data})
                rows[i] = validated.model_dump(mode="json")
                self._write(self.active_path, rows, self.fields)
                return validated
        return None

    # ---------- borrado lógico ----------
    def delete(self, record_id: int):
        """Mueve el registro a eliminados/. Devuelve el registro o None."""
        rows = self._read(self.active_path)
        target = next((r for r in rows if int(r["id"]) == record_id), None)
        if target is None:
            return None
        remaining = [r for r in rows if int(r["id"]) != record_id]
        deleted = self._read(self.deleted_path)
        deleted.append({**target, CAMPO_FECHA: datetime.now().isoformat(timespec="seconds")})
        self._write(self.deleted_path, deleted, self.fields + [CAMPO_FECHA])
        self._write(self.active_path, remaining, self.fields)
        return self._to_model(target)

    def list_deleted(self) -> "list[dict]":
        out = []
        for row in self._read(self.deleted_path):
            data = self._to_model(row).model_dump(mode="json")
            data[CAMPO_FECHA] = row[CAMPO_FECHA]
            out.append(data)
        return out

    def restore(self, record_id: int):
        """Devuelve un registro eliminado a activos. None si no está en el historial."""
        deleted = self._read(self.deleted_path)
        target = next((r for r in deleted if int(r["id"]) == record_id), None)
        if target is None:
            return None
        self._write(self.deleted_path,
                    [r for r in deleted if int(r["id"]) != record_id],
                    self.fields + [CAMPO_FECHA])
        rows = self._read(self.active_path)
        rows.append({k: target[k] for k in self.fields})
        self._write(self.active_path, rows, self.fields)
        return self._to_model(target)
