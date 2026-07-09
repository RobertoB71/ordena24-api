from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

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
    imagen_url: str | None = None



class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    precio: float | None = None
    categoria_id: int | None = None
    disponible: bool | None = None
    imagen_url: str | None = None


class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True


# -------------------------
# Pedidos
# -------------------------

class DetallePedidoCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    usuario_id: int | None = None
    cliente_nombre: str
    cliente_email: EmailStr
    telefono: str | None = None
    direccion_entrega: str
    detalle: list[DetallePedidoCreate]


class DetallePedidoResponse(BaseModel):
    id: int
    producto_id: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float

    class Config:
        from_attributes = True


class PedidoUpdateEstado(BaseModel):
    estado: str


class PedidoResponse(BaseModel):
    id: int
    usuario_id: int | None = None
    cliente_nombre: str
    cliente_email: str
    telefono: str | None = None
    direccion_entrega: str
    subtotal: float
    costo_envio: float
    total: float
    estado: str
    fecha_registro: datetime
    detalle: list[DetallePedidoResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
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


class RolResponse(BaseModel):
    id: int
    descripcion: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse