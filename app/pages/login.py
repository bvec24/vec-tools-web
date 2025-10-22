import reflex as rx
from app.state import AppState


def login_page() -> rx.Component:
    """
    Página de inicio de sesión con un diseño limpio y centrado.
    """
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.img(
                    src="https://backoffice.staging.vecfleet.io/static/media/logo-login-app.3ef99420e5a1cc400d8f.png",
                    class_name="h-16 mx-auto mb-8",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.input(
                            placeholder="Usuario",
                            name="username",
                            type="text",
                            class_name="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:ring-purple-500 focus:border-purple-500",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.input(
                            placeholder="Contraseña",
                            name="password",
                            type="password",
                            class_name="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:ring-purple-500 focus:border-purple-500",
                        ),
                        class_name="mb-6",
                    ),
                    rx.cond(
                        AppState.error_message != "",
                        rx.el.div(
                            AppState.error_message,
                            class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg relative mb-4 text-sm",
                        ),
                        None,
                    ),
                    rx.el.button(
                        "LOGIN",
                        type="submit",
                        class_name="w-full bg-purple-600 text-white font-semibold py-3 rounded-lg hover:bg-purple-700 transition-colors",
                    ),
                    on_submit=AppState.login,
                ),
                class_name="bg-white p-8 md:p-10 rounded-xl shadow-lg border border-gray-100 w-full max-w-sm",
            ),
            class_name="min-h-screen flex items-center justify-center p-4",
        ),
        class_name="bg-gray-50 font-['Inter']",
    )


login = login_page