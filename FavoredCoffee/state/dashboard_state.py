import reflex as rx
import datetime
from .base import State
from ..models import DashboardStats

class DashboardState(State):
    """Estado para la página del Dashboard (Panel de Control)."""    
    stats: DashboardStats = DashboardStats()

    # --- Propiedades Computadas para la UI ---

    @rx.var
    def welcome_message(self) -> str:
        """Crea el saludo con la fecha actual."""
        # NOTA: Usamos .js_to_string() para formatear en cliente
        # Esto evita problemas de hidratación
        return f"¡Bienvenido, {self.current_user.full_name}! Hoy es {rx.call_script('new Date().toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" })')}"

    @rx.var
    def sales_percentage_change(self) -> float:
        """Calcula el % de cambio en ventas (Regla 1)."""
        if self.stats.sales_last_week == 0:
            return 100.0 if self.stats.sales_this_week > 0 else 0.0
        
        return ((self.stats.sales_this_week - self.stats.sales_last_week) 
                / self.stats.sales_last_week) * 100

    @rx.var
    def orders_percentage_change(self) -> float:
        """Calcula el % de cambio en órdenes (Regla 1)."""
        if self.stats.orders_last_week == 0:
            return 100.0 if self.stats.orders_this_week > 0 else 0.0
            
        return ((self.stats.orders_this_week - self.stats.orders_last_week) 
                / self.stats.orders_last_week) * 100

    @rx.var
    def top_products_str(self) -> str:
        """Formatea la lista de top productos (Regla 2)."""
        if not self.stats.top_products:
            return "N/A"
        return ", ".join([p.name for p in self.stats.top_products])

    # --- Manejador de Eventos (API) ---
    
    async def load_dashboard(self):
        """
        Se ejecuta al cargar la página (on_mount).
        Primero valida el login, luego carga las estadísticas.
        """
        # Validar que sea Admin (el backend lo protege, pero es buena práctica)
        await self.check_admin_auth()
        if not self.is_admin:
             return
        
        response = await self.super()._api_call("GET", "/dashboard/stats")
        if response and response.status_code == 200:
            self.stats = DashboardStats(**response.json())
        else:
            # El error ya se maneja en _api_call
            pass