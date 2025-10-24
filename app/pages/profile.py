import reflex as rx
from app.states.profile_state import ProfileState
from app.pages.index import top_bar, sidebar

def profile_page() -> rx.Component:
    return rx.el.main(
        top_bar(),
        sidebar(),
        rx.el.div(
            rx.el.h1(
                "Mi Perfil",
                class_name="text-2xl font-bold text-gray-800 dark:text-white mb-6",
            ),
            rx.el.button(
                "Cambiar contraseña",
                on_click=ProfileState.open_modal,
                class_name="bg-purple-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors mb-8",
            ),
            rx.radix.primitives.dialog.root(
                rx.radix.primitives.dialog.portal(
                    rx.radix.primitives.dialog.overlay(
                        class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
                    ),
                    rx.radix.primitives.dialog.content(
                        rx.el.form(
                            rx.el.h2(
                                "Cambiar contraseña",
                                class_name="text-xl font-bold mb-4 text-gray-900 dark:text-white",
                            ),
                            rx.el.div(
                                rx.el.label("Contraseña actual", class_name="text-sm font-medium"),
                                rx.el.input(
                                    type="password",
                                    value=ProfileState.current_password,
                                    on_change=lambda v: ProfileState.set_value("current_password", v),
                                    class_name="w-full px-3 py-2 border rounded-md mb-4",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label("Nueva contraseña", class_name="text-sm font-medium"),
                                rx.el.input(
                                    type="password",
                                    value=ProfileState.new_password,
                                    on_change=lambda v: ProfileState.set_value("new_password", v),
                                    class_name="w-full px-3 py-2 border rounded-md mb-4",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label("Confirmar nueva contraseña", class_name="text-sm font-medium"),
                                rx.el.input(
                                    type="password",
                                    value=ProfileState.confirm_password,
                                    on_change=lambda v: ProfileState.set_value("confirm_password", v),
                                    class_name="w-full px-3 py-2 border rounded-md mb-4",
                                ),
                            ),
                            rx.cond(
                                ProfileState.error_message != "",
                                rx.el.div(
                                    ProfileState.error_message,
                                    class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg mb-4 text-sm",
                                ),
                            ),
                            rx.cond(
                                ProfileState.success_message != "",
                                rx.el.div(
                                    ProfileState.success_message,
                                    class_name="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded-lg mb-4 text-sm",
                                ),
                            ),
                            rx.el.div(
                                rx.radix.primitives.dialog.close(
                                    rx.el.button(
                                        "Cancelar",
                                        type="button",
                                        on_click=ProfileState.close_modal,
                                        class_name="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg font-medium hover:bg-gray-300",
                                    )
                                ),
                                rx.el.button(
                                    "Guardar",
                                    type="button",
                                    on_click=ProfileState.change_password,
                                    class_name="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700",
                                ),
                                class_name="flex justify-end gap-4 mt-6",
                            ),
                        ),
                        class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-2xl p-6 w-full max-w-md z-50 dark:bg-gray-800",
                    ),
                ),
                open=ProfileState.modal_open,
                on_open_change=ProfileState.close_modal,
            ),
            class_name="ml-64 pt-20 px-8 pb-8 h-full",
        ),
        class_name="bg-gray-50 dark:bg-gray-950 min-h-screen font-['Inter']",
    )
