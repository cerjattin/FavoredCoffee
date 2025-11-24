import os
import reflex as rx

LOCAL_BACKEND_URL = os.environ.get("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="FavoredCoffee",
    api_url=LOCAL_BACKEND_URL,
)
