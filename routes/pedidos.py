from fastapi import APIRouter, HTTPException
from schemas.schemas import PedidoCreate, PedidoResponse, PedidoUpdateEstado

router = APIRouter(
    prefix="/api/pedidos",
    tags=["Pedidos"]
)

pedidos = [
    {
        "id": 1,
        "cliente_nombre": "Juan Pérez",
        "cliente_email": "juan@example.com",
        "direccion_entrega": "Ciudad de Panamá, Vía España",
        "telefono": "6000-0000",
        "total": 9.25,
        "estado": "Pendiente",
        "detalle": [
            {
                "producto_id": 1,
                "nombre_producto": "Hamburguesa Clásica",
                "cantidad": 1,
                "precio_unitario": 6.50,
                "subtotal": 6.50
            },
            {
                "producto_id": 2,
                "nombre_producto": "Papas Fritas",
                "cantidad": 1,
                "precio_unitario": 2.75,
                "subtotal": 2.75
            }
        ]
    }
]


@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos():
    return pedidos


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(pedido_id: int):
    for pedido in pedidos:
        if pedido["id"] == pedido_id:
            return pedido

    raise HTTPException(status_code=404, detail="Pedido no encontrado")


@router.post("/", response_model=PedidoResponse, status_code=201)
def crear_pedido(pedido: PedidoCreate):
    nuevo_pedido = {
        "id": len(pedidos) + 1,
        "cliente_nombre": pedido.cliente_nombre,
        "cliente_email": pedido.cliente_email,
        "direccion_entrega": pedido.direccion_entrega,
        "telefono": pedido.telefono,
        "total": pedido.total,
        "estado": pedido.estado,
        "detalle": [item.model_dump() for item in pedido.detalle]
    }

    pedidos.append(nuevo_pedido)

    return nuevo_pedido


@router.put("/{pedido_id}/estado", response_model=PedidoResponse)
def actualizar_estado_pedido(pedido_id: int, estado_pedido: PedidoUpdateEstado):
    estados_validos = ["Pendiente", "En preparación", "En camino", "Entregado", "Cancelado"]

    if estado_pedido.estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado no válido. Estados permitidos: {estados_validos}"
        )

    for pedido in pedidos:
        if pedido["id"] == pedido_id:
            pedido["estado"] = estado_pedido.estado
            return pedido

    raise HTTPException(status_code=404, detail="Pedido no encontrado")


@router.delete("/{pedido_id}")
def eliminar_pedido(pedido_id: int):
    for pedido in pedidos:
        if pedido["id"] == pedido_id:
            pedidos.remove(pedido)
            return {
                "message": "Pedido eliminado correctamente"
            }

    raise HTTPException(status_code=404, detail="Pedido no encontrado")