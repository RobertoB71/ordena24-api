from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.api_database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(100), nullable=False, unique=True)
    activo = Column(Boolean, nullable=False, default=True)


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False)
    categoria_id = Column(Integer, nullable=False)
    disponible = Column(Boolean, nullable=False, default=True)
    imagen_url = Column(String(255), nullable=True)

    detalles_pedido = relationship(
        "DetallePedido",
        back_populates="producto"
    )

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, nullable=True)

    cliente_nombre = Column(String(150), nullable=False)
    cliente_email = Column(String(150), nullable=False)
    telefono = Column(String(30), nullable=True)
    direccion_entrega = Column(Text, nullable=False)

    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    costo_envio = Column(Numeric(10, 2), nullable=False, default=0)
    total = Column(Numeric(10, 2), nullable=False, default=0)

    estado = Column(String(30), nullable=False, default="Pendiente")

    fecha_registro = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now()
    )

    detalle = relationship(
        "DetallePedido",
        back_populates="pedido",
        cascade="all, delete-orphan"
    )


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id = Column(Integer, primary_key=True, index=True)

    pedido_id = Column(
        Integer,
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False
    )

    producto_id = Column(
        Integer,
        ForeignKey("productos.id"),
        nullable=False
    )

    nombre_producto = Column(String(150), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    pedido = relationship(
        "Pedido",
        back_populates="detalle"
    )

    producto = relationship(
        "Producto",
        back_populates="detalles_pedido"
    )