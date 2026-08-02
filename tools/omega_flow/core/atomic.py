import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

def atomic_write_bytes(dest_path: Path, data: bytes) -> Path:
    """Escribe datos en un archivo de forma estrictamente atómica (write + sync + atomic replace)."""
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(dir=dest_path.parent, delete=False, suffix=".tmp") as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name

    os.replace(tmp_name, dest_path)
    return dest_path

def atomic_copy_file(src_path: Path, dest_path: Path) -> Path:
    """Copia un archivo a un destino de forma atómica."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(dir=dest_path.parent, delete=False, suffix=".tmp") as tmp:
        tmp_name = tmp.name

    shutil.copy2(src_path, tmp_name)
    os.replace(tmp_name, dest_path)
    return dest_path

def atomic_write_json(dest_path: Path, data: Any, indent: int = 2) -> Path:
    """Persiste una estructura JSON de forma atómica."""
    payload = json.dumps(data, indent=indent, ensure_ascii=False).encode('utf-8')
    return atomic_write_bytes(dest_path, payload)
