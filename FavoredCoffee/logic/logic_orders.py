import pytz
from datetime import datetime
from sqlmodel import Session, select
from ..models import Product, Order, OrderItem, User, BusinessSettings
from ..schemas import OrderRequest
from .logic_settings import get_settings
from fastapi import HTTPException

TIMEZONE = pytz.timezone("America/Bogota")

def create_new_order(db: Session, order_request: OrderRequest, user: User) -> Order:
    
    # 1. Obtener configuración de impuestos
    settings = get_settings(db)
    TAX_RATE = settings.tax_rate

    product_ids = [item.product_id for item in order_request.items]
    if not product_ids:
        raise HTTPException(status_code=400, detail="La orden no tiene productos")

    # 2. Validar stock (bloqueando filas para evitar race conditions)
    statement = select(Product).where(Product.id.in_(product_ids)).with_for_update()
    products_db = db.exec(statement).all()
    products_map = {p.id: p for p in products_db}

    subtotal_calc = 0.0
    items_to_create = []

    for item in order_request.items:
        product = products_map.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto con ID {item.product_id} no encontrado")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para '{product.name}'")
        
        # Acumular subtotal
        price = product.price
        subtotal_calc += price * item.quantity
        
        # Preparar OrderItem (sin guardarlo aún)
        items_to_create.append(
            (product, item.quantity, price) # (Producto, Cantidad, PrecioEnEseMomento)
        )

    try:
        # 3. Calcular impuestos
        tax_amount_calc = round(subtotal_calc * (TAX_RATE / 100), 2)
        total_amount_calc = round(subtotal_calc + tax_amount_calc, 2)

        # 4. Crear la Orden
        new_order = Order(
            user_id=user.id,
            payment_method=order_request.payment_method,
            subtotal=subtotal_calc,
            tax_amount=tax_amount_calc,
            total_amount=total_amount_calc
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # 5. Descontar stock y crear OrderItems
        for (product, quantity, price_at_purchase) in items_to_create:
            # Descontar stock
            product.stock -= quantity
            db.add(product)
            
            # Crear item
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity,
                price_at_purchase=price_at_purchase
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(new_order)
        return new_order
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno al crear la orden: {str(e)}")

