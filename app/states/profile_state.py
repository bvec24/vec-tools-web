import reflex as rx
from app.state import AppState
from app.models import User as UserModel
from app.database import get_session, verify_password, hash_password


class ProfileState(rx.State):
    current_password: str = ""
    new_password: str = ""
    confirm_password: str = ""
    error_message: str = ""
    success_message: str = ""
    modal_open: bool = False

    @rx.event
    def open_modal(self):
        self.modal_open = True
        self.error_message = ""
        self.success_message = ""
        self.current_password = ""
        self.new_password = ""
        self.confirm_password = ""

    @rx.event
    def close_modal(self):
        self.modal_open = False
        self.error_message = ""
        self.success_message = ""
        self.current_password = ""
        self.new_password = ""
        self.confirm_password = ""

    @rx.event
    def set_value(self, key: str, value: str):
        setattr(self, key, value)

    @rx.event
    async def change_password(self, form_data: dict):
        current_password = form_data.get("current_password", "").strip()
        new_password = form_data.get("new_password", "").strip()
        confirm_password = form_data.get("confirm_password", "").strip()
        if not current_password or not new_password or (not confirm_password):
            self.error_message = "Todos los campos son obligatorios."
            return
        if new_password != confirm_password:
            self.error_message = "La nueva contraseña y la confirmación no coinciden."
            return
        app_state = await self.get_state(AppState)
        user_id = app_state.user_id
        while hasattr(user_id, "value"):
            user_id = user_id.value
        if not isinstance(user_id, (int, float, str)):
            self.error_message = "No se pudo obtener el ID de usuario válido."
            return
        user_id = int(user_id)
        if user_id is None:
            self.error_message = "No se pudo obtener el ID de usuario válido."
            return
        with get_session() as db:
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user or not verify_password(current_password, user.password_hash):
                self.error_message = "La contraseña actual es incorrecta."
                return
            user.password_hash = hash_password(new_password)
            db.commit()
        self.success_message = "Contraseña cambiada exitosamente."
        self.error_message = ""
        self.current_password = ""
        self.new_password = ""
        self.confirm_password = ""
        self.modal_open = False