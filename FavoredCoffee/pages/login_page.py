import reflex as rx
from ..theme import COLOR_CORAL, COLOR_MAGENTA
from ..state.base import State

def login_content() -> rx.Component:
    """Contenido del formulario de login."""
    return rx.flex(
        rx.box(
            # Simulación del logo
            rx.heading("Cafetería App", size="8", margin_bottom="0.5em", color_scheme="plum"),
            rx.heading("¡Bienvenido!", size="6", margin_bottom="0.5em"),
            rx.text("Inicia sesión para gestionar tu negocio.", color_scheme="gray", margin_bottom="2em"),
            
            rx.form(
                rx.vstack(
                    rx.text("Correo Electrónico", size="2", weight="medium"),
                    rx.input(
                        placeholder="admin@cafe.com",
                        name="email",
                        type="email",
                        required=True,
                        size="3",
                        width="100%",
                    ),
                    rx.text("Contraseña", size="2", weight="medium"),
                    rx.input(
                        placeholder="admin123",
                        name="password",
                        type="password",
                        required=True,
                        size="3",
                        width="100%",
                    ),
                    
                    # Mostrar errores de login
                    rx.cond(
                        State.error_message,
                        rx.callout(
                            State.error_message,
                            icon="triangle_alert", # Icono corregido
                            color_scheme="red",
                            width="100%",
                        ),
                    ),
                    
                    rx.button(
                        "Ingresar",
                        type="submit",
                        is_loading=State.is_loading,
                        size="3",
                        width="100%",
                        # Botón con gradiente
                        style={
                            "background": f"linear-gradient(to right, {COLOR_MAGENTA}, {COLOR_CORAL})",
                            "color": "white"
                        }
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=State.login,
                width="100%"
            ),
            
            # Estilo del Card
            padding="2.5em",
            border_radius="1em", 
            background="white",
            box_shadow="0px 10px 30px -5px rgba(0, 0, 0, 0.1)",
            max_width="400px",
            width="100%",
        ),
        
        # Estilo de la Página (Fondo completo)
        align="center",
        justify="center",
        height="100vh",
        width="100%",
        background=f"linear-gradient(to bottom right, {rx.color('plum', 3)}, {rx.color('tomato', 3)})",
    )

@rx.page(
    route="/", # Ruta Raíz (Login es lo primero que se ve)
    title="Iniciar Sesión"
)
def login_page() -> rx.Component:
    return login_content()