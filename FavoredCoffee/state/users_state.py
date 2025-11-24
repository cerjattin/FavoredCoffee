import reflex as rx
from typing import List, Dict
from .base import State
from ..models import User

class UsersState(State):
    users: List[User] = []
    show_modal: bool = False
    is_editing: bool = False
    current_user_id: int = 0
    
    # Formulario
    form_data: Dict[str, str] = {
        "email": "",
        "full_name": "",
        "role": ""
    }
    is_active_check: bool = True

    async def load_users(self):
        await self.check_auth()
        # Solo admin puede ver esto
        if not self.is_admin:
            return rx.redirect("/")
            
        response = await self.super()._api_call("GET", "/users")
        if response and response.status_code == 200:
            self.users = [User(**u) for u in response.json()]

    def set_form_field(self, field: str, value: str):
        self.form_data[field] = value

    def set_is_active_check(self, value: bool):
        self.is_active_check = value

    def open_add_modal(self):
        self.is_editing = False
        self.form_data = {"email": "", "full_name": "", "role": ""}
        self.is_active_check = True
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False
        
    def toggle_modal(self, is_open: bool):
        self.show_modal = is_open

    def edit_user(self, user: User):
        self.is_editing = True
        self.current_user_id = user.id
        self.form_data = {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
        self.is_active_check = user.is_active
        self.show_modal = True

    async def delete_user(self, user_id: int):
        response = await self.super()._api_call("DELETE", f"/users/{user_id}")
        if response and response.status_code == 200:
            await self.load_users()
            return rx.toast("Usuario eliminado", status="success")
        else:
            return rx.toast("Error al eliminar", status="error")

    async def save_user(self):
        user_data = {
            "email": self.form_data["email"],
            "full_name": self.form_data["full_name"],
            "role": self.form_data["role"],
            "is_active": self.is_active_check
        }
        
        if self.is_editing:
            response = await self.super()._api_call("PUT", f"/users/{self.current_user_id}", json=user_data)
        else:
            # Crear usuario (password por defecto 123456)
            user_data["password"] = "123456" 
            response = await self.super()._api_call("POST", "/users/create", json=user_data)

        if response and (response.status_code == 200 or response.status_code == 201):
            self.show_modal = False
            await self.load_users()
            return rx.toast("Usuario guardado", status="success")
        else:
            return rx.toast("Error al guardar", status="error")