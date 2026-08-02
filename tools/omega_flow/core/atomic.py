import os
import json
import shutil
import tempfile
import fcntl
from pathlib import Path
from typing import Any, Generator
from contextlib import contextmanager

@contextmanager
def atomic_open(dest_path: Path, mode: str = "wb") -> Generator[Any, None, None]:
    """
    Context manager de Escritura Atómica con fsync y bloqueo de archivo POSIX (fcntl).
    Garantiza que si hay un error a mitad de escritura, el archivo destino NUNCA se corrompe.
    """
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(dir=dest_path.parent, delete=False, mode=mode, suffix=".tmp") as tmp:
        tmp_name = tmp.name
        try:
            # Adquirir un bloqueo exclusivo en el archivo temporal
            try:
                fcntl.flock(tmp.fileno(), fcntl.LOCK_EX)
            except Exception:
                pass  # Fallback si el sistema no soporta fcntl
            
            yield tmp
            
            # Forzar la descarga física al disco
            tmp.flush()
            os.fsync(tmp.fileno())
            
            try:
                fcntl.flock(tmp.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
        except Exception:
            # Si ocurre un error dentro de la transacción, eliminar el archivo temporal
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
            raise

    # Reemplazo atómico POSIX
    os.replace(tmp_name, dest_path)

def atomic_write_bytes(dest_path: Path, data: bytes) -> Path:
    """Escribe bytes de forma atómica comprobando el tamaño final."""
    dest_path = Path(dest_path)
    with atomic_open(dest_path, "wb") as f:
        f.write(data)
    
    if os.path.getsize(dest_path) != len(data):
        raise IOError(f"Verificación de tamaño fallida en {dest_path}")
        
    return dest_path

def atomic_copy_file(src_path: Path, dest_path: Path) -> Path:
    """Copia un archivo a un destino de forma atómica."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(src_path, "rb") as src_f:
        with atomic_open(dest_path, "wb") as dest_f:
            shutil.copyfileobj(src_f, dest_f, length=1<<20)

    return dest_path

def atomic_write_json(dest_path: Path, data: Any, indent: int = 2) -> Path:
    """Persiste una estructura JSON de forma atómica en UTF-8."""
    payload = json.dumps(data, indent=indent, ensure_ascii=False).encode('utf-8')
    return atomic_write_bytes(dest_path, payload)
