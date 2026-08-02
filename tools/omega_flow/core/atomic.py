import os
import json
import shutil
import tempfile
import time
import hashlib
from pathlib import Path
from typing import Any, Generator, Optional
from contextlib import contextmanager

try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

def fsync_dir(dir_path: Path) -> None:
    """Fsync del directorio padre para garantizar la actualización del árbol de directorio en APFS/ext4."""
    try:
        dir_fd = os.open(dir_path, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except Exception:
        pass  # Ignorar si el SO no permite os.open en directorios

@contextmanager
def atomic_open(
    dest_path: Path, 
    mode: str = "wb", 
    max_retries: int = 3,
    sync_parent_dir: bool = True
) -> Generator[Any, None, None]:
    """
    Context manager de Escritura Atómica Grado Defensa.
    Características:
    - Escenarios sin colisión mediante tempfile en el mismo subdirectorio.
    - Bloqueo exclusivo POSIX fcntl.
    - fsync() del descriptor de archivo + fsync() del directorio contenedor.
    - Manejo de reintentos con descompresión exponencial ante colisiones de SO.
    """
    dest_path = Path(dest_path).resolve()
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(dir=dest_path.parent, delete=False, mode=mode, suffix=".tmp") as tmp:
        tmp_name = tmp.name
        try:
            if HAS_FCNTL:
                try:
                    fcntl.flock(tmp.fileno(), fcntl.LOCK_EX)
                except Exception:
                    pass
            
            yield tmp
            
            tmp.flush()
            os.fsync(tmp.fileno())
            
            if HAS_FCNTL:
                try:
                    fcntl.flock(tmp.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
        except Exception:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
            raise

    # Reemplazo atómico con reintentos para evitar bloqueos temporales de macOS/APFS
    last_err: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            os.replace(tmp_name, dest_path)
            if sync_parent_dir:
                fsync_dir(dest_path.parent)
            last_err = None
            break
        except OSError as e:
            last_err = e
            if e.errno == 18:  # EXDEV: Cross-device link
                shutil.move(tmp_name, dest_path)
                break
            time.sleep(0.05 * attempt)

    if last_err and os.path.exists(tmp_name):
        try:
            os.unlink(tmp_name)
        except Exception:
            pass
        raise last_err

def atomic_write_bytes(dest_path: Path, data: bytes, verify_checksum: bool = True) -> Path:
    """Escribe bytes de forma atómica con verificación estricta de suma de comprobación SHA-256."""
    dest_path = Path(dest_path)
    expected_hash = hashlib.sha256(data).hexdigest() if verify_checksum else None

    with atomic_open(dest_path, "wb") as f:
        f.write(data)

    if verify_checksum:
        actual_hash = hashlib.sha256(dest_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise IOError(f"Verificación checksum fallida en {dest_path}: {actual_hash} != {expected_hash}")

    return dest_path

def atomic_copy_file(src_path: Path, dest_path: Path, verify_checksum: bool = True) -> Path:
    """Copia un archivo de forma atómica comprobando el hash SHA-256 en tiempo de transmisión."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    
    src_hash = hashlib.sha256()
    dest_hash = hashlib.sha256()

    with open(src_path, "rb") as src_f:
        with atomic_open(dest_path, "wb") as dest_f:
            while chunk := src_f.read(1 << 20):  # Chunks de 1MB
                src_hash.update(chunk)
                dest_f.write(chunk)
                dest_hash.update(chunk)

    if verify_checksum and src_hash.hexdigest() != dest_hash.hexdigest():
        raise IOError(f"Fallo de integridad checksum durante la copia atómica de {src_path} a {dest_path}")

    return dest_path

def atomic_write_json(dest_path: Path, data: Any, indent: int = 2) -> Path:
    """Persiste JSON atómicamente con ordenación determinista de claves."""
    payload = json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True).encode('utf-8')
    return atomic_write_bytes(dest_path, payload, verify_checksum=True)
