import reflex as rx
from typing import List, Dict, Any
from .base import State
from ..models import SalesReport
from datetime import datetime, timedelta

class ReportsState(State):
    # Fechas por defecto
    start_date: str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date: str = datetime.now().strftime("%Y-%m-%d")
    
    # Datos del reporte (Objeto complejo)
    report: SalesReport = SalesReport()

    # --- Setters Explícitos ---
    def set_start_date(self, value: str):
        self.start_date = value

    def set_end_date(self, value: str):
        self.end_date = value

    # --- PUENTES PARA GRÁFICOS (La Solución al Error) ---
    # Convertimos los objetos Pydantic a diccionarios simples que Recharts entiende
    
    @rx.var
    def sales_chart_data(self) -> List[Dict[str, Any]]:
        """Devuelve las ventas como lista de diccionarios para el gráfico."""
        # model_dump() es la forma moderna de Pydantic v2 para convertir a dict
        # Si usas una versión vieja de Pydantic, usa .dict()
        return [item.dict() for item in self.report.sales_over_time]

    @rx.var
    def top_products_chart_data(self) -> List[Dict[str, Any]]:
        """Devuelve el top productos como lista de diccionarios."""
        return [item.dict() for item in self.report.top_products]

    # --- API ---
    async def get_report(self):
        await self.check_auth()
        url = f"/reports/sales?start_date={self.start_date}&end_date={self.end_date}"
        response = await self.super()._api_call("GET", url)
        
        if response and response.status_code == 200:
            self.report = SalesReport(**response.json())
        else:
            return rx.toast("Error al cargar reportes", status="error")