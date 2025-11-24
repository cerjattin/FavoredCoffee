import reflex as rx
from ..state.dashboard_state import DashboardState
from ..components.layout import app_layout

# --- Componentes visuales ---
def stat_card(title: str, value: str, icon: str, color: str) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=24, color="white"),
                padding="10px",
                border_radius="10px",
                background=color,
            ),
            rx.vstack(
                rx.text(title, size="1", color_scheme="gray", weight="medium"),
                rx.heading(value, size="6"),
                spacing="1",
                align="start"
            ),
            align="center",
            spacing="4"
        ),
        size="2"
    )

def dashboard_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Resumen General", size="7", margin_bottom="0.5em"),
        
        # Grid de KPIs
        rx.grid(
            stat_card("Ventas Hoy", f"${DashboardState.stats.sales_this_week:,.2f}", "dollar-sign", "#6A3587"),
            stat_card("Órdenes Hoy", f"{DashboardState.stats.orders_this_week}", "shopping-bag", "#D94A8A"),
            stat_card("Alertas Stock", f"{DashboardState.stats.low_stock_items_count}", "triangle_alert", "#EB7A74"),
            columns="3",
            spacing="4",
            width="100%"
        ),
        
        # Tabla simple de Top Productos (Más segura que los gráficos por ahora)
        rx.heading("Productos Más Vendidos", size="5", margin_top="1em"),
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Producto"),
                        rx.table.column_header_cell("Categoría"),
                        rx.table.column_header_cell("Precio"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        DashboardState.stats.top_products,
                        lambda p: rx.table.row(
                            rx.table.cell(p.name),
                            rx.table.cell(p.category),
                            rx.table.cell(f"${p.price:,.2f}"),
                        )
                    )
                ),
                width="100%"
            )
        ),
        spacing="5",
        width="100%",
        align="start"
    )


@rx.page(route="/dashboard", title="Dashboard", on_load=DashboardState.load_dashboard)
def dashboard_page() -> rx.Component:
    return app_layout(dashboard_content)