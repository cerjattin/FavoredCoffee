from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, date

# --- Schemas de Autenticación ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Schemas de Configuración ---
class SettingsSchema(BaseModel):
    business_name: str
    tax_rate: float
    currency_symbol: str
    low_stock_threshold: int
    class Config:
        from_attributes = True # Corrección V2

# --- Schemas de Usuario ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "Vendedor"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    class Config:
        from_attributes = True # Corrección V2

# --- Schemas de Producto ---
class ProductBase(BaseModel):
    sku: str
    name: str
    category: str
    price: float
    stock: int
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True # Corrección V2

# --- Schemas de Inventario (¡FALTABA ESTO!) ---
class InventoryUploadResponse(BaseModel):
    status: str
    summary: str

# --- Schemas de Órdenes ---
class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class OrderRequest(BaseModel):
    items: List[OrderItemRequest]
    payment_method: str = Field(default="Efectivo")

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float
    product_name: str
    
    class Config:
        from_attributes = True # Corrección V2

class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    status: str
    payment_method: str
    subtotal: float
    tax_amount: float
    total_amount: float
    user_id: int
    user_full_name: str
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True # Corrección V2
        
# --- Schemas de Dashboard ---
class DashboardStats(BaseModel):
    sales_this_week: float
    sales_last_week: float
    orders_this_week: int
    orders_last_week: int
    low_stock_items_count: int
    top_products: List[Product]

# --- Schemas de Reportes ---
class ReportItem(BaseModel):
    name: str
    units: int

class SalesReport(BaseModel):
    start_date: str # Enviamos strings ISO para simplificar
    end_date: str
    total_revenue: float
    total_orders: int
    average_ticket: float
    top_products: List[ReportItem]
    sales_by_category: List[ReportItem]
    sales_over_time: List[dict] # Lista de dicts simple
    detailed_sales: List[OrderResponse]