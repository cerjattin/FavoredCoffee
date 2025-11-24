import reflex as rx
from ..state.inventory_state import InventoryState
from ..components.layout import app_layout

def inventory_item(product: rx.Var) -> rx.Component:
    return rx.table.row(
        rx.table.cell(product.sku),
        rx.table.cell(
            rx.hstack(
                rx.image(
                    # Fix anterior: rx.cond para la imagen
                    src=rx.cond(
                        product.image_url, 
                        product.image_url, 
                        "/placeholder.png"
                    ),
                    height="40px",
                    width="40px",
                    object_fit="cover",
                    border_radius="4px",
                ),
                rx.text(product.name),
                align="center",
                spacing="2"
            )
        ),
        rx.table.cell(product.category),
        rx.table.cell(f"${product.price:,.0f}"),
        rx.table.cell(
            rx.badge(
                f"{product.stock}", 
                color_scheme=rx.cond(product.stock < 10, "red", "green")
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button("pencil", size="1", variant="soft", on_click=lambda: InventoryState.edit_product(product)),
                rx.icon_button("trash-2", size="1", variant="soft", color_scheme="red", on_click=lambda: InventoryState.delete_product(product.id)),
                spacing="2"
            )
        ),
    )

def inventory_content() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Inventario", size="6"),
            rx.spacer(),
            rx.button(
                rx.hstack(rx.icon("plus"), rx.text("Nuevo Producto")),
                on_click=InventoryState.open_add_modal
            ),
            width="100%",
            align="center",
            margin_bottom="1em"
        ),
        
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("SKU"),
                        rx.table.column_header_cell("Producto"),
                        rx.table.column_header_cell("Categoría"),
                        rx.table.column_header_cell("Precio"),
                        rx.table.column_header_cell("Stock"),
                        rx.table.column_header_cell("Acciones"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        InventoryState.products,
                        inventory_item
                    )
                ),
                width="100%"
            ),
            width="100%"
        ),
        
        # --- Modal para Agregar/Editar ---
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(
                    rx.cond(InventoryState.is_editing, "Editar Producto", "Nuevo Producto")
                ),
                rx.vstack(
                    rx.input(placeholder="SKU", value=InventoryState.form_data["sku"], on_change=lambda v: InventoryState.set_form_field("sku", v)),
                    rx.input(placeholder="Nombre", value=InventoryState.form_data["name"], on_change=lambda v: InventoryState.set_form_field("name", v)),
                    rx.select(
                        ["Bebida", "Comida", "Postre", "Otro"], 
                        placeholder="Categoría", 
                        value=InventoryState.form_data["category"], 
                        on_change=lambda v: InventoryState.set_form_field("category", v)
                    ),
                    rx.input(placeholder="Precio", type="number", value=InventoryState.form_data["price"], on_change=lambda v: InventoryState.set_form_field("price", v)),
                    rx.input(placeholder="Stock Inicial", type="number", value=InventoryState.form_data["stock"], on_change=lambda v: InventoryState.set_form_field("stock", v)),
                    rx.input(placeholder="URL Imagen (Opcional)", value=InventoryState.form_data["image_url"], on_change=lambda v: InventoryState.set_form_field("image_url", v)),
                    spacing="3",
                ),
                
                # 👇 AQUÍ ESTÁ EL CAMBIO: Usamos rx.flex en lugar de rx.dialog.actions
                rx.flex(
                    rx.button("Cancelar", color_scheme="gray", variant="soft", on_click=InventoryState.close_modal),
                    rx.button("Guardar", on_click=InventoryState.save_product),
                    spacing="3",
                    justify="end", # Alineamos a la derecha
                    margin_top="1.5em",
                ),
            ),
            open=InventoryState.show_modal,
            on_open_change=InventoryState.toggle_modal,
        ),
        
        width="100%",
        spacing="4"
    )

@rx.page(route="/inventory", title="Inventario", on_load=InventoryState.load_products)
def inventory_page() -> rx.Component:
    return app_layout(inventory_content)