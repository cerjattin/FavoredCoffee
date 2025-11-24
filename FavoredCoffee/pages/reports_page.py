import reflex as rx
from ..state.reports_state import ReportsState
from ..components.layout import app_layout

def summary_card(title: str, value: str, icon: str, color: str) -> rx.Component:
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

def reports_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Reportes y Estadísticas", size="7"),
        
        # --- Filtros ---
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.text("Fecha Inicio", size="1", weight="bold"),
                    rx.input(type="date", value=ReportsState.start_date, on_change=ReportsState.set_start_date),
                    align="start", spacing="1"
                ),
                rx.vstack(
                    rx.text("Fecha Fin", size="1", weight="bold"),
                    rx.input(type="date", value=ReportsState.end_date, on_change=ReportsState.set_end_date),
                    align="start", spacing="1"
                ),
                rx.spacer(),
                rx.button("Generar Reporte", on_click=ReportsState.get_report, size="3", variant="solid"),
                align="end", width="100%", spacing="4"
            ),
            width="100%"
        ),

        # --- KPIs ---
        rx.grid(
            summary_card("Ingresos Totales", f"${ReportsState.report.total_revenue:,.2f}", "dollar-sign", "#6A3587"),
            summary_card("Total Órdenes", f"{ReportsState.report.total_orders}", "shopping-bag", "#D94A8A"),
            summary_card("Ticket Promedio", f"${ReportsState.report.average_ticket:,.2f}", "bar-chart-2", "#EB7A74"),
            columns="3", spacing="4", width="100%"
        ),

        # --- Gráficos ---
        rx.grid(
            # Gráfico 1: Ventas en el Tiempo
            rx.card(
                rx.heading("Ventas en el Tiempo", size="4", margin_bottom="1em"),
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="total_sales",
                        stroke="#6A3587",
                        fill="#6A3587",
                        fill_opacity=0.3
                    ),
                    rx.recharts.x_axis(data_key="period"),
                    rx.recharts.y_axis(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    rx.recharts.tooltip(),
                    # 👇 EL CAMBIO CLAVE: Usamos la variable computada
                    data=ReportsState.sales_chart_data, 
                    height=300,
                    width="100%"
                ),
                width="100%"
            ),
            
            # Gráfico 2: Top Productos
            rx.card(
                rx.heading("Top Productos", size="4", margin_bottom="1em"),
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="units",
                        stroke="#D94A8A",
                        fill="#D94A8A",
                    ),
                    rx.recharts.x_axis(data_key="name"),
                    rx.recharts.y_axis(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                    rx.recharts.tooltip(),
                    # 👇 EL CAMBIO CLAVE: Usamos la variable computada
                    data=ReportsState.top_products_chart_data,
                    height=300,
                    width="100%"
                ),
                width="100%"
            ),
            columns="2", spacing="4", width="100%"
        ),
        spacing="5", width="100%", align="start"
    )

@rx.page(route="/reports", title="Reportes", on_load=ReportsState.get_report)
def reports_page() -> rx.Component:
    return app_layout(reports_content)