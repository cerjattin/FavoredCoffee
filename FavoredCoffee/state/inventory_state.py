import reflex as rx
from typing import List, Dict, Any
from .base import State
from ..models import Product

class InventoryState(State):
    # --- Estado de Datos ---
    products: List[Product] = []
    
    # --- Estado del Modal (Edición/Creación) ---
    show_modal: bool = False
    is_editing: bool = False
    current_product_id: int = 0
    
    # Formulario: Usamos un diccionario para mapear los campos del input
    form_data: Dict[str, str] = {
        "sku": "",
        "name": "",
        "category": "",
        "price": "",
        "stock": "",
        "image_url": ""
    }

    # --- Carga de Datos ---
    async def load_products(self):
        """Carga la lista de productos desde el backend."""
        await self.check_auth()
        response = await self.super()._api_call("GET", "/products")
        if response and response.status_code == 200:
            # Convertimos el JSON a objetos Product
            self.products = [Product(**p) for p in response.json()]

    # --- Manejo del Modal ---
    
    def open_add_modal(self):
        """Abre el modal para CREAR un nuevo producto (limpia el formulario)."""
        self.is_editing = False
        self.form_data = {
            "sku": "", "name": "", "category": "", 
            "price": "", "stock": "", "image_url": ""
        }
        self.show_modal = True

    def close_modal(self):
        """Cierra el modal."""
        self.show_modal = False

    def toggle_modal(self, is_open: bool):
        """Controlador para el evento on_open_change del Dialog."""
        self.show_modal = is_open

    # --- Lógica del Formulario ---

    def set_form_field(self, field: str, value: str):
        """Actualiza un campo específico del formulario."""
        self.form_data[field] = value

    # --- ACCIONES QUE FALTABAN (Corrección del error) ---

    def edit_product(self, product: Product):
        """
        Prepara el formulario con los datos del producto a editar.
        Esta es la función que el compilador decía que faltaba.
        """
        self.is_editing = True
        self.current_product_id = product.id
        # Llenamos el formulario con los datos actuales
        self.form_data = {
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "price": str(product.price),
            "stock": str(product.stock),
            "image_url": product.image_url or ""
        }
        self.show_modal = True

    async def delete_product(self, product_id: int):
        """Elimina un producto."""
        response = await self.super()._api_call("DELETE", f"/products/{product_id}")
        if response and response.status_code == 200:
            await self.load_products()
            return rx.toast("Producto eliminado", status="success")
        else:
            return rx.toast("Error al eliminar producto", status="error")

    async def save_product(self):
        """Decide si Crear o Actualizar según is_editing."""
        # Validación básica
        if not self.form_data["name"] or not self.form_data["price"]:
            return rx.toast("Nombre y Precio son obligatorios", status="warning")

        try:
            # Preparamos el payload (convertimos strings a números)
            product_data = {
                "sku": self.form_data["sku"],
                "name": self.form_data["name"],
                "category": self.form_data["category"],
                "price": float(self.form_data["price"]),
                "stock": int(self.form_data["stock"] or 0),
                "image_url": self.form_data["image_url"]
            }
        except ValueError:
            return rx.toast("Precio y Stock deben ser números válidos", status="error")

        if self.is_editing:
            # ACTUALIZAR (PUT)
            response = await self.super()._api_call(
                "PUT", 
                f"/products/{self.current_product_id}", 
                json=product_data
            )
        else:
            # CREAR (POST)
            response = await self.super()._api_call(
                "POST", 
                "/products/create", 
                json=product_data
            )

        if response and (response.status_code == 200 or response.status_code == 201):
            self.show_modal = False
            await self.load_products()
            action = "actualizado" if self.is_editing else "creado"
            return rx.toast(f"Producto {action} con éxito", status="success")
        else:
            return rx.toast("Error al guardar el producto", status="error")