import reflex as rx
from app.pages.index import index
from app.pages.login import login_page
from app.pages.admin import admin_page
from app.pages.permissions import permissions_page
from app.state import AppState
from app.states.admin_state import AdminState
from app.states.permissions_state import PermissionsState
from app.pages.profile import profile_page

app = rx.App(
    theme=rx.theme(appearance="light", accent_color="purple", gray_color="slate"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(login_page, route="/")
app.add_page(index, route="/home", on_load=AppState.on_load)
app.add_page(profile_page, route="/profile")
app.add_page(admin_page, route="/admin", on_load=AppState.on_load)
app.add_page(
    permissions_page,
    route="/admin/permissions",
    on_load=PermissionsState.on_load_permissions,
)