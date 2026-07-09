from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from database.api_database import get_db
from models.api_models import Categoria, Producto
from schemas.schemas import ProductoResponse


router = APIRouter(
    prefix="/api/productos",
    tags=["Productos"]
)


UPLOAD_DIR = Path("/app/uploads/productos")

EXTENSIONES_PERMITIDAS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}

TAMANO_MAXIMO = 5 * 1024 * 1024


@router.get("/", response_model=list[ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).order_by(
        Producto.id.asc()
    ).all()


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
async def crear_producto(
    nombre: str = Form(...),
    descripcion: str | None = Form(None),
    precio: float = Form(...),
    categoria_id: int = Form(...),
    disponible: bool = Form(True),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
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

    if precio <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio debe ser mayor que cero"
        )

    imagen_url = None
    ruta_archivo = None

    if imagen:
        extension = EXTENSIONES_PERMITIDAS.get(imagen.content_type)

        if not extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten imágenes PNG, JPG o WEBP"
            )

        contenido = await imagen.read()

        if len(contenido) > TAMANO_MAXIMO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La imagen no puede superar los 5 MB"
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        nombre_archivo = f"{uuid4().hex}{extension}"
        ruta_archivo = UPLOAD_DIR / nombre_archivo
        ruta_archivo.write_bytes(contenido)

        imagen_url = f"/uploads/productos/{nombre_archivo}"

    nuevo_producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria_id=categoria_id,
        disponible=disponible,
        imagen_url=imagen_url
    )

    try:
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)

        return nuevo_producto

    except Exception:
        db.rollback()

        if ruta_archivo and ruta_archivo.exists():
            ruta_archivo.unlink()

        raise

    finally:
        if imagen:
            await imagen.close()


@router.put("/{producto_id}", response_model=ProductoResponse)
async def actualizar_producto(
    producto_id: int,
    nombre: str | None = Form(None),
    descripcion: str | None = Form(None),
    precio: float | None = Form(None),
    categoria_id: int | None = Form(None),
    disponible: bool | None = Form(None),
    imagen: UploadFile | None = File(None),
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

    if categoria_id is not None:
        categoria = db.query(Categoria).filter(
            Categoria.id == categoria_id
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

        producto.categoria_id = categoria_id

    if nombre is not None:
        producto.nombre = nombre

    if descripcion is not None:
        producto.descripcion = descripcion

    if precio is not None:
        if precio <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio debe ser mayor que cero"
            )

        producto.precio = precio

    if disponible is not None:
        producto.disponible = disponible

    ruta_nueva = None
    ruta_anterior = None

    if imagen:
        extension = EXTENSIONES_PERMITIDAS.get(imagen.content_type)

        if not extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten imágenes PNG, JPG o WEBP"
            )

        contenido = await imagen.read()

        if len(contenido) > TAMANO_MAXIMO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La imagen no puede superar los 5 MB"
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        nombre_archivo = f"{uuid4().hex}{extension}"
        ruta_nueva = UPLOAD_DIR / nombre_archivo
        ruta_nueva.write_bytes(contenido)

        if producto.imagen_url:
            ruta_anterior = Path("/app") / producto.imagen_url.lstrip("/")

        producto.imagen_url = f"/uploads/productos/{nombre_archivo}"

    try:
        db.commit()
        db.refresh(producto)

        if ruta_anterior and ruta_anterior.exists():
            ruta_anterior.unlink()

        return producto

    except Exception:
        db.rollback()

        if ruta_nueva and ruta_nueva.exists():
            ruta_nueva.unlink()

        raise

    finally:
        if imagen:
            await imagen.close()


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