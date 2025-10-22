import os
import json
import asyncio
import sys
import logging
from pathlib import Path
from typing import Any

EXCLUDE_DIRS = {"__pycache__", "tests", ".venv", "venv"}
EXCLUDE_FILES = {"__init__.py", "vec-tools.py"}


def load_tools_catalog(root_path: str) -> dict[str, dict[str, str]]:
    """
    Carga un archivo 'tools.json' opcional para enriquecer los datos de las herramientas.
    Busca en el directorio raíz del proyecto.
    """
    project_root = Path.cwd()
    parent_of_root = Path(root_path).parent
    potential_paths = [project_root / "tools.json", parent_of_root / "tools.json"]
    for catalog_path in potential_paths:
        if catalog_path.is_file():
            try:
                with open(catalog_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {item["relpath"]: item for item in data}
            except (json.JSONDecodeError, IOError) as e:
                logging.exception(f"Error loading tools catalog: {e}")
                return {}
    return {}


def discover_tools(root_path: str) -> list[dict[str, str]]:
    """
    Escanea el directorio `root_path` en busca de scripts .py.
    Normaliza y enriquece los datos de cada script.
    """
    discovered_tools = []
    catalog = load_tools_catalog(root_path)
    if not os.path.isdir(root_path):
        return []
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in filenames:
            if not filename.endswith(".py") or filename in EXCLUDE_FILES:
                continue
            full_path = os.path.join(dirpath, filename)
            relpath = os.path.relpath(full_path, root_path).replace("\\", "/")
            parts = relpath.split("/")
            group = parts[0] if len(parts) > 1 else "General"
            tool_data = {
                "name": Path(filename).stem,
                "relpath": relpath,
                "group": group,
                "title": "",
                "desc": "",
                "icon": "",
            }
            if relpath in catalog:
                tool_data.update(catalog[relpath])
            discovered_tools.append(tool_data)
    return discovered_tools


async def run_script(
    root: str, relpath: str, timeout: int = 60
) -> dict[str, bool | str]:
    """
    Ejecuta un script de forma segura usando un subproceso.
    """
    full_path = os.path.abspath(os.path.join(root, relpath))
    if not os.path.commonpath([full_path, os.path.abspath(root)]) == os.path.abspath(
        root
    ):
        return {
            "ok": False,
            "stdout": "",
            "stderr": "Error: Intento de acceso fuera del directorio de herramientas.",
        }
    if not os.path.isfile(full_path):
        return {
            "ok": False,
            "stdout": "",
            "stderr": f"Error: No se encontró el archivo {relpath}.",
        }
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            full_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )
        return {
            "ok": process.returncode == 0,
            "stdout": stdout_bytes.decode("utf-8", errors="ignore")[:4000],
            "stderr": stderr_bytes.decode("utf-8", errors="ignore")[:4000],
        }
    except asyncio.TimeoutError as e:
        logging.exception(f"Script timeout: {e}")
        return {
            "ok": False,
            "stdout": "",
            "stderr": f"Error: El script superó el tiempo límite de {timeout} segundos.",
        }
    except Exception as e:
        logging.exception(f"Unexpected error running script: {e}")
        return {
            "ok": False,
            "stdout": "",
            "stderr": f"Error de ejecución inesperado: {str(e)}",
        }