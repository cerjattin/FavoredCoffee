from fastapi import HTTPException
from sqlmodel import Session, select
from ..models import BusinessSettings
from ..schemas import SettingsSchema

def get_settings(db: Session) -> BusinessSettings:
    """Obtiene la configuración actual del negocio."""
    settings = db.get(BusinessSettings, 1) # ID es siempre 1
    if not settings:
        # Esto es llamado por on_startup, así que debe existir
        settings = create_initial_settings(db)
    return settings

def update_settings(db: Session, settings_data: SettingsSchema) -> BusinessSettings:
    """Actualiza la configuración del negocio."""
    settings = db.get(BusinessSettings, 1)
    if not settings:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    settings_data_dict = settings_data.dict(exclude_unset=True)
    for key, value in settings_data_dict.items():
        setattr(settings, key, value)
    
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings

def create_initial_settings(db: Session) -> BusinessSettings:
    """Crea la configuración inicial si no existe."""
    settings = db.get(BusinessSettings, 1)
    if not settings:
        settings = BusinessSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
        print("INFO:     Configuración de negocio inicial creada.")
    return settings