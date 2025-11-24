import reflex as rx
from typing import List, Dict, Any
from .base import State
from ..models import Product, CartItem, SettingsModel

class POSState(State):
    
    # --- Datos del Backend ---
    products: List[Product] = []
    settings: SettingsModel = SettingsModel()
    
    # --- Estado del Carrito ---
    cart: Dict[int, CartItem] = {}
    
    # --- Estado de la UI ---
    search_term: str = ""
    selected_category: str = "Todas"
    show_payment_modal: bool = False
    selected_payment_method: str = "Efectivo"
    
    # --- Setters ---
    def set_search_term(self, value):
        self.search_term = value

    def set_selected_category(self, value):
        self.selected_category = value

    # --- Propiedades Computadas ---
    @rx.var
    def filtered_products(self) -> List[Product]:
        products = self.products
        if self.selected_category != "Todas" and self.selected_category != "all":
            products = [p for p in products if p.category == self.selected_category]
        
        if self.search_term:
            term = self.search_term.lower()
            products = [p for p in products if term in p.name.lower() or term in p.sku.lower()]
        return products

    @rx.var
    def cart_items(self) -> List[CartItem]:
        return sorted(self.cart.values(), key=lambda item: item.name)

    @rx.var
    def cart_subtotal(self) -> float:
        return sum(item.price * item.qty for item in self.cart.values())

    @rx.var
    def cart_total(self) -> float:
        return self.cart_subtotal 
    
    # --- API ---
    async def load_products(self):
        products_response = await self.super()._api_call("GET", "/products")
        if products_response and products_response.status_code == 200:
            self.products = [Product(**p) for p in products_response.json()]
    
    async def load_pos_data(self):
        await self.check_auth()
        if not self.is_vendedor:
            return rx.redirect("/")
        
        settings_response = await self.super()._api_call("GET", "/settings")
        if settings_response and settings_response.status_code == 200:
            self.settings = SettingsModel(**settings_response.json())
        
        await self.load_products()

    async def process_payment(self):
        if not self.cart:
            return rx.toast("El carrito está vacío", status="warning")
            
        order_data = {
            "items": [{"product_id": item.product_id, "quantity": item.qty} for item in self.cart.values()],
            "payment_method": self.selected_payment_method
        }
        
        response = await self.super()._api_call("POST", "/orders/create", json=order_data)
        
        if response and response.status_code == 200:
            order_id = response.json().get("id")
            self.cart = {}
            self.show_payment_modal = False
            self.selected_payment_method = "Efectivo"
            await self.load_products() 
            return rx.toast(f"¡Orden #{order_id} creada con éxito!", status="success")
        else:
            return rx.toast("Error al procesar la orden", status="error")

    # --- Lógica Carrito ---
    def add_to_cart(self, product: Product):
        if product.stock <= 0:
             return rx.toast("Producto sin stock", status="error")
        
        if product.id in self.cart:
            item_in_cart = self.cart[product.id]
            return self.increase_qty(item_in_cart)
        else:
            self.cart[product.id] = CartItem(
                product_id=product.id,
                name=product.name,
                price=product.price,
                image_url=product.image_url,
                stock=product.stock,
                qty=1
            )

    def increase_qty(self, item: CartItem):
        if item.product_id in self.cart:
            current_item = self.cart[item.product_id]
            if current_item.qty < current_item.stock:
                current_item.qty += 1
                self.cart[item.product_id] = current_item
            else:
                return rx.toast(f"Stock máximo ({current_item.stock}) alcanzado", status="warning")

    def decrease_qty(self, item: CartItem):
        if item.product_id in self.cart:
            current_item = self.cart[item.product_id]
            current_item.qty -= 1
            if current_item.qty <= 0:
                del self.cart[item.product_id]
            else:
                self.cart[item.product_id] = current_item