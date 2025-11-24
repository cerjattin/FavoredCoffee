import reflex as rx
import httpx
from typing import Optional, Dict, Any
# Asegúrate de que User esté en models.py
from ..models import User
from reflex.config import get_config

# ======================================================
# CONFIGURACIÓN DE LA URL DE LA API
# ======================================================
# Obtenemos la configuración actual de Reflex
config = get_config()

# Lógica inteligente para determinar a dónde llamar:
# 1. Si config.api_url existe (Prod), úsala.
# 2. Si no, asume localhost:8000 (Dev).
_base = config.api_url or "http://localhost:8000"

# ⚠️ IMPORTANTE: Agregamos "/api" porque ahí montamos tu backend
BASE_API_URL = f"{_base}/api"

class State(rx.State):
    """
    Estado base v3. Maneja autenticación y llamadas a la API unificada.
    """
    
    token: str = rx.LocalStorage("")
    current_user: User = User()
    
    is_loading: bool = False
    error_message: str = ""

    # --- Propiedades Computadas de Roles ---

    @rx.var
    def is_authenticated(self) -> bool:
        return self.token != ""

    @rx.var
    def is_admin(self) -> bool:
        return self.current_user.role == "Admin"

    @rx.var
    def is_vendedor(self) -> bool:
        """Un vendedor (o admin) puede vender."""
        return self.current_user.role in ["Admin", "Vendedor"]

    @rx.var
    def is_bodeguero(self) -> bool:
        """Un bodeguero (o admin) puede gestionar inventario."""
        return self.current_user.role in ["Admin", "Bodeguero"]

    # --- Lógica de Autenticación (Login / Logout) ---

    async def login(self, form_data: Dict[str, str]):
        """Maneja el login llamando a la API interna."""
        self.is_loading = True
        self.error_message = ""
        
        # FastAPI OAuth2 espera 'username', mapeamos el email ahí
        login_data = {
            "username": form_data["email"],
            "password": form_data["password"]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # 👇 La URL final será: http://localhost:8000/api/auth/login
                print(f"📡 Intentando login en: {BASE_API_URL}/auth/login")
                
                response = await client.post(
                    f"{BASE_API_URL}/auth/login",
                    data=login_data 
                )
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                # Obtenemos info del usuario inmediatamente
                await self.get_user_info_from_token()
                return rx.redirect("/") # Al Dashboard
            else:
                detail = response.json().get('detail', 'Error desconocido')
                self.error_message = f"Error ({response.status_code}): {detail}"
                
        except httpx.RequestError as e:
            self.error_message = f"No se pudo conectar con el servidor: {e}"
        finally:
            self.is_loading = False

    def logout(self):
        """Cierra la sesión localmente."""
        self.token = ""
        self.current_user = User() # Reinicia usuario vacío
        return rx.redirect("/")

    # --- Helpers de API y Token ---

    async def get_user_info_from_token(self):
        """
        Llama a /api/auth/me para obtener datos frescos.
        """
        if not self.token:
            return

        try:
            # Llamamos al helper interno
            response = await self._api_call("GET", "/auth/me")
            if response and response.status_code == 200:
                # Actualizamos el usuario en el estado
                self.current_user = User(**response.json())
            
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            self.logout()

    def _get_auth_headers(self) -> Dict[str, str]:
        if not self.token:
            # Si no hay token, no lanzamos excepción, retornamos dict vacío 
            # para que la API responda 401 naturalmente
            return {} 
        return {"Authorization": f"Bearer {self.token}"}

    async def _api_call(self, method: str, endpoint: str, **kwargs) -> Optional[httpx.Response]:
        """
        Helper unificado para llamadas API.
        endpoint debe empezar con barra, ej: "/products"
        """
        self.is_loading = True
        self.error_message = ""
        
        try:
            headers = self._get_auth_headers()
            # Si pasaron headers extra, los combinamos
            if "headers" in kwargs:
                headers.update(kwargs.pop("headers"))
            
            async with httpx.AsyncClient() as client:
                # Construimos la URL completa: BASE + endpoint
                full_url = f"{BASE_API_URL}{endpoint}"
                
                response = await client.request(
                    method, full_url, headers=headers, **kwargs
                )
            
            if response.status_code == 401:
                # Token vencido o inválido
                self.logout()
                return None

            response.raise_for_status() 
            return response
        
        except httpx.HTTPStatusError as e:
            # Errores que devuelve la API (400, 404, 500)
            try:
                detail = e.response.json().get('detail', e.response.text)
                self.error_message = f"Error API: {detail}"
            except:
                self.error_message = f"Error API: {e}"
        except httpx.RequestError as e:
            # Errores de red (servidor caído, timeout)
            self.error_message = f"Error de conexión: {e}"
        finally:
            self.is_loading = False
        
        return None

    # --- Helpers de Protección de Rutas ---
    
    async def check_auth(self):
        """Verifica si el usuario puede ver la página."""
        if not self.is_authenticated:
            return rx.redirect("/") # Al login
        
        # Si tenemos token pero no datos de usuario, los pedimos
        if not self.current_user.email:
            await self.get_user_info_from_token()

    async def check_admin_auth(self):
        """Solo admins."""
        await self.check_auth()
        # Pequeña espera para asegurar que current_user se cargó
        if not self.is_admin:
            return rx.redirect("/dashboard")