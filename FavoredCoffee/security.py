
import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from .database import get_session
from .models import User

# --- Configuración (sin cambios) ---
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "unaclavesecretav3-muy-dificil")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Funciones Hashing/JWT (sin cambios) ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Dependencia de Usuario Actual (Actualizada) ---
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") # <-- Cambiado de username a email
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.email == email)).first() # <-- Query por email
    
    if user is None or not user.is_active:
        raise credentials_exception
    return user

# --- Dependencias de Roles (Actualizadas) ---
async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Se requieren permisos de Administrador")
    return current_user

async def get_current_seller_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Permite Vendedores O Admins."""
    if current_user.role not in ["Vendedor", "Admin"]:
        raise HTTPException(status_code=403, detail="Se requieren permisos de Vendedor o Administrador")
    return current_user

async def get_current_warehouse_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Permite Bodegueros O Admins."""
    if current_user.role not in ["Bodeguero", "Admin"]:
        raise HTTPException(status_code=403, detail="Se requieren permisos de Bodeguero o Administrador")
    return current_user