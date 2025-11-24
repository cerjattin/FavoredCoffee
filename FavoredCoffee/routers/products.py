from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..security import get_current_warehouse_user, get_current_admin_user
from ..models import Product
from ..schemas import Product as ProductSchema, ProductCreate

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    # Protegido para Bodegueros y Admins
    dependencies=[Depends(get_current_warehouse_user)] 
)

@router.post("/", response_model=ProductSchema, status_code=201, dependencies=[Depends(get_current_admin_user)])
def create_product(product_data: ProductCreate, db: Session = Depends(get_session)):
    # Solo Admins pueden crear
    db_product = db.exec(select(Product).where(Product.sku == product_data.sku)).first()
    if db_product:
        raise HTTPException(status_code=400, detail="SKU ya registrado")
    
    new_product = Product.from_orm(product_data)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/", response_model=List[ProductSchema])
def read_products(db: Session = Depends(get_session)):
    # Bodegueros y Admins pueden leer
    return db.exec(select(Product)).all()

# ... (Aquí irían los endpoints PUT /{id} y DELETE /{id} para Admins) ...