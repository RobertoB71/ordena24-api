from fastapi import APIRouter, HTTPException
from schemas.schemas import ProductoCreate, ProductoUpdate, ProductoResponse

router = APIRouter(
    prefix="/api/productos",
    tags=["Productos"]
)

productos = [
    {
        "id": 1,
        "nombre": "Hamburguesa Clásica",
        "descripcion": "Hamburguesa con carne, queso, lechuga, tomate y salsa especial.",
        "precio": 6.50,
        "categoria_id": 1,
        "disponible": True
    },
    {
        "id": 2,
        "nombre": "Papas Fritas",
        "descripcion": "Porción mediana de papas fritas.",
        "precio": 2.75,
        "categoria_id": 1,
        "disponible": True
    },
    {
        "id": 3,
        "nombre": "Soda",
        "descripcion": "Bebida fría en lata.",
        "precio": 1.50,
        "categoria_id": 2,
        "disponible": True
    }
]


@router.get("/", response_model=list[ProductoResponse])
def listar_productos():
    return productos


@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int):
    for producto in productos:
        if producto["id"] == producto_id:
            return producto

    raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.post("/", response_model=ProductoResponse, status_code=201)
def crear_producto(producto: ProductoCreate):
    nuevo_producto = {
        "id": len(productos) + 1,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": producto.precio,
        "categoria_id": producto.categoria_id,
        "disponible": producto.disponible
    }

    productos.append(nuevo_producto)

    return nuevo_producto


@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(producto_id: int, producto_actualizado: ProductoUpdate):
    for producto in productos:
        if producto["id"] == producto_id:
            if producto_actualizado.nombre is not None:
                producto["nombre"] = producto_actualizado.nombre

            if producto_actualizado.descripcion is not None:
                producto["descripcion"] = producto_actualizado.descripcion

            if producto_actualizado.precio is not None:
                producto["precio"] = producto_actualizado.precio

            if producto_actualizado.categoria_id is not None:
                producto["categoria_id"] = producto_actualizado.categoria_id

            if producto_actualizado.disponible is not None:
                producto["disponible"] = producto_actualizado.disponible

            return producto

    raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int):
    for producto in productos:
        if producto["id"] == producto_id:
            productos.remove(producto)
            return {
                "message": "Producto eliminado correctamente"
            }

    raise HTTPException(status_code=404, detail="Producto no encontrado")