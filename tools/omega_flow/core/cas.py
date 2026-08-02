import hashlib
from pathlib import Path
from typing import Any, Optional
from .contracts import Artifact
from .atomic import atomic_copy_file, atomic_write_bytes

class CAS:
    """Content-Addressable Store con Garantía de Atomicidad Estricta."""

    def __init__(self, root: Path, public_root: Optional[Path] = None):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.public_root = Path(public_root) if public_root else None

    def _shard(self, digest: str) -> Path:
        return self.root / digest[:2] / digest[2:4] / digest

    def put_file(
        self, src: Path, mime: str,
        meta: dict | None = None,
        lineage: list | None = None,
    ) -> Artifact:
        src = Path(src)
        h = hashlib.sha256()
        size = 0
        with open(src, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
                size += len(chunk)
        digest = h.hexdigest()

        dest = self._shard(digest)
        if not dest.exists():
            # Escritura atómica
            atomic_copy_file(src, dest)

        return Artifact(
            sha256=digest, uri=f"cas://{digest}", mime=mime,
            size_bytes=size, meta=meta or {}, lineage=lineage or [],
        )

    def put_bytes(self, data: bytes, mime: str, **kw) -> Artifact:
        h = hashlib.sha256(data).hexdigest()
        dest = self._shard(h)
        if not dest.exists():
            atomic_write_bytes(dest, data)

        return Artifact(
            sha256=h, uri=f"cas://{h}", mime=mime,
            size_bytes=len(data), meta=kw.get("meta", {}), lineage=kw.get("lineage", []),
        )

    def path(self, a: Artifact) -> Path:
        return self._shard(a.sha256)

    def publish_for_remotion(self, a: Artifact, job_id: str, filename: str) -> str:
        """Enlaza/copia atómicamente el activo en public/omega/<job_id>/ para Remotion."""
        if self.public_root is None:
            raise RuntimeError("CAS.public_root no configurado.")
            
        rel = Path("omega") / job_id / filename
        dest = self.public_root / rel
        
        if not dest.exists():
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.hardlink_to(self.path(a))
            except Exception:
                atomic_copy_file(self.path(a), dest)
                
        return str(rel).replace("\\", "/")
