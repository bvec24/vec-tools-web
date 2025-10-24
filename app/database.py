import os
import bcrypt
import logging
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.models import Base, User, Permission

DB_PATH = os.getenv("DB_PATH", "vec_tools.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Activa el modo WAL al conectar a la base de datos para mejor rendimiento."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout = 5000")
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager para obtener una sesión de base de datos de forma segura.
    Garantiza que la sesión se cierre correctamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Genera un hash de la contraseña usando bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def init_db():
    """
    Crea todas las tablas en la base de datos y un usuario administrador
    inicial si no existe ninguno.
    """
    try:
        Base.metadata.create_all(bind=engine)
        with get_session() as db:
            admin_user_exists = db.query(User).filter(User.is_admin == True).first()
            if not admin_user_exists:
                logging.info("No admin user found. Creating one...")
                admin_username = os.getenv("ADMIN_USER", "admin")
                admin_password = os.getenv("ADMIN_PASS", "admin_password")
                admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
                hashed = hash_password(admin_password)
                new_admin = User(
                    username=admin_username,
                    password_hash=hashed,
                    email=admin_email,
                    is_admin=True,
                    created_at=datetime.utcnow(),
                )
                db.add(new_admin)
                db.commit()
                logging.warning(
                    f"Admin user '{admin_username}' created. Please change the default password."
                )
    except Exception as e:
        logging.exception(f"An error occurred during DB initialization: {e}")


def sync_permissions(discovered_tools: list[dict]):
    """Syncs discovered script relpaths with the Permission table."""
    with get_session() as db:
        existing_permissions = {p.script_relpath for p in db.query(Permission).all()}
        discovered_relpaths = {tool["relpath"] for tool in discovered_tools}
        new_relpaths = discovered_relpaths - existing_permissions
        if new_relpaths:
            logging.info(
                f"Found {len(new_relpaths)} new scripts to add to permissions table."
            )
            for relpath in new_relpaths:
                db.add(Permission(script_relpath=relpath))
            db.commit()