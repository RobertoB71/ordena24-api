from pydantic import BaseModel


# -------------------------
# Categorías
# -------------------------

class CategoriaBase(BaseModel):
    nombre: str
    descripcion: str | None = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None


class CategoriaResponse(CategoriaBase):
    id: int


# -------------------------
# Productos
# -------------------------

class ProductoBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    precio: float
    categoria_id: int
    disponible: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    precio: float | None = None
    categoria_id: int | None = None
    disponible: bool | None = None


class ProductoResponse(ProductoBase):
    id: int

# -------------------------
# Pedidos
# -------------------------

class DetallePedidoBase(BaseModel):
    producto_id: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoBase(BaseModel):
    cliente_nombre: str
    cliente_email: str
    direccion_entrega: str
    telefono: str | None = None
    total: float
    estado: str = "Pendiente"
    detalle: list[DetallePedidoBase]


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdateEstado(BaseModel):
    estado: str


class PedidoResponse(PedidoBase):
    id: int