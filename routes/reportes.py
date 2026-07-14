from decimal import Decimal
from io import BytesIO
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from database.api_database import get_db
from models.api_models import Pedido


router = APIRouter(
    prefix="/api/reportes",
    tags=["Reportes"]
)


EstadoPedido = Literal[
    "Pendiente",
    "En preparación",
    "Enviado",
    "Entregado",
    "Cancelado"
]


@router.get("/pedidos/pdf")
def generar_reporte_pedidos_pdf(
    estado: EstadoPedido | None = None,
    db: Session = Depends(get_db)
):
    consulta = db.query(Pedido)

    if estado:
        consulta = consulta.filter(
            Pedido.estado == estado
        )

    pedidos = consulta.order_by(
        Pedido.fecha_registro.desc()
    ).all()

    if not pedidos:
        mensaje = (
            f"No existen pedidos con estado '{estado}'"
            if estado
            else "No existen pedidos registrados"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=mensaje
        )

    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
        title="Reporte de pedidos Ordena24"
    )

    estilos = getSampleStyleSheet()
    elementos = []

    titulo = "Reporte de pedidos"

    if estado:
        titulo += f" - {estado}"

    elementos.append(
        Paragraph(titulo, estilos["Title"])
    )
    elementos.append(Spacer(1, 0.2 * inch))

    datos_tabla = [[
        "ID",
        "Cliente",
        "Correo",
        "Teléfono",
        "Subtotal",
        "Envío",
        "Total",
        "Estado",
        "Fecha"
    ]]

    for pedido in pedidos:
        fecha = (
            pedido.fecha_registro.strftime("%d/%m/%Y %H:%M")
            if pedido.fecha_registro
            else "-"
        )

        datos_tabla.append([
            str(pedido.id),
            pedido.cliente_nombre,
            pedido.cliente_email,
            pedido.telefono or "-",
            f"${Decimal(pedido.subtotal):.2f}",
            f"${Decimal(pedido.costo_envio):.2f}",
            f"${Decimal(pedido.total):.2f}",
            pedido.estado,
            fecha
        ])

    tabla = Table(
        datos_tabla,
        repeatRows=1,
        colWidths=[
            35,
            105,
            130,
            75,
            65,
            60,
            65,
            85,
            100
        ]
    )

    tabla.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#1F2937")
        ),
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.white
        ),
        (
            "FONTNAME",
            (0, 0),
            (-1, 0),
            "Helvetica-Bold"
        ),
        (
            "ALIGN",
            (0, 0),
            (-1, 0),
            "CENTER"
        ),
        (
            "ALIGN",
            (4, 1),
            (6, -1),
            "RIGHT"
        ),
        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            8
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.grey
        ),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [
                colors.white,
                colors.HexColor("#F3F4F6")
            ]
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            6
        )
    ]))

    elementos.append(tabla)
    elementos.append(Spacer(1, 0.2 * inch))

    total_general = sum(
        Decimal(pedido.total)
        for pedido in pedidos
    )

    resumen = (
        f"Cantidad de pedidos: {len(pedidos)}"
        f" | Total acumulado: ${total_general:.2f}"
    )

    elementos.append(
        Paragraph(resumen, estilos["Heading3"])
    )

    documento.build(elementos)

    buffer.seek(0)

    nombre_estado = (
        estado.lower()
        .replace(" ", "_")
        .replace("ó", "o")
        .replace("í", "i")
        if estado
        else "todos"
    )

    nombre_archivo = f"reporte_pedidos_{nombre_estado}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{nombre_archivo}"'
            )
        }
    )