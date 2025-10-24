import reflex as rx
from typing import TypedDict
from app.database import get_session
from app.models import User, Permission, UserPermission


class UserPermissionInfo(TypedDict):
    user_id: int
    username: str
    permission_count: int


class PermissionData(TypedDict):
    id: int
    script_relpath: str


class PermissionsState(rx.State):
    """Manages the state for the permissions page."""

    users_with_permissions: list[UserPermissionInfo] = []
    all_permissions: list[PermissionData] = []
    search_term: str = ""
    is_modal_open: bool = False
    selected_user_id: int = -1
    selected_user_username: str = ""
    user_permissions: list[int] = []

    @rx.var
    def filtered_permissions(self) -> list[PermissionData]:
        """Filters permissions based on the search term."""
        if not self.search_term:
            return self.all_permissions
        return [
            p
            for p in self.all_permissions
            if self.search_term.lower() in p["script_relpath"].lower()
        ]

    @rx.event
    async def on_load_permissions(self):
        """Loads all necessary data when the permissions page is accessed."""
        with get_session() as db:
            users = (
                db.query(User)
                .filter(User.is_admin == False)
                .order_by(User.username)
                .all()
            )
            permissions = db.query(Permission).order_by(Permission.script_relpath).all()
            self.all_permissions = [
                {"id": p.id, "script_relpath": p.script_relpath} for p in permissions
            ]
            user_perms_info = []
            for user in users:
                count = (
                    db.query(UserPermission)
                    .filter(UserPermission.user_id == user.id)
                    .count()
                )
                user_perms_info.append(
                    {
                        "user_id": user.id,
                        "username": user.username,
                        "permission_count": count,
                    }
                )
            self.users_with_permissions = user_perms_info

    @rx.event
    def open_permissions_modal(self, user_id: int):
        """Opens the modal to edit permissions for a given user."""
        self.selected_user_id = user_id
        with get_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return rx.toast.error("User not found.")
            self.selected_user_username = user.username
            permissions = (
                db.query(UserPermission.permission_id)
                .filter(UserPermission.user_id == user_id)
                .all()
            )
            self.user_permissions = [p[0] for p in permissions]
        self.is_modal_open = True
        self.search_term = ""

    @rx.event
    def close_permissions_modal(self):
        """Closes the permissions modal and resets state."""
        self.is_modal_open = False
        self.selected_user_id = -1
        self.selected_user_username = ""
        self.user_permissions = []
        return PermissionsState.on_load_permissions

    @rx.event
    def toggle_permission(self, permission_id: int, is_granted: bool):
        """Grants or revokes a permission for the selected user."""
        with get_session() as db:
            if is_granted:
                existing = (
                    db.query(UserPermission)
                    .filter(
                        UserPermission.user_id == self.selected_user_id,
                        UserPermission.permission_id == permission_id,
                    )
                    .first()
                )
                if not existing:
                    new_permission = UserPermission(
                        user_id=self.selected_user_id, permission_id=permission_id
                    )
                    db.add(new_permission)
                    db.commit()
                    self.user_permissions.append(permission_id)
            else:
                to_delete = (
                    db.query(UserPermission)
                    .filter(
                        UserPermission.user_id == self.selected_user_id,
                        UserPermission.permission_id == permission_id,
                    )
                    .first()
                )
                if to_delete:
                    db.delete(to_delete)
                    db.commit()
                    if permission_id in self.user_permissions:
                        self.user_permissions.remove(permission_id)
        return rx.toast.info("Permissions updated.", duration=1500)