from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.api_database import get_db
from models.api_models import Categoria, DetallePedido, Pedido, Producto
from schemas.schemas import (
    PedidoCreate,
    PedidoResponse,
    PedidoUpdateEstado
)


router = APIRouter(
    prefix="/api/pedidos",
    tags=["Pedidos"]
)


ESTADOS_VALIDOS = [
    "Pendiente",
    "En preparación",
    "Enviado",
    "Entregado",
    "Cancelado"
]


def redondear_monto(valor: Decimal) -> Decimal:
    return valor.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(db: Session = Depends(get_db)):
    pedidos = db.query(Pedido).order_by(
        Pedido.id.desc()
    ).all()

    return pedidos


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )

    return pedido


@router.post(
    "/",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_pedido(
    pedido: PedidoCreate,
    db: Session = Depends(get_db)
):
    if not pedido.detalle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El pedido debe contener al menos un producto"
        )

    subtotal_pedido = Decimal("0.00")
    detalles_preparados = []
    
    productos_recibidos = set()

    for item in pedido.detalle:
        
        if item.producto_id in productos_recibidos:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El producto con ID {item.producto_id} está repetido"
        )

        productos_recibidos.add(item.producto_id)
        
        producto = db.query(Producto).filter(
            Producto.id == item.producto_id
        ).first()
        
        

        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {item.producto_id} no encontrado"
            )

        if not producto.disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto '{producto.nombre}' no está disponible"
            )

        categoria = db.query(Categoria).filter(
            Categoria.id == producto.categoria_id
        ).first()

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La categoría del producto '{producto.nombre}' no existe"
            )

        if not categoria.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La categoría del producto '{producto.nombre}' está deshabilitada"
            )
            

        precio_unitario = Decimal(producto.precio)
        subtotal_detalle = redondear_monto(
            precio_unitario * item.cantidad
        )

        subtotal_pedido += subtotal_detalle

        detalles_preparados.append({
            "producto_id": producto.id,
            "nombre_producto": producto.nombre,
            "cantidad": item.cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal_detalle
        })

    subtotal_pedido = redondear_monto(subtotal_pedido)

    costo_envio = redondear_monto(
        subtotal_pedido * Decimal("0.05")
    )

    total = redondear_monto(
        subtotal_pedido + costo_envio
    )

    nuevo_pedido = Pedido(
        usuario_id=pedido.usuario_id,
        cliente_nombre=pedido.cliente_nombre,
        cliente_email=pedido.cliente_email,
        telefono=pedido.telefono,
        direccion_entrega=pedido.direccion_entrega,
        subtotal=subtotal_pedido,
        costo_envio=costo_envio,
        total=total,
        estado="Pendiente"
    )

    try:
        db.add(nuevo_pedido)
        db.flush()

        for item in detalles_preparados:
            nuevo_detalle = DetallePedido(
                pedido_id=nuevo_pedido.id,
                producto_id=item["producto_id"],
                nombre_producto=item["nombre_producto"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                subtotal=item["subtotal"]
            )

            db.add(nuevo_detalle)

        db.commit()
        db.refresh(nuevo_pedido)

        return nuevo_pedido

    except Exception:
        db.rollback()
        raise


@router.put(
    "/{pedido_id}/estado",
    response_model=PedidoResponse
)
def actualizar_estado_pedido(
    pedido_id: int,
    data: PedidoUpdateEstado,
    db: Session = Depends(get_db)
):
    if data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Estado no válido. "
                f"Estados permitidos: {ESTADOS_VALIDOS}"
            )
        )

    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )

    pedido.estado = data.estado

    db.commit()
    db.refresh(pedido)

    return pedido