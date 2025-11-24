from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..database import get_session
from ..models import User
from ..schemas import Token, User as UserSchema
from ..security import (
    create_access_token, verify_password, get_current_user
)
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    # Nota: form_data.username contendrá el EMAIL enviado por el frontend
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
        
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role} # <-- "sub" es el email
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user