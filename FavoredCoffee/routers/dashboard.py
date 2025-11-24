from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import get_session
from ..security import get_current_admin_user
from ..logic import logic_dashboard

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_admin_user)] # Protegido
)

@router.get("/stats")
def get_dashboard_statistics(db: Session = Depends(get_session)):
    """
    Endpoint para el Dashboard Principal.
    Calcula ventas, órdenes, % de cambio, stock bajo y top productos.
    """
    return logic_dashboard.get_dashboard_stats(db)