import reflex as rx
from app.state import AppState
from app.pages.index import top_bar, sidebar
from app.states.permissions_state import PermissionsState

HEADER_H = "64px"


def _users_table() -> rx.Component:
    """Tabla de usuarios con contador de permisos y botón Editar."""
    return rx.el.table(
        rx.el.thead(
            rx.el.tr(
                rx.el.th(
                    "Usuario",
                    class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                ),
                rx.el.th(
                    "# Permisos",
                    class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                ),
                rx.el.th("", class_name="px-4 py-3"),
            )
        ),
        rx.el.tbody(
            rx.foreach(
                PermissionsState.users_with_permissions,
                lambda u: rx.el.tr(
                    rx.el.td(u.username, class_name="px-4 py-2 whitespace-nowrap"),
                    rx.el.td(
                        u.permission_count, class_name="px-4 py-2 whitespace-nowrap"
                    ),
                    rx.el.td(
                        rx.button(
                            "Editar",
                            size="2",
                            on_click=lambda: PermissionsState.open_permissions_modal(
                                u.user_id
                            ),
                        ),
                        class_name="px-4 py-2 text-right",
                    ),
                    class_name="bg-white dark:bg-gray-800",
                ),
            ),
            class_name="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700",
        ),
        class_name="min-w-full divide-y divide-gray-200 dark:divide-gray-700",
    )


def _permissions_list() -> rx.Component:
    """Listado de permisos (filtrable) — se usa dentro del modal."""
    return rx.el.table(
        rx.el.thead(
            rx.el.tr(
                rx.el.th(
                    "ID",
                    class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                ),
                rx.el.th(
                    "Script",
                    class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                ),
                rx.el.th(
                    "Concedido",
                    class_name="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                ),
            )
        ),
        rx.el.tbody(
            rx.foreach(
                PermissionsState.all_permissions,
                lambda p: rx.el.tr(
                    rx.el.td(p.id, class_name="px-4 py-2 whitespace-nowrap"),
                    rx.el.td(
                        p.script_relpath, class_name="px-4 py-2 whitespace-nowrap"
                    ),
                    rx.el.td(
                        rx.checkbox(
                            checked=PermissionsState.user_permissions.contains(
                                p.id
                            ).bool(),
                            on_change=lambda v: PermissionsState.toggle_permission(
                                p.id, v
                            ),
                        ),
                        class_name="px-4 py-2",
                    ),
                    class_name="bg-white dark:bg-gray-800",
                ),
            ),
            class_name="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700",
        ),
        class_name="min-w-full divide-y divide-gray-200 dark:divide-gray-700",
    )


def _edit_permissions_modal() -> rx.Component:
    """Panel/modal para editar permisos del usuario seleccionado."""
    return rx.cond(
        PermissionsState.is_modal_open,
        rx.box(
            rx.hstack(
                rx.heading(
                    rx.text.strong("Editar permisos de "),
                    rx.code(PermissionsState.selected_user_username),
                    size="5",
                ),
                rx.spacer(),
                rx.icon_button(
                    "x",
                    variant="soft",
                    on_click=PermissionsState.close_permissions_modal,
                ),
                align="center",
                width="100%",
                mb="3",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Buscar por ruta de script…",
                    on_change=PermissionsState.set_search_term,
                    width="100%",
                    default_value=PermissionsState.search_term,
                ),
                align="center",
                width="100%",
                mb="3",
            ),
            rx.box(
                _permissions_list(),
                class_name="shadow overflow-hidden border border-gray-200 sm:rounded-lg dark:border-gray-700",
            ),
            class_name="fixed inset-x-4 top-20 md:inset-x-20 lg:inset-x-40 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-2xl p-4 z-50",
        ),
        rx.fragment(),
    )


def permissions_page() -> rx.Component:
    """Página de permisos (admin)."""
    return rx.cond(
        AppState.is_authenticated & AppState.user_is_admin,
        rx.box(
            top_bar(),
            rx.box(
                sidebar(),
                rx.box(
                    rx.hstack(
                        rx.heading("Permisos", size="6"),
                        rx.spacer(),
                        rx.button(
                            "Refrescar", on_click=PermissionsState.on_load_permissions
                        ),
                        align="center",
                        width="100%",
                        mb="4",
                    ),
                    rx.box(
                        _users_table(),
                        class_name="shadow overflow-hidden border border-gray-200 sm:rounded-lg dark:border-gray-700",
                    ),
                    _edit_permissions_modal(),
                    padding="16px",
                    pt=HEADER_H,
                ),
            ),
            class_name="bg-gray-50 dark:bg-gray-950 min-h-screen font-['Inter']",
        ),
        rx.fragment(),
    )