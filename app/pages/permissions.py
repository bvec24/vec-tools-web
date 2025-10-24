import reflex as rx
from app.states.permissions_state import PermissionsState
from app.pages.index import top_bar, sidebar
from app.state import AppState


def permissions_modal() -> rx.Component:
    """Modal to edit permissions for a specific user."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    "Edit Permissions for ",
                    rx.el.span(
                        PermissionsState.selected_user_username,
                        class_name="font-bold text-purple-600",
                    ),
                    class_name="text-xl font-bold text-gray-900 dark:text-white mb-4",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="Search scripts...",
                        on_change=PermissionsState.set_search_term,
                        class_name="w-full px-3 py-2 border rounded-md mb-4",
                    ),
                    rx.el.div(
                        rx.foreach(
                            PermissionsState.filtered_permissions,
                            lambda p: rx.el.div(
                                rx.el.input(
                                    type="checkbox",
                                    checked=PermissionsState.user_permissions.contains(
                                        p["id"]
                                    ),
                                    on_change=lambda checked: PermissionsState.toggle_permission(
                                        p["id"], checked
                                    ),
                                    class_name="mr-2 h-4 w-4 rounded text-purple-600 focus:ring-purple-500",
                                ),
                                rx.el.label(
                                    p["script_relpath"],
                                    class_name="text-sm font-medium text-gray-700 dark:text-gray-300",
                                ),
                                class_name="flex items-center p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800",
                            ),
                        ),
                        class_name="max-h-96 overflow-y-auto space-y-1 border p-2 rounded-lg bg-gray-50 dark:bg-gray-900/50",
                    ),
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Close",
                            on_click=PermissionsState.close_permissions_modal,
                            class_name="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg font-medium hover:bg-gray-300",
                        )
                    ),
                    class_name="flex justify-end mt-6",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 w-full max-w-2xl z-50 dark:bg-gray-800",
            ),
        ),
        open=PermissionsState.is_modal_open,
    )


def permissions_page() -> rx.Component:
    """Page for managing user permissions."""
    return rx.el.main(
        rx.fragment(
            rx.cond(
                ~AppState.is_authenticated | ~AppState.user_is_admin,
                rx.redirect("/"),
                rx.noop(),
            )
        ),
        top_bar(),
        sidebar(),
        rx.el.div(
            rx.el.h1(
                "Permissions Management",
                class_name="text-2xl font-bold text-gray-800 dark:text-white mb-6",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "User",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Assigned Scripts",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Actions",
                                class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            PermissionsState.users_with_permissions,
                            lambda user_perm: rx.el.tr(
                                rx.el.td(
                                    user_perm["username"],
                                    class_name="px-6 py-4 whitespace-nowrap font-medium text-gray-900 dark:text-white",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        user_perm["permission_count"].to_string(),
                                        class_name="px-2.5 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800 dark:bg-purple-800/30 dark:text-purple-300",
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap",
                                ),
                                rx.el.td(
                                    rx.el.button(
                                        "Edit Permissions",
                                        on_click=lambda: PermissionsState.open_permissions_modal(
                                            user_perm["user_id"]
                                        ),
                                        class_name="font-medium text-purple-600 hover:text-purple-800",
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
                                ),
                                class_name="bg-white dark:bg-gray-800",
                            ),
                        ),
                        class_name="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700",
                    ),
                    class_name="min-w-full divide-y divide-gray-200 dark:divide-gray-700",
                ),
                class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg dark:border-gray-700",
            ),
            class_name="ml-64 pt-20 px-8 pb-8 h-full",
        ),
        permissions_modal(),
        class_name="bg-gray-50 dark:bg-gray-950 min-h-screen font-['Inter']",
    )