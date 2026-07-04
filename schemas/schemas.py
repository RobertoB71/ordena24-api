from pydantic import BaseModel
from pydantic import BaseModel, EmailStr


# -------------------------
# Categorías
# -------------------------

class CategoriaBase(BaseModel):
    descripcion: str
    activo: bool = True


class CategoriaCreate(BaseModel):
    descripcion: str


class CategoriaUpdate(BaseModel):
    descripcion: str | None = None
    activo: bool | None = None


class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True
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


# -------------------------
# Usuarios / Auth
# -------------------------

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol_id: int = 1


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: EmailStr | None = None
    rol_id: int | None = None


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol_id: int | None = None
    activo: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse