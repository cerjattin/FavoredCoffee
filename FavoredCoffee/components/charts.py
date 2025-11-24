import reflex as rx

def sales_evolution_chart(data: list) -> rx.Component:
    """Gráfico de Área para Evolución de Ventas."""
    return rx.recharts.area_chart(
        rx.recharts.area(
            data_key="Ventas",
            stroke="#D94A8A",
            fill="url(#colorVentas)",
        ),
        rx.recharts.x_axis(data_key="name", hide=True), # Ocultamos eje X para limpieza visual
        rx.recharts.y_axis(hide=True),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
        rx.recharts.tooltip(),
        rx.recharts.defs(
            rx.recharts.linear_gradient(
                rx.recharts.stop(offset="5%", stop_color="#D94A8A", stop_opacity=0.8),
                rx.recharts.stop(offset="95%", stop_color="#D94A8A", stop_opacity=0),
                id="colorVentas",
                x1=0, y1=0, x2=0, y2=1,
            )
        ),
        data=data,
        height=250,
        width="100%",
    )

def category_pie_chart(data: list) -> rx.Component:
    """Gráfico Circular para Categorías."""
    return rx.recharts.pie_chart(
        rx.recharts.pie(
            data=data,
            data_key="value",
            name_key="name",
            cx="50%",
            cy="50%",
            inner_radius=40,
            outer_radius=80,
            padding_angle=5,
            label=True,
        ),
        rx.recharts.tooltip(),
        height=250,
        width="100%",
    )

def top_products_bar_chart(data: list) -> rx.Component:
    """Gráfico de Barras Horizontales para Top Productos."""
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="Ventas",
            fill="#6A3587",
            radius=[0, 4, 4, 0],
            bar_size=20,
        ),
        rx.recharts.x_axis(type_="number", hide=True),
        rx.recharts.y_axis(data_key="name", type_="category", width=100, style={"font-size": "12px"}),
        rx.recharts.tooltip(),
        layout="vertical",
        data=data,
        height=250,
        width="100%",
    )