"""Fábrica de routers CRUD: cada entidad aparece como su propia sección en /docs."""
from typing import Callable
from fastapi import APIRouter, HTTPException, status


def crud_router(*, prefix, tag, repo, Model, Create, singular, femenino=False,
                before_save: Callable | None = None, extra: Callable | None = None):
    """Crea el CRUD de una entidad con borrado conservando historial."""
    router = APIRouter(prefix=prefix, tags=[tag])
    art = "a" if femenino else "o"
    no_enc = f"{singular.capitalize()} no encontrad{art}"
    prepare = before_save or (lambda d: d.model_dump())

    @router.get("", response_model=list[Model], summary=f"Listar {prefix[1:]} activ{art}s")
    def listar():
        return repo.list()

    @router.post("", response_model=Model, status_code=status.HTTP_201_CREATED,
                 summary=f"Crear {singular}")
    def crear(datos: Create):
        return repo.create(prepare(datos))

    if extra:
        extra(router)  # rutas fijas (buscar, filtrar...) deben ir antes de /{record_id}

    @router.get("/historial", summary=f"Listar {prefix[1:]} eliminad{art}s (historial)")
    def historial():
        return repo.list_deleted()

    @router.get("/{record_id}", response_model=Model, summary=f"Consultar {singular} por ID")
    def obtener(record_id: int):
        item = repo.get(record_id)
        if item is None:
            raise HTTPException(404, no_enc)
        return item

    @router.put("/{record_id}", response_model=Model, summary=f"Actualizar {singular}")
    def actualizar(record_id: int, datos: Create):
        item = repo.update(record_id, prepare(datos))
        if item is None:
            raise HTTPException(404, no_enc)
        return item

    @router.delete("/{record_id}", summary=f"Eliminar {singular} conservando historial")
    def eliminar(record_id: int):
        if repo.delete(record_id) is None:
            raise HTTPException(404, no_enc)
        return {"mensaje": f"{singular.capitalize()} eliminad{art} correctamente (guardad{art} en el historial)"}

    @router.post("/{record_id}/restaurar", response_model=Model,
                 summary=f"Restaurar {singular} eliminad{art}")
    def restaurar(record_id: int):
        item = repo.restore(record_id)
        if item is None:
            raise HTTPException(404, f"{singular.capitalize()} no está en el historial")
        return item

    return router
