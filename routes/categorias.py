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


@router.get("/activas", response_model=list[CategoriaResponse])
def listar_categorias_activas(db: Session = Depends(get_db)):
    return db.query(Categoria).filter(Categoria.activo == True).all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return categoria


@router.post("/", response_model=CategoriaResponse, status_code=201)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    categoria_existente = db.query(Categoria).filter(
        Categoria.descripcion == categoria.descripcion
    ).first()

    if categoria_existente:
        raise HTTPException(
            status_code=400,
            detail="La categoría ya existe"
        )

    nueva_categoria = Categoria(
        descripcion=categoria.descripcion,
        activo=True
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

    if categoria_actualizada.descripcion is not None:
        categoria.descripcion = categoria_actualizada.descripcion

    if categoria_actualizada.activo is not None:
        categoria.activo = categoria_actualizada.activo

    db.commit()
    db.refresh(categoria)

    return categoria


@router.delete("/{categoria_id}")
def deshabilitar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    categoria.activo = False

    db.commit()
    db.refresh(categoria)

    return {
        "message": "Categoría deshabilitada correctamente"
    }