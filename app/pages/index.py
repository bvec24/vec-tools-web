import reflex as rx
from app.state import AppState, Tool
from typing import cast

LOGO_URL = "https://backoffice.staging.vecfleet.io/static/media/logo-login-app.3ef99420e5a1cc400d8f.png"


def top_bar() -> rx.Component:
    """
    Barra de navegación superior fija con logo, título, toggle de tema y botón de logout.
    """
    return rx.el.header(
        rx.el.div(
            rx.el.img(src=LOGO_URL, class_name="h-8"),
            rx.el.h1(
                "VEC Tools",
                class_name="text-xl font-bold text-gray-800 dark:text-white",
            ),
            class_name="flex items-center gap-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon(tag="sun", class_name="h-5 w-5 text-gray-500"),
                rx.el.button(
                    rx.el.span(
                        class_name=rx.color_mode_cond(
                            light="block w-4 h-4 rounded-full bg-gray-600 transform translate-x-0 transition-transform",
                            dark="block w-4 h-4 rounded-full bg-white transform translate-x-4 transition-transform",
                        )
                    ),
                    class_name=rx.color_mode_cond(
                        light="w-10 h-6 rounded-full p-1 bg-gray-300 transition-all",
                        dark="w-10 h-6 rounded-full p-1 bg-purple-600 transition-all",
                    ),
                    on_click=rx.toggle_color_mode,
                ),
                rx.icon(tag="moon", class_name="h-5 w-5 text-gray-500"),
                class_name="flex items-center gap-2",
            ),
            rx.el.button(
                "LOGOUT",
                on_click=AppState.logout,
                class_name="bg-purple-50 hover:bg-purple-100 text-purple-700 font-semibold px-4 py-2 rounded-lg text-sm transition-colors dark:bg-purple-800/20 dark:text-purple-300 dark:hover:bg-purple-800/40",
            ),
            class_name="flex items-center gap-6",
        ),
        class_name="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-sm border-b border-gray-200 dark:bg-gray-900/80 dark:border-gray-800 flex items-center justify-between px-6 z-30",
    )


def sidebar() -> rx.Component:
    """
    Barra lateral con la lista de grupos de herramientas.
    """
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Grupos",
                    class_name="text-sm font-semibold text-gray-500 uppercase tracking-wider px-4 pb-2",
                ),
                rx.el.nav(
                    rx.foreach(
                        AppState.groups_list,
                        lambda group_item: rx.el.a(
                            rx.icon(tag="folder", class_name="h-5 w-5 text-gray-400"),
                            rx.el.span(
                                group_item[0],
                                class_name="font-medium text-gray-700 dark:text-gray-300",
                            ),
                            href=f"#{group_item[0]}",
                            class_name="flex items-center gap-3 px-4 py-2.5 rounded-lg hover:bg-purple-50 dark:hover:bg-gray-800 transition-colors",
                        ),
                    ),
                    class_name="flex flex-col gap-1",
                ),
                class_name="flex-1 overflow-y-auto p-4",
            ),
            rx.el.div(
                rx.el.a(
                    rx.icon(tag="user", class_name="h-5 w-5 text-gray-400"),
                    rx.el.span(
                        "Mi Perfil",
                        class_name="font-medium text-gray-700 dark:text-gray-300",
                    ),
                    href="/profile",
                    class_name="flex items-center gap-3 px-4 py-2.5 rounded-lg hover:bg-purple-50 dark:hover:bg-gray-800 transition-colors",
                ),
                rx.cond(
                    AppState.user_is_admin,
                    rx.el.div(
                        rx.el.a(
                            rx.icon(tag="users", class_name="h-5 w-5 text-gray-400"),
                            rx.el.span(
                                "Admin",
                                class_name="font-medium text-gray-700 dark:text-gray-300",
                            ),
                            href="/admin",
                            class_name="flex items-center gap-3 px-4 py-2.5 rounded-lg hover:bg-purple-50 dark:hover:bg-gray-800 transition-colors",
                        ),
                        rx.el.a(
                            rx.icon(
                                tag="shield-check", class_name="h-5 w-5 text-gray-400"
                            ),
                            rx.el.span(
                                "Permissions",
                                class_name="font-medium text-gray-700 dark:text-gray-300",
                            ),
                            href="/admin/permissions",
                            class_name="flex items-center gap-3 px-4 py-2.5 rounded-lg hover:bg-purple-50 dark:hover:bg-gray-800 transition-colors",
                        ),
                        class_name="space-y-1",
                    ),
                ),
                class_name="border-t border-gray-200 dark:border-gray-800 p-4 space-y-1",
            ),
        ),
        class_name="fixed top-16 bottom-0 left-0 w-64 bg-white border-r border-gray-200 dark:bg-gray-900 dark:border-gray-800 flex flex-col pt-4 z-20",
    )


def tool_card(tool: Tool) -> rx.Component:
    """
    Tarjeta individual para una herramienta.
    """
    tool_var = cast(rx.Var, tool)
    has_permission = AppState.user_is_admin | AppState.user_permissions.contains(
        tool_var["relpath"]
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    rx.cond(tool_var["icon"] != "", tool_var["icon"], "settings"),
                    class_name="h-6 w-6 text-purple-600",
                ),
                rx.cond(
                    ~has_permission,
                    rx.icon(tag="lock", class_name="h-4 w-4 text-yellow-500"),
                    rx.fragment(),
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.span(
                tool_var["group"],
                class_name="text-xs font-semibold text-purple-700 bg-purple-100 dark:text-purple-300 dark:bg-purple-800/30 px-2.5 py-1 rounded-full w-fit",
            ),
            class_name="flex items-center justify-between mb-3",
        ),
        rx.el.h3(
            rx.cond(tool_var["title"] != "", tool_var["title"], tool_var["name"]),
            class_name="font-bold text-gray-800 dark:text-white text-lg mb-1 truncate",
        ),
        rx.el.p(
            rx.cond(tool_var["desc"] != "", tool_var["desc"], tool_var["relpath"]),
            class_name="text-sm text-gray-500 dark:text-gray-400 mb-4 h-10 overflow-hidden",
        ),
        rx.el.button(
            "Ejecutar",
            rx.icon(tag="play", class_name="ml-2 h-4 w-4"),
            on_click=lambda: AppState.run_tool(tool_var["relpath"]),
            disabled=~has_permission,
            class_name="w-full bg-gray-800 text-white font-semibold py-2.5 rounded-lg hover:bg-gray-900 dark:bg-purple-600 dark:hover:bg-purple-700 transition-colors flex items-center justify-center disabled:bg-gray-400 disabled:cursor-not-allowed dark:disabled:bg-gray-600",
        ),
        class_name="bg-white p-5 rounded-xl border border-gray-200 shadow-md hover:shadow-lg hover:border-purple-300 transition-all duration-300 transform hover:-translate-y-1 dark:bg-gray-800/50 dark:border-gray-700 dark:hover:border-purple-500",
        opacity=rx.cond(has_permission, "100%", "60%"),
    )


def results_modal() -> rx.Component:
    """
    Modal para mostrar los resultados (STDOUT/STDERR) de la ejecución.
    """
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    AppState.selected_tool_title,
                    class_name="text-xl font-bold text-gray-900 dark:text-white mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "STDOUT",
                                class_name="font-semibold text-gray-700 dark:text-gray-300 mb-2",
                            ),
                            rx.el.button(
                                rx.icon(tag="copy"),
                                on_click=rx.set_clipboard(AppState.stdout),
                                class_name="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300",
                            ),
                            class_name="flex justify-between items-center",
                        ),
                        rx.el.pre(
                            rx.el.code(
                                AppState.stdout,
                                class_name="text-xs font-mono dark:text-gray-300",
                            ),
                            class_name="bg-gray-50 p-4 rounded-md border max-h-64 overflow-y-auto dark:bg-gray-800 dark:border-gray-700",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "STDERR",
                                class_name="font-semibold text-red-700 dark:text-red-400 mb-2",
                            ),
                            rx.el.button(
                                rx.icon(tag="copy"),
                                on_click=rx.set_clipboard(AppState.stderr),
                                class_name="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300",
                            ),
                            class_name="flex justify-between items-center",
                        ),
                        rx.el.pre(
                            rx.el.code(
                                AppState.stderr,
                                class_name="text-xs font-mono text-red-600 dark:text-red-400",
                            ),
                            class_name="bg-red-50 p-4 rounded-md border border-red-200 max-h-64 overflow-y-auto dark:bg-red-900/20 dark:border-red-500/30",
                        ),
                        class_name=rx.cond(AppState.stderr != "", "block", "hidden"),
                    ),
                    rx.el.div(
                        rx.spinner(class_name="text-purple-600 dark:text-purple-400"),
                        rx.el.p(
                            "Ejecutando...",
                            class_name="text-sm text-gray-500 dark:text-gray-400 ml-3",
                        ),
                        class_name="flex items-center justify-center mt-4",
                        hidden=~AppState.running,
                    ),
                    class_name="text-sm",
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Cerrar",
                            on_click=AppState.close_modal,
                            class_name="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600",
                        )
                    ),
                    class_name="flex justify-end mt-6 pt-4 border-t dark:border-gray-700",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 w-full max-w-2xl z-50 dark:bg-gray-800 dark:border dark:border-gray-700",
            ),
        ),
        open=AppState.modal_open,
        on_open_change=AppState.close_modal,
    )


def index() -> rx.Component:
    """
    Página principal del dashboard.
    """
    return rx.cond(
        AppState.is_authenticated,
        rx.el.main(
            top_bar(),
            sidebar(),
            rx.el.div(
                rx.cond(
                    AppState.has_tools,
                    rx.foreach(
                        AppState.groups_list,
                        lambda group_item: rx.el.section(
                            rx.el.h2(
                                group_item[0],
                                id=group_item[0],
                                class_name="text-2xl font-bold text-gray-800 dark:text-white mb-6 pt-4 scroll-mt-20",
                            ),
                            rx.el.div(
                                rx.foreach(group_item[1], tool_card),
                                class_name="grid grid-cols-[repeat(auto-fill,minmax(300px,1fr))] gap-6",
                            ),
                            class_name="mb-12",
                        ),
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                tag="folder-x", class_name="h-12 w-12 text-gray-400"
                            ),
                            rx.el.h3(
                                "No hay herramientas disponibles",
                                class_name="mt-4 text-lg font-semibold text-gray-600 dark:text-gray-400",
                            ),
                            rx.el.p(
                                "No se encontraron scripts en el directorio configurado.",
                                class_name="mt-1 text-sm text-gray-500 dark:text-gray-400",
                            ),
                            class_name="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 dark:bg-gray-800/20 dark:border-gray-700",
                        ),
                        class_name="flex items-center justify-center h-full",
                    ),
                ),
                class_name="ml-64 pt-20 px-8 pb-8 h-full",
            ),
            results_modal(),
            class_name="bg-gray-50 dark:bg-gray-950 min-h-screen font-['Inter']",
        ),
        rx.fragment(),
    )