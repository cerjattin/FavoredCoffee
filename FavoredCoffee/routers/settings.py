from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import get_session
from ..security import get_current_admin_user
from ..schemas import SettingsSchema
from ..logic import logic_settings

router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
    dependencies=[Depends(get_current_admin_user)] # Protegido
)

@router.get("/", response_model=SettingsSchema)
def read_settings(db: Session = Depends(get_session)):
    return logic_settings.get_settings(db)

@router.put("/", response_model=SettingsSchema)
def write_settings(settings_data: SettingsSchema, db: Session = Depends(get_session)):
    return logic_settings.update_settings(db=db, settings_data=settings_data)