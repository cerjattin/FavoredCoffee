import reflex as rx
from ..state.pos_state import POSState
from ..components.layout import app_layout

# Usamos rx.Var o Any para el tipo, ya que en tiempo de ejecución es un objeto reactivo
def product_card(product: rx.Var) -> rx.Component:
    """Tarjeta individual de producto."""
    return rx.card(
        rx.vstack(
            rx.image(
                # ✅ CORRECCIÓN 1: Usamos rx.cond (Lógica de Reflex)
                src=rx.cond(
                    product.image_url, 
                    product.image_url, 
                    "/placeholder.png"
                ),
                height="120px",
                width="100%",
                object_fit="cover",
                border_radius="8px 8px 0 0",
            ),
            rx.vstack(
                # ✅ CORRECCIÓN 4: Usamos sintaxis de punto (product.name)
                rx.text(product.name, weight="bold", size="2"),
                rx.hstack(
                    rx.badge(f"${product.price:,.0f}", color_scheme="green"),
                    rx.spacer(),
                    rx.text(f"Stock: {product.stock}", size="1", color_scheme="gray"),
                    width="100%"
                ),
                align="start",
                padding="2",
                width="100%"
            ),
            spacing="0",
            width="100%"
        ),
        on_click=lambda: POSState.add_to_cart(product),
        cursor="pointer",
        _hover={"transform": "scale(1.02)", "transition": "0.2s"},
    )

def cart_item(item: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(item.name, weight="medium", size="2"),
            rx.text(f"${item.price:,.0f}", size="1", color="gray"),
            align="start",
            width="100%"
        ),
        rx.hstack(
            rx.icon_button("minus", size="1", variant="soft", on_click=lambda: POSState.decrease_qty(item)),
            rx.text(f"{item.qty}", weight="bold"),
            rx.icon_button("plus", size="1", variant="soft", on_click=lambda: POSState.increase_qty(item)),
            spacing="2",
            align="center"
        ),
        width="100%",
        justify="between",
        padding_y="2",
        border_bottom="1px solid #eee"
    )

def pos_content() -> rx.Component:
    return rx.grid(
        # --- COLUMNA IZQUIERDA: Productos ---
        rx.vstack(
            rx.heading("Menú", size="6"),
            
            # Selector de Categorías
            rx.segmented_control.root(
                rx.segmented_control.item("Todas", value="Todas"), 
                rx.segmented_control.item("Bebida", value="Bebida"),
                rx.segmented_control.item("Comida", value="Comida"),
                value=POSState.selected_category,
                on_change=POSState.set_selected_category,
                width="100%",
            ),
            
            # Buscador
            rx.input(
                placeholder="Buscar producto...",
                value=POSState.search_term,
                on_change=POSState.set_search_term,
                width="100%"
            ),
            
            # Grid de productos con Scroll
            rx.scroll_area(
                rx.grid(
                    rx.foreach(
                        POSState.filtered_products,
                        product_card
                    ),
                    columns="3",
                    spacing="4",
                    width="100%"
                ),
                height="60vh",
                width="100%"
            ),
            spacing="4",
            width="100%",
            height="100%"
        ),
        
        # --- COLUMNA DERECHA: Carrito ---
        rx.card(
            rx.vstack(
                rx.heading("Orden Actual", size="4"),
                rx.scroll_area(
                    rx.vstack(
                        # ✅ CORRECCIÓN 2: Usamos cart_items (Lista) en lugar de cart (Diccionario)
                        rx.foreach(POSState.cart_items, cart_item),
                        width="100%",
                        spacing="2"
                    ),
                    height="45vh",
                    width="100%"
                ),
                rx.divider(),
                rx.hstack(
                    rx.text("Total", weight="bold", size="4"),
                    rx.spacer(),
                    # ✅ CORRECCIÓN 3: Nombre correcto de la variable (cart_total)
                    rx.heading(f"${POSState.cart_total:,.0f}", size="6", color_scheme="green"),
                    width="100%",
                    align="center"
                ),
                rx.button(
                    "Completar Pago", 
                    width="100%", 
                    size="3", 
                    color_scheme="green",
                    on_click=POSState.process_payment
                ),
                spacing="4",
                height="100%",
                justify="between"
            ),
            height="80vh",
            width="100%"
        ),
        columns="2",
        spacing="6",
        width="100%"
    )

@rx.page(route="/pos", title="Punto de Venta", on_load=POSState.load_pos_data)
def pos_page() -> rx.Component:
    return app_layout(pos_content)