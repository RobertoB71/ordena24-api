from fastapi import APIRouter, HTTPException
from schemas.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter(
    prefix="/api/categorias",
    tags=["Categorías"]
)

categorias = [
    {
        "id": 1,
        "nombre": "Comidas rápidas",
        "descripcion": "Hamburguesas, papas fritas y combos rápidos."
    },
    {
        "id": 2,
        "nombre": "Bebidas",
        "descripcion": "Jugos, sodas, agua y bebidas frías."
    }
]


@router.get("/", response_model=list[CategoriaResponse])
def listar_categorias():
    return categorias


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(categoria_id: int):
    for categoria in categorias:
        if categoria["id"] == categoria_id:
            return categoria

    raise HTTPException(status_code=404, detail="Categoría no encontrada")


@router.post("/", response_model=CategoriaResponse, status_code=201)
def crear_categoria(categoria: CategoriaCreate):
    nueva_categoria = {
        "id": len(categorias) + 1,
        "nombre": categoria.nombre,
        "descripcion": categoria.descripcion
    }

    categorias.append(nueva_categoria)

    return nueva_categoria


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria(categoria_id: int, categoria_actualizada: CategoriaUpdate):
    for categoria in categorias:
        if categoria["id"] == categoria_id:
            if categoria_actualizada.nombre is not None:
                categoria["nombre"] = categoria_actualizada.nombre

            if categoria_actualizada.descripcion is not None:
                categoria["descripcion"] = categoria_actualizada.descripcion

            return categoria

    raise HTTPException(status_code=404, detail="Categoría no encontrada")


@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int):
    for categoria in categorias:
        if categoria["id"] == categoria_id:
            categorias.remove(categoria)
            return {
                "message": "Categoría eliminada correctamente"
            }

    raise HTTPException(status_code=404, detail="Categoría no encontrada")