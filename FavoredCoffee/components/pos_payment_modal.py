import reflex as rx
from ..state.pos_state import POSState
from ..theme import COLOR_PURPLE

def payment_modal() -> rx.Component:
    """Modal para confirmar el pago y seleccionar método."""
    return rx.modal(
        rx.modal_body(
            rx.vstack(
                rx.heading("Confirmar Pago", size="6", text_align="center"),
                rx.text("Total a Pagar", size="3", color_scheme="gray", text_align="center"),
                rx.heading(
                    f"{POSState.currency}{POSState.cart_total:,.2f}",
                    size="9",
                    text_align="center",
                    color_scheme="purple",
                ),
                
                rx.text("Seleccione método de pago", size="3", text_align="center"),
                
                # --- Botones de Método de Pago ---
                rx.segmented_control(
                    rx.segmented_control_item("Efectivo", value="Efectivo"),
                    rx.segmented_control_item("Tarjeta", value="Tarjeta"),
                    rx.segmented_control_item("Otros", value="Otros"),
                    value=POSState.selected_payment_method,
                    on_change=POSState.set_selected_payment_method,
                    size="2",
                    width="100%"
                ),

                # --- Botones de Acción ---
                rx.grid(
                    rx.button(
                        "Cancelar",
                        size="3",
                        variant="soft",
                        color_scheme="gray",
                        on_click=POSState.close_payment_modal,
                    ),
                    rx.button(
                        "Confirmar Pago",
                        size="3",
                        on_click=POSState.create_order,
                        is_loading=POSState.is_loading,
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                spacing="5",
                width="100%",
                align="center",
            )
        ),
        is_open=POSState.show_payment_modal,
        on_open_change=POSState.set_show_payment_modal,
    )