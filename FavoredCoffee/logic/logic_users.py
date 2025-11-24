from typing import List, Optional
from sqlmodel import Session, select
from ..models import User
from ..security import get_password_hash
from ..schemas import UserCreate, UserUpdate
from fastapi import HTTPException


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Devuelve un usuario por email o None si no existe."""
    return db.exec(select(User).where(User.email == email)).first()

def get_users(db: Session) -> List[User]:
    """Obtiene la lista completa de usuarios."""
    return db.exec(select(User)).all()

def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=user_data.is_active,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """Actualiza campos del usuario y cambia la contraseña si se envía."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = user_data.dict(exclude_unset=True)
    new_password = data.pop("password", None)

    for key, value in data.items():
        setattr(user, key, value)

    if new_password:
        user.hashed_password = get_password_hash(new_password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_first_admin(session: Session):
    """Crea un usuario admin (v3) por defecto si no existe ninguno."""
    user = session.exec(select(User)).first()
    if not user:
        hashed_password = get_password_hash("admin123")
        admin_user = User(
            email="admin@cafe.com", # <-- Campo actualizado
            full_name="Admin de la Tienda",
            hashed_password=hashed_password,
            role="Admin",
            is_active=True
        )
        session.add(admin_user)
        session.commit()
        print("INFO:     Usuario 'admin@cafe.com' (pass: 'admin123') creado.")

# ... (resto de funciones de lógica de usuario) ...