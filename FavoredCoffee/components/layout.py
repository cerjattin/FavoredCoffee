import reflex as rx
from ..state.base import State

def sidebar_item(text: str, icon: str, url: str) -> rx.Component:
    """Componente auxiliar para los items del menú."""
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3", weight="medium"),
            spacing="3",
            align="center",
            padding="12px",
            border_radius="8px",
            width="100%",
            # Estilos de hover simples y robustos
            _hover={"background": "rgba(0,0,0, 0.05)"},
            color="inherit"
        ),
        href=url,
        underline="none",
        width="100%"
    )

def app_layout(content_component: rx.Component) -> rx.Component:
    """
    Layout principal con menú lateral fijo y área de contenido dinámica.
    Recibe el contenido de la página como argumento.
    """
    return rx.flex(
        # --- SIDEBAR (Menú Lateral) ---
        rx.box(
            rx.vstack(
                rx.heading("Cafetería App", size="5", margin_bottom="2em", color_scheme="plum"),
                
                # Navegación
                rx.vstack(
                    sidebar_item("Dashboard", "layout-dashboard", "/dashboard"),
                    sidebar_item("Punto de Venta", "shopping-cart", "/pos"),
                    sidebar_item("Inventario", "package", "/inventory"),
                    sidebar_item("Reportes", "bar-chart-3", "/reports"),
                    sidebar_item("Equipo", "users", "/users"),
                    spacing="2",
                    width="100%"
                ),
                
                rx.spacer(),
                
                # Botón de Salir
                rx.button(
                    rx.hstack(rx.icon("log-out"), rx.text("Cerrar Sesión")),
                    variant="soft",
                    color_scheme="red",
                    width="100%",
                    on_click=State.logout
                ),
                height="100%",
                padding="2em",
                align="start"
            ),
            # Estilos del contenedor del sidebar
            width=["0px", "0px", "280px"], # Oculto en móviles, 280px en escritorio
            height="100vh",
            position="sticky",
            top="0",
            border_right="1px solid #eaeaea",
            background="white",
            display=["none", "none", "block"], # Control responsivo
            z_index="10"
        ),
        
        # --- MAIN CONTENT (Contenido Principal) ---
        rx.box(
            content_component(), # Ejecutamos la función de contenido
            padding="2em",
            width="100%",
            min_height="100vh",
            background="#F7F9FB", # Fondo gris muy claro para el cuerpo
            flex="1"
        ),
        width="100%"
    )