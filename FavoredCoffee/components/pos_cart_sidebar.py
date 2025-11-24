import reflex as rx
from ..models import CartItem 
from ..state.pos_state import POSState

def _render_cart_item(item: rx.Var[CartItem]) -> rx.Component:
    """Componente helper para un solo item en el carrito."""
    return rx.hstack(
        rx.avatar(src=item.image_url or "/placeholder.png", size="3"),
        rx.vstack(
            rx.text(item.name, size="2", weight="medium"),
            rx.text(f"{POSState.currency}{item.price:,.2f}", size="2", color_scheme="gray"),
            align="start",
            spacing="0",
        ),
        rx.spacer(),
        # Stepper de cantidad
        rx.hstack(
            rx.icon_button(
                "minus", 
                size="1", 
                on_click=POSState.remove_one_from_cart(item.product_id),
                variant="outline",
            ),
            rx.text(item.qty, size="3", weight="medium"),
            rx.icon_button(
                "plus", 
                size="1", 
                on_click=POSState.add_one_to_cart(item.product_id),
            ),
            spacing="2",
            align="center",
        ),
        # Botón de eliminar
        rx.icon_button(
            "trash-2",
            size="2",
            color_scheme="red",
            variant="ghost",
            on_click=POSState.delete_item_from_cart(item.product_id),
        ),
        align="center",
        width="100%",
    )

def cart_sidebar() -> rx.Component:
    """La sidebar del carrito con los totales."""
    return rx.vstack(
        rx.heading("Orden Actual", size="6"),
        rx.divider(),
        
        # --- Lista de Items ---
        rx.box(
            rx.cond(
                POSState.cart_items.length() > 0,
                rx.vstack(
                    rx.foreach(POSState.cart_items, _render_cart_item),
                    spacing="4",
                ),
                rx.text("El carrito está vacío.", color_scheme="gray", align="center")
            ),
            # Scroll
            height="calc(100vh - 450px)", # Ajustar altura
            overflow_y="auto",
            padding_x="0.5em",
        ),
        
        rx.spacer(),
        
        # --- Resumen de Totales ---
        rx.vstack(
            rx.divider(),
            rx.hstack(
                rx.text("Subtotal", size="3", color_scheme="gray"),
                rx.spacer(),
                rx.text(f"{POSState.currency}{POSState.cart_subtotal:,.2f}", size="3"),
                width="100%",
            ),
            rx.hstack(
                rx.text(f"IVA ({POSState.settings.tax_rate}%)", size="3", color_scheme="gray"),
                rx.spacer(),
                rx.text(f"{POSState.currency}{POSState.cart_tax_amount:,.2f}", size="3"),
                width="100%",
            ),
            rx.hstack(
                rx.text("Total a Pagar", size="5", weight="bold"),
                rx.spacer(),
                rx.text(f"{POSState.currency}{POSState.cart_total:,.2f}", size="5", weight="bold"),
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        
        # --- Botón de Liquidar ---
        rx.button(
            "Liquidar Venta",
            size="3",
            width="100%",
            on_click=POSState.open_payment_modal,
            is_loading=POSState.is_loading,
            # Botón con gradiente de tus colores
            style={
                "background": f"linear-gradient(to right, {rx.color('magenta', 6)}, {rx.color('coral', 6)})",
                "color": "white"
            }
        ),
        
        # Estilo de la sidebar
        width="380px",
        height="100vh",
        position="fixed",
        top="0",
        right="0",
        padding="1.5em",
        bg=rx.color("gray", 2),
        border_left=f"1px solid {rx.color('gray', 5)}",
        spacing="4",
    )