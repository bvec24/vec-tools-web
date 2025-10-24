import reflex as rx
from app.state import AppState
from app.pages.index import top_bar, sidebar
from app.states.admin_state import AdminState


def user_form_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.form(
                    rx.radix.primitives.dialog.title(
                        AdminState.modal_title,
                        class_name="text-xl font-bold text-gray-900 dark:text-white mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label("Username", class_name="text-sm font-medium"),
                            rx.el.input(
                                name="username",
                                default_value=AdminState.user_form_data["username"],
                                class_name="w-full px-3 py-2 border rounded-md",
                                disabled=AdminState.is_editing,
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.label("Email", class_name="text-sm font-medium"),
                            rx.el.input(
                                name="email",
                                type="email",
                                default_value=AdminState.user_form_data["email"],
                                class_name="w-full px-3 py-2 border rounded-md",
                            ),
                            class_name="mb-4",
                        ),
                        rx.cond(
                            ~AdminState.is_editing,
                            rx.el.div(
                                rx.el.label(
                                    "Password", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    name="password",
                                    type="password",
                                    class_name="w-full px-3 py-2 border rounded-md",
                                ),
                                class_name="mb-4",
                            ),
                        ),
                        rx.el.div(
                            rx.el.input(
                                type="checkbox",
                                name="is_admin",
                                default_checked=AdminState.user_form_data[
                                    "is_admin"
                                ].to(bool),
                            ),
                            rx.el.label("Is Admin?", class_name="ml-2"),
                            class_name="flex items-center mb-4",
                        ),
                    ),
                    rx.cond(
                        AdminState.user_form_error != "",
                        rx.el.div(
                            AdminState.user_form_error,
                            class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg mb-4 text-sm",
                        ),
                    ),
                    rx.el.div(
                        rx.radix.primitives.dialog.close(
                            rx.el.button(
                                "Cancel",
                                type="button",
                                on_click=AdminState.close_user_modal,
                                class_name="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg font-medium hover:bg-gray-300",
                            )
                        ),
                        rx.el.button(
                            AdminState.modal_submit_text,
                            type="submit",
                            class_name="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700",
                        ),
                        class_name="flex justify-end gap-4 mt-6",
                    ),
                    on_submit=AdminState.handle_user_form_submit,
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 w-full max-w-md z-50 dark:bg-gray-800",
            ),
        ),
        open=AdminState.is_user_modal_open,
        on_open_change=AdminState.close_user_modal,
    )


def delete_confirmation_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Confirm Deletion"),
            rx.alert_dialog.description(
                "Are you sure you want to delete this user? This action cannot be undone."
            ),
            rx.el.div(
                rx.alert_dialog.cancel(
                    rx.el.button(
                        "Cancel",
                        on_click=AdminState.close_delete_dialog,
                        variant="soft",
                    )
                ),
                rx.alert_dialog.action(
                    rx.el.button(
                        "Delete User",
                        on_click=AdminState.confirm_delete_user,
                        color_scheme="red",
                    )
                ),
                class_name="flex justify-end gap-4 mt-4",
            ),
            class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 w-full max-w-sm z-50 dark:bg-gray-800",
        ),
        open=AdminState.delete_dialog_open,
    )


def admin_page() -> rx.Component:
    HEADER_H = "64px"
    return rx.cond(
        AppState.is_authenticated & AppState.user_is_admin,
        rx.box(
            top_bar(),
            rx.box(
                sidebar(),
                rx.box(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Username",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Email",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Role",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Created At",
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
                                AdminState.all_users,
                                lambda user: rx.el.tr(
                                    rx.el.td(
                                        user["username"],
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    rx.el.td(
                                        user["email"],
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    rx.el.td(
                                        rx.cond(user["is_admin"], "Admin", "User"),
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    rx.el.td(
                                        user["created_at"].to_string(),
                                        class_name="px-6 py-4 whitespace-nowrap",
                                    ),
                                    rx.el.td(
                                        rx.el.button(
                                            "Edit",
                                            on_click=lambda: AdminState.open_edit_user_modal(
                                                user
                                            ),
                                            margin_right="1rem",
                                        ),
                                        rx.el.button(
                                            "Cambiar contraseña",
                                            on_click=lambda: AdminState.open_password_modal(
                                                user["id"], user["username"]
                                            ),
                                            color_scheme="purple",
                                            margin_right="1rem",
                                        ),
                                        rx.el.button(
                                            "Delete",
                                            on_click=lambda: AdminState.open_delete_dialog(
                                                user["id"]
                                            ),
                                            color_scheme="red",
                                            disabled=user["id"] == AppState.user_id,
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
                    padding="16px",
                    pt=HEADER_H,
                ),
                user_form_modal(),
                delete_confirmation_dialog(),
                rx.radix.primitives.dialog.root(
                    rx.radix.primitives.dialog.portal(
                        rx.radix.primitives.dialog.overlay(
                            class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
                        ),
                        rx.radix.primitives.dialog.content(
                            rx.el.form(
                                rx.el.h2(
                                    f"Cambiar contraseña de {AdminState.password_user_username}",
                                    class_name="text-xl font-bold mb-4 text-gray-900 dark:text-white",
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "Nueva contraseña",
                                        class_name="text-sm font-medium",
                                    ),
                                    rx.el.div(
                                        rx.el.input(
                                            type=rx.cond(
                                                AdminState.show_new_password,
                                                "text",
                                                "password",
                                            ),
                                            name="new_password",
                                            class_name="w-full px-3 py-2 border rounded-md mb-2",
                                            default_value=AdminState.new_password,
                                        ),
                                        rx.el.button(
                                            rx.icon(
                                                tag=rx.cond(
                                                    AdminState.show_new_password,
                                                    "eye-off",
                                                    "eye",
                                                )
                                            ),
                                            type="button",
                                            on_click=AdminState.toggle_show_new_password,
                                            class_name="ml-2 text-gray-500 hover:text-gray-700",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                ),
                                rx.el.div(
                                    rx.el.label(
                                        "Confirmar nueva contraseña",
                                        class_name="text-sm font-medium",
                                    ),
                                    rx.el.div(
                                        rx.el.input(
                                            type=rx.cond(
                                                AdminState.show_confirm_password,
                                                "text",
                                                "password",
                                            ),
                                            name="confirm_password",
                                            class_name="w-full px-3 py-2 border rounded-md mb-2",
                                            default_value=AdminState.confirm_password,
                                        ),
                                        rx.el.button(
                                            rx.icon(
                                                tag=rx.cond(
                                                    AdminState.show_confirm_password,
                                                    "eye-off",
                                                    "eye",
                                                )
                                            ),
                                            type="button",
                                            on_click=AdminState.toggle_show_confirm_password,
                                            class_name="ml-2 text-gray-500 hover:text-gray-700",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                ),
                                rx.cond(
                                    AdminState.password_error != "",
                                    rx.el.div(
                                        AdminState.password_error,
                                        class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg mb-4 text-sm",
                                    ),
                                ),
                                rx.cond(
                                    AdminState.password_success != "",
                                    rx.el.div(
                                        AdminState.password_success,
                                        class_name="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded-lg mb-4 text-sm",
                                    ),
                                ),
                                rx.el.div(
                                    rx.radix.primitives.dialog.close(
                                        rx.el.button(
                                            "Cancelar",
                                            type="button",
                                            on_click=AdminState.close_password_modal,
                                            class_name="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg font-medium hover:bg-gray-300",
                                        )
                                    ),
                                    rx.el.button(
                                        "Guardar",
                                        type="submit",
                                        class_name="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700",
                                    ),
                                    class_name="flex justify-end gap-4 mt-6",
                                ),
                                on_submit=AdminState.change_user_password,
                            ),
                            class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 w-full max-w-md z-50 dark:bg-gray-800",
                        ),
                    ),
                    open=AdminState.is_password_modal_open,
                    on_open_change=AdminState.close_password_modal,
                ),
            ),
            class_name="bg-gray-50 dark:bg-gray-950 min-h-screen font-['Inter']",
        ),
        "",
    )