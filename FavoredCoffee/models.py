from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel, EmailStr
import reflex as rx  # Importamos Reflex para los modelos visuales

# ==========================================
# 1. TABLAS DE BASE DE DATOS (BACKEND)
# Estas clases definen tu base de datos y también
# sirven para transportar datos al frontend.
# ==========================================

class BusinessSettings(SQLModel, table=True):
    """Configuración global del negocio."""
    id: Optional[int] = Field(default=1, primary_key=True)
    business_name: str = Field(default="Café Sol")
    tax_id: Optional[str] = Field(default=None)
    # Tasa de impuesto como porcentaje, ej. 12.0 para 12%
    tax_rate: float = Field(default=12.0)
    currency_symbol: str = Field(default="$")
    low_stock_threshold: int = Field(default=10)

class User(SQLModel, table=True):
    """Usuario del sistema (Login y relaciones)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True) 
    hashed_password: str
    full_name: Optional[str] = None
    role: str = Field(default="Vendedor") # Admin, Vendedor, Bodeguero
    is_active: bool = Field(default=True)
    
    # Relaciones
    orders: List["Order"] = Relationship(back_populates="user")

class Product(SQLModel, table=True):
    """Productos del inventario."""
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True)
    name: str
    category: str = Field(index=True)
    price: float = Field(gt=0)
    stock: int = Field(default=0)
    image_url: Optional[str] = None 
    
    # Relaciones
    order_items: List["OrderItem"] = Relationship(back_populates="product")

class Order(SQLModel, table=True):
    """Cabecera de las órdenes de venta."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="Pagada") # Pagada, Cancelada
    
    # Datos financieros
    payment_method: str = Field(default="Efectivo") 
    subtotal: float 
    tax_amount: float 
    total_amount: float 
    
    # Relaciones
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    """Detalle de los productos dentro de una orden."""
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(gt=0)
    price_at_purchase: float # Precio histórico al momento de la venta
    
    # Relaciones
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    order: Optional[Order] = Relationship(back_populates="items")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    product: Optional[Product] = Relationship(back_populates="order_items")


# ==========================================
# 2. MODELOS DE UI / LÓGICA (FRONTEND)
# Estos NO crean tablas en la BD. Sirven para 
# manejar el carrito, gráficos y reportes.
# ==========================================

class CartItem(rx.Model):
    """Elemento temporal del carrito de compras (POS)."""
    product_id: int
    name: str
    price: float
    image_url: Optional[str] = None
    stock: int 
    qty: int = 0

    def calculate_total(self) -> float:
        return self.price * self.qty

class DashboardStats(rx.Model):
    """Datos agregados para mostrar en el Dashboard."""
    sales_this_week: float = 0.0
    sales_last_week: float = 0.0
    orders_this_week: int = 0
    orders_last_week: int = 0
    low_stock_items_count: int = 0
    # Reutilizamos el modelo Product de la base de datos
    top_products: List[Product] = [] 

class ReportItem(rx.Model):
    """Para gráficos simples (Nombre vs Cantidad)."""
    name: str
    units: float  # Puede ser dinero o cantidad

class SalesTimePoint(rx.Model):
    """Para el gráfico de líneas (Tiempo vs Ventas)."""
    period: str 
    total_sales: float

class OrderDetail(rx.Model):
    """Vista simplificada de una orden para tablas de reportes."""
    id: int
    created_at: str # Convertimos datetime a string para el frontend
    total_amount: float
    items_summary: str # Ej: "2x Café, 1x Pan"
    status: str
    user_name: str

class SalesReport(rx.Model):
    """Estructura completa del reporte de ventas."""
    start_date: str=""
    end_date: str=""
    total_revenue: float = 0.0
    total_orders: int = 0
    average_ticket: float = 0.0
    
    # Gráficos
    top_products: List[ReportItem] = []
    sales_by_category: List[ReportItem] = []
    sales_over_time: List[SalesTimePoint] = []
    
    # Tabla de detalles
    detailed_sales: List[OrderDetail] = []

class SettingsModel(rx.Model):
    """Modelo de configuración utilizado por el estado del POS."""
    business_name: str = "Mi Cafetería"
    tax_rate: float = 0.0
    currency_symbol: str = "$"
    low_stock_threshold: int = 10    