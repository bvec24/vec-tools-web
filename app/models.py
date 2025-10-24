import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """
    Modelo de usuario para autenticación y permisos.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True, index=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    permissions = relationship(
        "UserPermission", back_populates="user", cascade="all, delete-orphan"
    )


class Permission(Base):
    """
    Modelo que representa un permiso para ejecutar un script específico.
    """

    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    script_relpath = Column(String(500), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)


class UserPermission(Base):
    """
    Tabla de asociación para vincular usuarios con permisos.
    """

    __tablename__ = "user_permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    granted_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="permissions")
    permission = relationship("Permission")