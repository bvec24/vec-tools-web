import reflex as rx

def index():
    return rx.el.div(
        rx.el.button("Switch", on_click=rx.toggle_color_mode),
        class_name="bg-gray-50 dark:bg-gray-900 min-h-screen"
    )

app = rx.App(
    theme=rx.theme(appearance="inherit"),
)
app.add_page(index, route="/")