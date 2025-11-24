from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from datetime import date
from ..database import get_session
from ..security import get_current_admin_user
from ..logic import logic_reports

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(get_current_admin_user)] # Protegido
)

@router.get("/sales")
def get_sales_report(
    db: Session = Depends(get_session),
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    """
    Endpoint principal de Reportes.
    Genera un reporte completo de ventas basado en un rango de fechas.
    """
    return logic_reports.get_sales_report(db, start_date, end_date)