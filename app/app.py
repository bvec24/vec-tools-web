import reflex as rx
from app.pages.index import index
from app.pages.login import login_page
from app.state import AppState
from app.themes import light_theme, dark_theme

app = rx.App(
    theme=rx.theme(light_theme, dark_theme, appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)
app.add_page(login_page, route="/login")