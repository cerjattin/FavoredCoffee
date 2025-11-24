import reflex as rx
from fastapi import FastAPI
from sqlmodel import SQLModel, Session
from .database import engine
from .logic.logic_users import create_first_admin
from .logic.logic_settings import create_initial_settings
from .routers import auth, inventory, users, settings, dashboard, reports, products, orders

style = {"font_family": "Instrument Sans", "background_color": "#F9FAFB"}
app = rx.App(style=style)

def init_db():
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        create_initial_settings(session)
        create_first_admin(session)

# Startup en la app raíz (sí se ejecuta)
app._api.add_event_handler("startup", init_db)

# Sub‑app con tus routers
custom_api = FastAPI()
custom_api.include_router(auth.router)
custom_api.include_router(inventory.router)
custom_api.include_router(users.router)
custom_api.include_router(settings.router)
custom_api.include_router(dashboard.router)
custom_api.include_router(reports.router)
custom_api.include_router(products.router)
custom_api.include_router(orders.router)

app._api.mount("/api", custom_api)
