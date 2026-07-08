from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.api_database import get_db
from models.api_models import Categoria, Producto
from schemas.schemas import (
    ProductoCreate,
    ProductoResponse,
    ProductoUpdate,
)


router = APIRouter(
    prefix="/api/productos",
    tags=["Productos"]
)


@router.get("/", response_model=list[ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).order_by(
        Producto.id.asc()
    ).all()

    return productos


@router.get("/disponibles", response_model=list[ProductoResponse])
def listar_productos_disponibles(db: Session = Depends(get_db)):
    productos = db.query(Producto).filter(
        Producto.disponible.is_(True)
    ).order_by(
        Producto.id.asc()
    ).all()

    productos_visibles = []

    for producto in productos:
        categoria = db.query(Categoria).filter(
            Categoria.id == producto.categoria_id,
            Categoria.activo.is_(True)
        ).first()

        if categoria:
            productos_visibles.append(producto)

    return productos_visibles


@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):
    producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()

    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    return producto


@router.post(
    "/",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db)
):
    categoria = db.query(Categoria).filter(
        Categoria.id == producto.categoria_id
    ).first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    if not categoria.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede crear un producto en una categoría deshabilitada"
        )

    if producto.precio <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio debe ser mayor que cero"
        )

    nuevo_producto = Producto(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        categoria_id=producto.categoria_id,
        disponible=producto.disponible,
        imagen_url=producto.imagen_url
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
    producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()

    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    if producto_actualizado.categoria_id is not None:
        categoria = db.query(Categoria).filter(
            Categoria.id == producto_actualizado.categoria_id
        ).first()

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        if not categoria.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede asignar una categoría deshabilitada"
            )

        producto.categoria_id = producto_actualizado.categoria_id

    if producto_actualizado.nombre is not None:
        producto.nombre = producto_actualizado.nombre

    if producto_actualizado.descripcion is not None:
        producto.descripcion = producto_actualizado.descripcion

    if producto_actualizado.precio is not None:
        if producto_actualizado.precio <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio debe ser mayor que cero"
            )

        producto.precio = producto_actualizado.precio

    if producto_actualizado.disponible is not None:
        producto.disponible = producto_actualizado.disponible

    if producto_actualizado.imagen_url is not None:
        producto.imagen_url = producto_actualizado.imagen_url

    db.commit()
    db.refresh(producto)

    return producto


@router.put("/{producto_id}/estado", response_model=ProductoResponse)
def cambiar_estado_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):
    producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()

    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    nuevo_estado = not producto.disponible

    if nuevo_estado:
        categoria = db.query(Categoria).filter(
            Categoria.id == producto.categoria_id
        ).first()

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría del producto no existe"
            )

        if not categoria.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No se puede habilitar el producto porque "
                    "su categoría está deshabilitada"
                )
            )

    producto.disponible = nuevo_estado

    db.commit()
    db.refresh(producto)

    return producto