from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import Producto, Categoria
from schemas.schemas import ProductoCreate, ProductoUpdate, ProductoResponse

router = APIRouter(
    prefix="/api/productos",
    tags=["Productos"]
)


@router.get("/", response_model=list[ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()


@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return producto


@router.post("/", response_model=ProductoResponse, status_code=201)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == producto.categoria_id).first()

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    nuevo_producto = Producto(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        categoria_id=producto.categoria_id,
        disponible=producto.disponible
    )

    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)

    return nuevo_producto


@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int,
    producto_actualizado: ProductoUpdate,
    db: Session = Depends(get_db)
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if producto_actualizado.categoria_id is not None:
        categoria = db.query(Categoria).filter(
            Categoria.id == producto_actualizado.categoria_id
        ).first()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        producto.categoria_id = producto_actualizado.categoria_id

    if producto_actualizado.nombre is not None:
        producto.nombre = producto_actualizado.nombre

    if producto_actualizado.descripcion is not None:
        producto.descripcion = producto_actualizado.descripcion

    if producto_actualizado.precio is not None:
        producto.precio = producto_actualizado.precio

    if producto_actualizado.disponible is not None:
        producto.disponible = producto_actualizado.disponible

    db.commit()
    db.refresh(producto)

    return producto


@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(producto)
    db.commit()

    return {
        "message": "Producto eliminado correctamente"
    }