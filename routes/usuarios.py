from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.webapp_database import get_webapp_db
from models.webapp_models import Usuario, Rol
from schemas.schemas import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
    RolResponse
)
from utils.security import encriptar_password

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_webapp_db)):
    usuarios = db.query(Usuario).order_by(
        Usuario.id.asc()
    ).all()

    return usuarios


@router.get("/roles", response_model=list[RolResponse])
def listar_roles(db: Session = Depends(get_webapp_db)):
    roles = db.query(Rol).order_by(
        Rol.id.asc()
    ).all()

    return roles


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_webapp_db)):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_webapp_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if data.rol_id is not None:
        rol = db.query(Rol).filter(
            Rol.id == data.rol_id
        ).first()

        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El rol indicado no existe"
            )

        usuario.rol_id = data.rol_id

    if data.nombre is not None:
        usuario.nombre = data.nombre

    if data.email is not None:
        usuario_email_existente = db.query(Usuario).filter(
            Usuario.email == data.email,
            Usuario.id != usuario_id
        ).first()

        if usuario_email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está siendo usado por otro usuario"
            )

        usuario.email = data.email

    db.commit()
    db.refresh(usuario)

    return usuario


@router.put("/{usuario_id}/deshabilitar", response_model=UsuarioResponse)
def deshabilitar_usuario(
    usuario_id: int,
    db: Session = Depends(get_webapp_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    usuario.activo = False

    db.commit()
    db.refresh(usuario)

    return usuario


@router.put("/{usuario_id}/habilitar", response_model=UsuarioResponse)
def habilitar_usuario(
    usuario_id: int,
    db: Session = Depends(get_webapp_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    usuario.activo = True

    db.commit()
    db.refresh(usuario)

    return usuario

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_webapp_db)
):
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == data.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )

    rol = db.query(Rol).filter(
        Rol.id == data.rol_id
    ).first()

    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol indicado no existe"
        )

    nuevo_usuario = Usuario(
        nombre=data.nombre,
        email=data.email,
        password=encriptar_password(data.password),
        rol_id=data.rol_id,
        activo=True
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario