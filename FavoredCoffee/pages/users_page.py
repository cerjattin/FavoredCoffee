import reflex as rx
from ..state.users_state import UsersState
from ..components.layout import app_layout

def user_row(user: rx.Var) -> rx.Component:
    return rx.table.row(
        rx.table.cell(user.full_name),
        rx.table.cell(user.email),
        rx.table.cell(user.role),
        rx.table.cell(
            rx.badge(
                # 👇 CORRECCIÓN 1: rx.cond para el texto
                rx.cond(user.is_active, "Activo", "Inactivo"),
                # 👇 CORRECCIÓN 2: rx.cond para el color
                color_scheme=rx.cond(user.is_active, "green", "gray")
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    "pencil", 
                    size="1", 
                    variant="soft", 
                    on_click=lambda: UsersState.edit_user(user)
                ),
                rx.icon_button(
                    "trash-2", 
                    size="1", 
                    variant="soft", 
                    color_scheme="red", 
                    on_click=lambda: UsersState.delete_user(user.id)
                ),
                spacing="2"
            )
        ),
    )

def users_content() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Gestión de Usuarios", size="6"),
            rx.spacer(),
            rx.button(
                rx.hstack(rx.icon("plus"), rx.text("Nuevo Usuario")),
                on_click=UsersState.open_add_modal
            ),
            width="100%",
            align="center",
            margin_bottom="1em"
        ),
        
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Nombre"),
                        rx.table.column_header_cell("Email"),
                        rx.table.column_header_cell("Rol"),
                        rx.table.column_header_cell("Estado"),
                        rx.table.column_header_cell("Acciones"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        UsersState.users,
                        user_row
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
                    # 👇 CORRECCIÓN 3: rx.cond para el título del modal
                    rx.cond(UsersState.is_editing, "Editar Usuario", "Nuevo Usuario")
                ),
                rx.vstack(
                    rx.input(
                        placeholder="Email", 
                        value=UsersState.form_data["email"], 
                        on_change=lambda v: UsersState.set_form_field("email", v)
                    ),
                    rx.input(
                        placeholder="Nombre Completo", 
                        value=UsersState.form_data["full_name"], 
                        on_change=lambda v: UsersState.set_form_field("full_name", v)
                    ),
                    rx.select(
                        ["Admin", "Vendedor", "Bodeguero"], 
                        placeholder="Seleccionar Rol", 
                        value=UsersState.form_data["role"], 
                        on_change=lambda v: UsersState.set_form_field("role", v)
                    ),
                    
                    # Checkbox de Activo (Solo visible si editamos, opcional)
                    rx.hstack(
                        rx.checkbox(
                            checked=UsersState.is_active_check,
                            on_change=UsersState.set_is_active_check
                        ),
                        rx.text("Usuario Activo"),
                        align="center"
                    ),
                    
                    spacing="3",
                ),
                
                # 👇 CORRECCIÓN 4: Reemplazo de rx.dialog.actions por rx.flex
                rx.flex(
                    rx.button("Cancelar", color_scheme="gray", variant="soft", on_click=UsersState.close_modal),
                    rx.button("Guardar", on_click=UsersState.save_user),
                    spacing="3",
                    justify="end",
                    margin_top="1.5em",
                ),
            ),
            open=InventoryState.show_modal if False else UsersState.show_modal, # Aseguramos usar el state correcto
            on_open_change=UsersState.toggle_modal,
        ),
        
        width="100%",
        spacing="4"
    )

@rx.page(route="/users", title="Usuarios", on_load=UsersState.load_users)
def users_page() -> rx.Component:
    return app_layout(users_content)