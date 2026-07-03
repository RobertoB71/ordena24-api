from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database.api_database import get_db
from models.api_models import Pedido, DetallePedido, Producto
from schemas.schemas import PedidoCreate, PedidoResponse, PedidoUpdateEstado

router = APIRouter(
    prefix="/api/pedidos",
    tags=["Pedidos"]
)


def construir_respuesta_pedido(pedido: Pedido, db: Session):
    detalle = db.query(DetallePedido).filter(
        DetallePedido.pedido_id == pedido.id
    ).all()

    detalle_respuesta = []

    for item in detalle:
        producto = db.query(Producto).filter(
            Producto.id == item.producto_id
        ).first()

        detalle_respuesta.append({
            "producto_id": item.producto_id,
            "nombre_producto": producto.nombre if producto else "Producto no encontrado",
            "cantidad": item.cantidad,
            "precio_unitario": float(item.precio_unitario),
            "subtotal": float(item.subtotal)
        })

    return {
        "id": pedido.id,
        "cliente_nombre": pedido.cliente_nombre,
        "cliente_email": pedido.cliente_email,
        "direccion_entrega": pedido.direccion_entrega,
        "telefono": pedido.telefono,
        "total": float(pedido.total),
        "estado": pedido.estado,
        "detalle": detalle_respuesta
    }


@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(db: Session = Depends(get_db)):
    pedidos = db.query(Pedido).all()

    return [
        construir_respuesta_pedido(pedido, db)
        for pedido in pedidos
    ]


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    return construir_respuesta_pedido(pedido, db)


@router.post("/", response_model=PedidoResponse, status_code=201)
def crear_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    nuevo_pedido = Pedido(
        cliente_nombre=pedido.cliente_nombre,
        cliente_email=pedido.cliente_email,
        direccion_entrega=pedido.direccion_entrega,
        telefono=pedido.telefono,
        total=pedido.total,
        estado=pedido.estado
    )

    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    for item in pedido.detalle:
        producto = db.query(Producto).filter(
            Producto.id == item.producto_id
        ).first()

        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID {item.producto_id} no encontrado"
            )

        nuevo_detalle = DetallePedido(
            pedido_id=nuevo_pedido.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=item.subtotal
        )

        db.add(nuevo_detalle)

    db.commit()

    return construir_respuesta_pedido(nuevo_pedido, db)


@router.put("/{pedido_id}/estado", response_model=PedidoResponse)
def actualizar_estado_pedido(
    pedido_id: int,
    estado_pedido: PedidoUpdateEstado,
    db: Session = Depends(get_db)
):
    estados_validos = [
        "Pendiente",
        "En preparación",
        "En camino",
        "Entregado",
        "Cancelado"
    ]

    if estado_pedido.estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado no válido. Estados permitidos: {estados_validos}"
        )

    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    pedido.estado = estado_pedido.estado

    db.commit()
    db.refresh(pedido)

    return construir_respuesta_pedido(pedido, db)


@router.delete("/{pedido_id}")
def eliminar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    detalles = db.query(DetallePedido).filter(
        DetallePedido.pedido_id == pedido_id
    ).all()

    for detalle in detalles:
        db.delete(detalle)

    db.delete(pedido)
    db.commit()

    return {
        "message": "Pedido eliminado correctamente"
    }