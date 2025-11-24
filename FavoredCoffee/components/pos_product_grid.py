import reflex as rx
from ..state.pos_state import POSState

def product_grid() -> rx.Component:
    """La grilla de productos con filtros y búsqueda."""
    return rx.vstack(
        # --- Barra de Búsqueda y Filtros ---
        rx.hstack(
            rx.input(
                placeholder="Buscar producto por nombre o SKU...",
                value=POSState.search_term,
                on_change=POSState.set_search_term,
                size="3",
                width="40%",
            ),
            rx.spacer(),
            # Filtros de Categoría
            rx.segmented_control(
                rx.foreach(
                    POSState.categories,
                    lambda cat: rx.segmented_control_item(cat, value=cat),
                ),
                value=POSState.selected_category,
                on_change=POSState.select_category,
                size="2",
            ),
            width="100%",
            padding_bottom="1em"
        ),
        
        # --- Grid de Productos ---
        rx.box(
            rx.grid(
                rx.foreach(
                    POSState.filtered_products,
                    lambda product: rx.card(
                        rx.vstack(
                            rx.image(
                                src=product.image_url or "/placeholder.png",
                                width="100%",
                                height="120px",
                                object_fit="cover",
                                border_radius="var(--radius-3)",
                            ),
                            rx.text(product.name, weight="bold", size="3"),
                            rx.text(
                                f"{POSState.currency}{product.price:,.2f}", 
                                size="2", 
                                color_scheme="gray"
                            ),
                            align="start",
                            spacing="2",
                        ),
                        on_click=POSState.add_to_cart(product),
                        is_disabled=(product.stock <= 0),
                        cursor="pointer",
                        _hover={"shadow": "var(--shadow-4)"},
                    ),
                ),
                columns="5", # 5 columnas
                spacing="4",
                width="100%",
            ),
            # Scroll vertical
            height="calc(100vh - 200px)", # Ajustar altura
            overflow_y="auto",
            padding="0.5em"
        ),
        
        align="start",
        width="100%",
        spacing="4",
    )