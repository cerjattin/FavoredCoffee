import pytz
from datetime import datetime, timedelta
from sqlmodel import Session, select, func
from sqlalchemy import case

from ..models import Order, OrderItem, Product
from ..logic.logic_settings import get_settings
from ..logic.logic_orders import TIMEZONE # Importamos la zona horaria

def get_dashboard_stats(db: Session):
    """
    Calcula las estadísticas para el Dashboard principal.
    Implementa las Reglas de Negocio 1 y 2.
    """
    
    # --- Configuración de Fechas (Regla 1) ---
    today = datetime.now(TIMEZONE).date()
    
    # Inicio de esta semana (Lunes 00:00)
    start_of_this_week_local = today - timedelta(days=today.weekday())
    start_of_this_week_utc = TIMEZONE.localize(
        datetime.combine(start_of_this_week_local, datetime.min.time())
    ).astimezone(pytz.utc)

    # Inicio de la semana pasada (Lunes anterior 00:00)
    start_of_last_week_local = start_of_this_week_local - timedelta(days=7)
    start_of_last_week_utc = TIMEZONE.localize(
        datetime.combine(start_of_last_week_local, datetime.min.time())
    ).astimezone(pytz.utc)
    
    # Fin de la semana pasada (Domingo anterior 23:59:59)
    end_of_last_week_utc = start_of_this_week_utc - timedelta(seconds=1)

    # --- 1. Estadísticas de Ventas (Regla 1) ---
    
    # Ventas de esta semana (Mon-Hoy)
    stats_this_week = db.exec(
        select(
            func.sum(Order.total_amount),
            func.count(Order.id)
        ).where(
            Order.status == "Pagada",
            Order.created_at >= start_of_this_week_utc
        )
    ).first()
    
    total_revenue_this_week = stats_this_week[0] or 0.0
    total_orders_this_week = stats_this_week[1] or 0

    # Ventas de la semana pasada (Mon-Sun)
    stats_last_week = db.exec(
        select(
            func.sum(Order.total_amount),
            func.count(Order.id)
        ).where(
            Order.status == "Pagada",
            Order.created_at >= start_of_last_week_utc,
            Order.created_at <= end_of_last_week_utc
        )
    ).first()
    
    total_revenue_last_week = stats_last_week[0] or 0.0
    total_orders_last_week = stats_last_week[1] or 0
    
    # --- 2. Alertas de Inventario (de la UI) ---
    settings = get_settings(db)
    low_stock_count = db.exec(
        select(func.count(Product.id))
        .where(Product.stock <= settings.low_stock_threshold)
        .where(Product.stock > 0) # Opcional: solo si hay stock
    ).one()

    # --- 3. Top Productos (Regla 2: Unidades) ---
    # Top 3 productos vendidos esta semana
    top_products_query = (
        select(
            Product,
            func.sum(OrderItem.quantity).label("total_units")
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            Order.status == "Pagada",
            Order.created_at >= start_of_this_week_utc
        )
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(3)
    )
    
    top_products_result = db.exec(top_products_query).all()
    # Extraemos solo el objeto Product
    top_products_list = [product for product, units in top_products_result]

    return {
        "sales_this_week": total_revenue_this_week,
        "sales_last_week": total_revenue_last_week,
        "orders_this_week": total_orders_this_week,
        "orders_last_week": total_orders_last_week,
        "low_stock_items_count": low_stock_count,
        "top_products": top_products_list
    }