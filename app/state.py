import reflex as rx
import os
from typing import TypedDict, cast, Optional
from . import utils
from .database import get_session, init_db, verify_password, sync_permissions
from .models import User as UserModel, UserPermission


class Tool(TypedDict):
    name: str
    relpath: str
    group: str
    title: str
    desc: str
    icon: str


class AppState(rx.State):
    """
    Estado principal de la aplicaci
    Gestiona la autenticaci	n, las herramientas, la interfaz y la ejecuci	n de scripts.
    """

    user: Optional[str] = None
    user_id: Optional[int] = None
    user_is_admin: bool = False
    user_permissions: set[str] = set()
    error_message: str = ""
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
        Devuelve el t	ulo de la herramienta actualmente seleccionada para el modal.
        """
        for tool in self.tools:
            if tool["relpath"] == self.selected_relpath:
                return tool.get("title") or tool.get("name")
        return "Resultado de Ejecuci\tn"

    @rx.var
    def groups_list(self) -> list[tuple[str, list[Tool]]]:
        """
        Convierte el diccionario de grupos a una lista de tuplas para usar en rx.foreach.
        """
        return sorted(list(self.groups.items()))

    @rx.var
    def has_tools(self) -> bool:
        """
        Devuelve True si hay al menos un grupo de herramientas.
        """
        return len(self.groups) > 0

    @rx.var
    def is_authenticated(self) -> bool:
        """
        Comprueba si el usuario est	 autenticado bas	ndose en la presencia del user_id.
        """
        return self.user_id is not None

    @rx.event
    def login(self, form_data: dict):
        """
        Valida las credenciales contra la base de datos y establece el estado de la sesi\x93n.
        Reflex se encarga de persistir el estado autom\x92ticamente.
        """
        username = form_data.get("username", "").strip()
        password = form_data.get("password", "").strip()
        with get_session() as db:
            user_in_db = (
                db.query(UserModel).filter(UserModel.username == username).first()
            )
            if user_in_db and verify_password(password, user_in_db.password_hash):
                self.user_id = user_in_db.id
                self.user = user_in_db.username
                self.user_is_admin = user_in_db.is_admin
                self.error_message = ""
                return rx.redirect("/")
            else:
                self.error_message = "Usuario o contrase\x91a incorrectos."
                self.user_id = None
                self.user = None
                self.user_is_admin = False

    @rx.event
    def logout(self):
        """
        Limpia el estado de la sesi\x93n y redirige a la p\x92gina de login.
        """
        self.reset()
        return rx.redirect("/login")

    @rx.event
    async def on_load(self):
        """
        Se ejecuta al cargar la p	ina. Inicializa la BD y descubre las herramientas.
        """
        init_db()
        if self.is_authenticated:
            all_discovered_tools = utils.discover_tools(self.tools_root_abs)
            sync_permissions(all_discovered_tools)
            with get_session() as db:
                if self.user_is_admin:
                    from app.states.admin_state import AdminState

                    admin_state = await self.get_state(AdminState)
                    await admin_state.load_users()
                    self.tools = [cast(Tool, t) for t in all_discovered_tools]
                else:
                    user_perms = (
                        db.query(UserPermission)
                        .join(UserPermission.permission)
                        .filter(UserPermission.user_id == self.user_id)
                        .all()
                    )
                    allowed_relpaths = {
                        up.permission.script_relpath for up in user_perms
                    }
                    self.user_permissions = allowed_relpaths
                    self.tools = [
                        cast(Tool, t)
                        for t in all_discovered_tools
                        if t["relpath"] in allowed_relpaths
                    ]
            new_groups = {}
            for tool in self.tools:
                group_name = tool["group"]
                if group_name not in new_groups:
                    new_groups[group_name] = []
                new_groups[group_name].append(tool)
            self.groups = new_groups
        else:
            self.tools = []
            self.groups = {}

    @rx.event(background=True)
    async def run_tool(self, relpath: str):
        """
        Ejecuta un script en un proceso de fondo, verificando permisos primero.
        """
        if not self.user_is_admin and relpath not in self.user_permissions:
            yield rx.toast.error("You do not have permission to run this script.")
            return
        async with self:
            self.running = True
            self.selected_relpath = relpath
            self.stdout = "Executing script..."
            self.stderr = ""
            self.modal_open = True
        result = await utils.run_script(self.tools_root_abs, relpath, timeout=60)
        async with self:
            self.stdout = result["stdout"]
            self.stderr = result["stderr"]
            if not result["ok"] and (not self.stderr):
                self.stderr = "Script failed without an explicit error (see stdout)."
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