import httpx
import reflex as rx
import os
from typing import List, Dict, Any

# 1. Obtener la config de forma segura
# Usamos rx.get_config() para asegurar que la config esté cargada
config = rx.get_config()
BASE_URL = config.api_url or "http://localhost:3000"

# 2. Definir la URL BASE DE LA API (Agregando /api)
# Como montamos FastAPI en "/api", debemos incluirlo aquí.
API_BASE_URL = f"{BASE_URL}/api"

API_KEY = os.getenv("API_KEY", "unaclavesecretapordefecto")
HEADERS = {"X-API-Key": API_KEY}

class ApiService:
    """Centraliza todas las llamadas HTTP a nuestro backend."""
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Helper para manejar llamadas, timeouts y errores."""
        async with httpx.AsyncClient() as client:
            # Construimos la URL final: http://localhost:3000/api/products
            url = f"{API_BASE_URL}{endpoint}"
            
            try:
                print(f"📡 Llamando a: {method} {url}") # Log para depuración
                response = await client.request(
                    method, url, headers=HEADERS, timeout=10.0, **kwargs
                )
                response.raise_for_status() 
                return response
                
            except httpx.HTTPStatusError as e:
                print(f"❌ Error API ({e.response.status_code}): {e.response.text}")
                return e.response 
            except httpx.RequestError as e:
                print(f"❌ Error Conexión: {e}")
                # En Reflex, es mejor retornar None o una respuesta vacía controlada
                # en lugar de romper la app con una excepción, pero depende de tu gusto.
                raise Exception(f"Error de conexión con el Backend: {e}")

    # --- ENDPOINTS ---
    # Asegúrate de que estos coincidan con los @router.get("/") definidos en tus routers
    
    async def get_products(self) -> httpx.Response:
        # Esto llamará a: /api/products
        return await self._make_request("GET", "/products")

    async def create_order(self, items: List[Dict[str, Any]]) -> httpx.Response:
        return await self._make_request("POST", "/orders", json={"items": items}) 
        # NOTA: Cambié "/create_order" a "/orders" asumiendo REST estándar, 
        # revisa cómo se llama en routers/orders.py
    
    async def get_daily_summary(self) -> httpx.Response:
        return await self._make_request("GET", "/dashboard/summary")
        # NOTA: Revisa si tu router de dashboard tiene prefijo.
    
    async def upload_inventory(self, file_data: bytes, filename: str) -> httpx.Response:
        # Para subir archivos con httpx se usa 'files'
        files = {'file': (filename, file_data)}
        return await self._make_request("POST", "/inventory/upload", files=files)

# Instancia global
api = ApiService()