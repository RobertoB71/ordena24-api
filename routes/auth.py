from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.webapp_database import get_webapp_db
from models.webapp_models import Usuario, Rol
from schemas.schemas import UsuarioCreate, UsuarioLogin, UsuarioResponse, LoginResponse
from utils.security import encriptar_password, verificar_password, crear_token


router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)


@router.post("/register", response_model=UsuarioResponse)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_webapp_db)):
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == usuario.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )

    rol = db.query(Rol).filter(
        Rol.id == usuario.rol_id
    ).first()

    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol indicado no existe"
        )

    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password=encriptar_password(usuario.password),
        rol_id=usuario.rol_id,
        activo=True
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.post("/login", response_model=LoginResponse)
def login_usuario(data: UsuarioLogin, db: Session = Depends(get_webapp_db)):
    usuario = db.query(Usuario).filter(
        Usuario.email == data.email
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    password_valido = verificar_password(
        data.password,
        usuario.password
    )

    if not password_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está deshabilitado"
        )

    token = crear_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol_id": usuario.rol_id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario
    }