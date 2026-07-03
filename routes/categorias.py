from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database.api_database import get_db
from models.api_models import Categoria
from schemas.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter(
    prefix="/api/categorias",
    tags=["Categorías"]
)


@router.get("/", response_model=list[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return categoria


@router.post("/", response_model=CategoriaResponse, status_code=201)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    nueva_categoria = Categoria(
        nombre=categoria.nombre,
        descripcion=categoria.descripcion
    )

    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)

    return nueva_categoria


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria(
    categoria_id: int,
    categoria_actualizada: CategoriaUpdate,
    db: Session = Depends(get_db)
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if categoria_actualizada.nombre is not None:
        categoria.nombre = categoria_actualizada.nombre

    if categoria_actualizada.descripcion is not None:
        categoria.descripcion = categoria_actualizada.descripcion

    db.commit()
    db.refresh(categoria)

    return categoria


@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    db.delete(categoria)
    db.commit()

    return {
        "message": "Categoría eliminada correctamente"
    }