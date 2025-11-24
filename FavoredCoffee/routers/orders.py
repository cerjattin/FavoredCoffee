from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_session
from ..security import get_current_seller_user # <-- Usamos el rol de Vendedor
from ..schemas import OrderRequest, OrderResponse
from ..models import User
from ..logic.logic_orders import create_new_order

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("/create", response_model=OrderResponse)
def create_order(
    order_request: OrderRequest,
    # Cambiamos get_current_active_user por get_current_seller_user
    # Esto permite que tanto Vendedores como Admins creen órdenes
    current_user: Annotated[User, Depends(get_current_seller_user)],
    session: Session = Depends(get_session)
):
    """
    Crea una nueva orden. Accesible por Vendedores y Admins.
    """
    new_order = create_new_order(
        db=session, 
        order_request=order_request, 
        user=current_user
    )
    return new_order

# Nota: El endpoint de daily_summary se movió a routers/dashboard.py y routers/reports.py
# por lo que ya no es necesario aquí.