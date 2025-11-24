from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..database import get_session
from ..security import get_current_admin_user
from ..schemas import User as UserSchema, UserCreate, UserUpdate
from ..logic import logic_users

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_admin_user)] # Protegido
)

@router.post("/", response_model=UserSchema, status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_session)):
    db_user = logic_users.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return logic_users.create_user(db=db, user_data=user_data)

@router.get("/", response_model=List[UserSchema])
def read_users(db: Session = Depends(get_session)):
    return logic_users.get_users(db)

@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_session)):
    return logic_users.update_user(db=db, user_id=user_id, user_data=user_data)