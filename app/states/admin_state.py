import reflex as rx
from typing import Any, Optional, TypedDict
from app.database import get_session, hash_password
from app.models import User as UserModel
from datetime import datetime


class UserData(TypedDict):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: str


class AdminState(rx.State):
    is_password_modal_open: bool = False
    password_user_id: Optional[int] = None
    password_user_username: str = ""
    new_password: str = ""
    confirm_password: str = ""
    password_error: str = ""
    password_success: str = ""
    show_new_password: bool = False
    show_confirm_password: bool = False

    @rx.event
    def open_password_modal(self, user_id: int, username: str):
        self.is_password_modal_open = True
        self.password_user_id = user_id
        self.password_user_username = username
        self.new_password = ""
        self.confirm_password = ""
        self.password_error = ""
        self.password_success = ""
        self.show_new_password = False
        self.show_confirm_password = False

    @rx.event
    def close_password_modal(self):
        self.is_password_modal_open = False
        self.password_user_id = None
        self.password_user_username = ""
        self.new_password = ""
        self.confirm_password = ""
        self.password_error = ""
        self.password_success = ""
        self.show_new_password = False
        self.show_confirm_password = False

    @rx.event
    def set_password_value(self, key: str, value: str):
        setattr(self, key, value)

    @rx.event
    def toggle_show_new_password(self):
        self.show_new_password = not self.show_new_password

    @rx.event
    def toggle_show_confirm_password(self):
        self.show_confirm_password = not self.show_confirm_password

    @rx.event
    async def change_user_password(self, form_data: dict):
        new_password = form_data.get("new_password", "").strip()
        confirm_password = form_data.get("confirm_password", "").strip()
        if not new_password or not confirm_password:
            self.password_error = "Todos los campos son obligatorios."
            return
        if new_password != confirm_password:
            self.password_error = "Las contraseñas no coinciden."
            return
        with get_session() as db:
            user = (
                db.query(UserModel)
                .filter(UserModel.id == self.password_user_id)
                .first()
            )
            if not user:
                self.password_error = "Usuario no encontrado."
                return
            user.password_hash = hash_password(new_password)
            db.commit()
        self.password_success = (
            f"Contraseña de {self.password_user_username} cambiada exitosamente."
        )
        self.password_error = ""
        self.new_password = ""
        self.confirm_password = ""

    all_users: list[UserData] = []
    is_user_modal_open: bool = False
    is_editing: bool = False
    editing_user_id: Optional[int] = None
    user_form_data: dict[str, str | bool] = {
        "username": "",
        "email": "",
        "password": "",
        "is_admin": False,
    }
    user_form_error: str = ""
    delete_dialog_open: bool = False
    user_to_delete_id: Optional[int] = None

    @rx.var
    def modal_title(self) -> str:
        return "Edit User" if self.is_editing else "Create New User"

    @rx.var
    def modal_submit_text(self) -> str:
        return "Save Changes" if self.is_editing else "Create User"

    @rx.event
    async def load_users(self):
        with get_session() as db:
            users = db.query(UserModel).order_by(UserModel.id).all()
            self.all_users = [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_admin": user.is_admin,
                    "created_at": user.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for user in users
            ]

    @rx.event
    def set_form_value(self, key: str, value: Any):
        self.user_form_data[key] = value

    def _reset_form(self):
        self.is_editing = False
        self.editing_user_id = None
        self.user_form_data = {
            "username": "",
            "email": "",
            "password": "",
            "is_admin": False,
        }
        self.user_form_error = ""

    @rx.event
    def open_create_user_modal(self):
        self._reset_form()
        self.is_user_modal_open = True

    @rx.event
    def open_edit_user_modal(self, user: dict):
        self.is_editing = True
        self.editing_user_id = user["id"]
        self.user_form_data = {
            "username": user["username"],
            "email": user["email"],
            "is_admin": user["is_admin"],
            "password": "",
        }
        self.user_form_error = ""
        self.is_user_modal_open = True

    @rx.event
    def close_user_modal(self):
        self.is_user_modal_open = False
        self.user_form_error = ""
        self._reset_form()

    @rx.event
    async def handle_user_form_submit(self, form_data: dict):
        self.user_form_data["username"] = form_data.get("username", "").strip()
        self.user_form_data["email"] = form_data.get("email", "").strip()
        self.user_form_data["is_admin"] = form_data.get("is_admin") == "on"
        if self.is_editing:
            await self._update_user()
        else:
            self.user_form_data["password"] = form_data.get("password", "").strip()
            await self._create_user()

    async def _create_user(self):
        username = self.user_form_data.get("username", "").strip()
        email = self.user_form_data.get("email", "").strip()
        password = self.user_form_data.get("password", "").strip()
        if not username or not email or (not password):
            self.user_form_error = "Username, email, and password are required."
            return
        with get_session() as db:
            existing_user = (
                db.query(UserModel).filter(UserModel.username == username).first()
            )
            if existing_user:
                self.user_form_error = "Username already exists."
                return
            hashed = hash_password(password)
            new_user = UserModel(
                username=username,
                email=email,
                password_hash=hashed,
                is_admin=self.user_form_data.get("is_admin", False),
                created_at=datetime.utcnow(),
            )
            db.add(new_user)
            db.commit()
        self.is_user_modal_open = False
        await self.load_users()
        return rx.toast.success("User created successfully!")

    async def _update_user(self):
        email = self.user_form_data.get("email", "").strip()
        if not email:
            self.user_form_error = "Email cannot be empty."
            return
        with get_session() as db:
            user = (
                db.query(UserModel).filter(UserModel.id == self.editing_user_id).first()
            )
            if user:
                user.email = email
                user.is_admin = self.user_form_data.get("is_admin", False)
                db.commit()
        self.is_user_modal_open = False
        await self.load_users()
        return rx.toast.success("User updated successfully!")

    @rx.event
    def open_delete_dialog(self, user_id: int):
        self.user_to_delete_id = user_id
        self.delete_dialog_open = True

    @rx.event
    def close_delete_dialog(self):
        self.delete_dialog_open = False

    @rx.event
    async def confirm_delete_user(self):
        self.delete_dialog_open = False
        with get_session() as db:
            user = (
                db.query(UserModel)
                .filter(UserModel.id == self.user_to_delete_id)
                .first()
            )
            if user:
                db.delete(user)
                db.commit()
        await self.load_users()
        return rx.toast.info("User deleted.")