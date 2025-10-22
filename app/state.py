import reflex as rx
import os
from typing import TypedDict, cast, Optional
from . import utils

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "super-secret-default-key")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "vec_tools_session")
SESSION_MAX_AGE_SECONDS = int(os.getenv("SESSION_MAX_AGE_SECONDS", "3600"))
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin")


class Tool(TypedDict):
    name: str
    relpath: str
    group: str
    title: str
    desc: str
    icon: str


class AppState(rx.State):
    """
    Estado principal de la aplicación.
    Gestiona la autenticación, las herramientas, la interfaz y la ejecución de scripts.
    """

    user: Optional[str] = None
    error_message: str = ""
    theme_dark: bool = False
    theme_cookie: str | None = rx.Cookie(name="theme_dark_cookie")
    tools: list[Tool] = []
    groups: dict[str, list[Tool]] = {}
    running: bool = False
    selected_relpath: str = ""
    stdout: str = ""
    stderr: str = ""
    modal_open: bool = False
    tools_root_abs: str = os.getenv(
        "TOOLS_ROOT_ABS", os.path.join(os.getcwd(), "support_scripts")
    )

    @rx.var
    def selected_tool_title(self) -> str:
        """
        Devuelve el t_tulo de la herramienta actualmente seleccionada para el modal.
        """
        for tool in self.tools:
            if tool["relpath"] == self.selected_relpath:
                return tool.get("title") or tool.get("name")
        return "Resultado de Ejecuci_n"

    @rx.var
    def groups_list(self) -> list[tuple[str, list[Tool]]]:
        """
        Convierte el diccionario de grupos a una lista de tuplas para usar en rx.foreach.
        """
        return list(self.groups.items())

    @rx.var
    def has_tools(self) -> bool:
        """
        Devuelve True si hay al menos un grupo de herramientas.
        """
        return len(self.groups) > 0

    @rx.var
    def is_authenticated(self) -> bool:
        """
        Comprueba si el usuario está autenticado basándose en la presencia del token de sesión.
        """
        return self.router.session.client_token is not None

    @rx.event
    def hydrate_user(self):
        """
        Lee el nombre de usuario de la cookie de sesi
        Reflex gestiona la cookie internamente a trav
        """
        if self.is_authenticated:
            self.user = ADMIN_USER
        else:
            self.user = None
        self.theme_dark = self.theme_cookie == "dark"
        self.error_message = ""

    @rx.event
    def login(self, form_data: dict):
        """
        Valida las credenciales y establece la cookie de sesión si son correctas.
        """
        username = form_data.get("username", "").strip()
        password = form_data.get("password", "").strip()
        if username == ADMIN_USER and password == ADMIN_PASS:
            self.user = username
            self.error_message = ""
            return rx.redirect("/", token=username)
        else:
            self.error_message = "Usuario o contraseña incorrectos."
            self.user = None

    @rx.event
    def logout(self):
        """
        Elimina la cookie de sesión y redirige a la página de login.
        """
        self.user = None
        return rx.redirect("/login")

    @rx.event
    def toggle_theme(self):
        """
        Cambia entre el tema claro y oscuro.
        """
        self.theme_dark = not self.theme_dark
        self.theme_cookie = "dark" if self.theme_dark else "light"

    @rx.event
    def on_load(self):
        """
        Se ejecuta al cargar la página del dashboard. Descubre y agrupa las herramientas.
        """
        discovered_tools = utils.discover_tools(self.tools_root_abs)
        self.tools = [cast(Tool, t) for t in discovered_tools]
        new_groups = {}
        for tool in self.tools:
            group_name = tool["group"]
            if group_name not in new_groups:
                new_groups[group_name] = []
            new_groups[group_name].append(tool)
        self.groups = new_groups

    @rx.event(background=True)
    async def run_tool(self, relpath: str):
        """
        Ejecuta un script en un proceso de fondo.
        """
        async with self:
            self.running = True
            self.selected_relpath = relpath
            self.stdout = "Ejecutando script..."
            self.stderr = ""
            self.modal_open = True
        result = await utils.run_script(self.tools_root_abs, relpath, timeout=60)
        async with self:
            self.stdout = result["stdout"]
            self.stderr = result["stderr"]
            if not result["ok"] and (not self.stderr):
                self.stderr = "El script falló sin un error explícito (ver stdout)."
            self.running = False

    @rx.event
    def close_modal(self):
        """
        Cierra el modal de resultados.
        """
        self.modal_open = False
        self.stdout = ""
        self.stderr = ""
        self.selected_relpath = ""