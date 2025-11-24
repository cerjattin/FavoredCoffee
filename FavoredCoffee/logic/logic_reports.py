from fastapi import HTTPException
import pytz
from datetime import datetime, timedelta
from sqlmodel import Session, select, func
from sqlalchemy.orm import joinedload
from sqlalchemy import Date, cast

from ..models import Order, OrderItem, Product
from ..logic.logic_orders import TIMEZONE
from ..schemas import OrderResponse # Usaremos el schema de respuesta

def get_sales_report(db: Session, start_date: datetime.date, end_date: datetime.date):
    """
    Calcula el reporte de ventas para un rango de fechas.
    Implementa las Reglas de Negocio 3, 4 y 5.
    """
    
    # --- Configuración de Fechas (UTC) ---
    try:
        start_time_local = TIMEZONE.localize(datetime.combine(start_date, datetime.min.time()))
        end_time_local = TIMEZONE.localize(datetime.combine(end_date, datetime.max.time()))
        
        start_utc = start_time_local.astimezone(pytz.utc)
        end_utc = end_time_local.astimezone(pytz.utc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Rango de fechas inválido: {e}")

    # --- 1. Métricas Principales (Regla 4: Solo 'Pagada') ---
    main_metrics_query = db.exec(
        select(
            func.sum(Order.total_amount),
            func.count(Order.id),
            func.avg(Order.total_amount)
        ).where(
            Order.status == "Pagada",
            Order.created_at >= start_utc,
            Order.created_at <= end_utc
        )
    ).first()
    
    total_revenue = main_metrics_query[0] or 0.0
    total_orders = main_metrics_query[1] or 0
    average_ticket = main_metrics_query[2] or 0.0

    # Base query para todos los reportes (Regla 4)
    base_query = (
        select(OrderItem, Product, Order)
        .join(Product, OrderItem.product_id == Product.id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            Order.status == "Pagada",
            Order.created_at >= start_utc,
            Order.created_at <= end_utc
        )
    )
    
    report_items = db.exec(base_query).all()

    # --- 2. Top Productos y Categorías (Regla 5: Unidades) ---
    top_products = {}
    sales_by_category = {}

    for item, product, order in report_items:
        # Top Productos
        top_products[product.name] = top_products.get(product.name, 0) + item.quantity
        # Top Categorías
        sales_by_category[product.category] = sales_by_category.get(product.category, 0) + item.quantity
    
    # Ordenar y formatear
    top_products_list = [
        {"name": k, "units": v} for k, v in sorted(top_products.items(), key=lambda i: i[1], reverse=True)
    ]
    sales_by_category_list = [
        {"name": k, "units": v} for k, v in sorted(sales_by_category.items(), key=lambda i: i[1], reverse=True)
    ]

    # --- 3. Evolución de Ventas (Regla 3: Semanal) ---
    sales_over_time = {}
    for item, product, order in report_items:
        # Agrupar por el Lunes de esa semana
        order_date_local = order.created_at.astimezone(TIMEZONE).date()
        start_of_week = order_date_local - timedelta(days=order_date_local.weekday())
        week_key = start_of_week.isoformat()
        
        # Usamos un set para contar órdenes únicas por semana
        if week_key not in sales_over_time:
            sales_over_time[week_key] = {"total_sales": 0.0, "order_ids": set()}
        
        # Evitar doble conteo si una orden tiene múltiples items
        if order.id not in sales_over_time[week_key]["order_ids"]:
            sales_over_time[week_key]["total_sales"] += order.total_amount
            sales_over_time[week_key]["order_ids"].add(order.id)

    sales_over_time_list = [
        {"period": k, "total_sales": v["total_sales"]} for k, v in sorted(sales_over_time.items())
    ]

    # --- 4. Resumen Detallado de Ventas ---
    # Re-consultar órdenes con carga ansiosa (eager loading)
    detailed_orders = db.exec(
        select(Order)
        .options(
            joinedload(Order.user), # Cargar info del usuario
            joinedload(Order.items).joinedload(OrderItem.product) # Cargar items y sus productos
        )
        .where(
            Order.status == "Pagada", # (Regla 4)
            Order.created_at >= start_utc,
            Order.created_at <= end_utc
        )
        .order_by(Order.created_at.desc())
    ).all()

    # Convertir a schemas de respuesta (costoso pero completo)
    detailed_sales_response = []
    for order in detailed_orders:
        detailed_sales_response.append(
            OrderResponse(
                id=order.id,
                created_at=order.created_at,
                status=order.status,
                payment_method=order.payment_method,
                subtotal=order.subtotal,
                tax_amount=order.tax_amount,
                total_amount=order.total_amount,
                user_id=order.user_id,
                user_full_name=order.user.full_name if order.user else "N/A",
                items=[
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price_at_purchase": item.price_at_purchase,
                        "product_name": item.product.name if item.product else "N/A"
                    } for item in order.items
                ]
            )
        )

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_ticket": average_ticket,
        "top_products": top_products_list,
        "sales_by_category": sales_by_category_list,
        "sales_over_time": sales_over_time_list,
        "detailed_sales": detailed_sales_response
    }