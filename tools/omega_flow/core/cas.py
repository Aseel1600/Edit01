import hashlib
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional
from .contracts import Artifact

class CAS:
    """Content-Addressable Store. Deduplica y da inmutabilidad a los medios."""

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
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".tmp")
            shutil.copy2(src, tmp)
            tmp.replace(dest)

        return Artifact(
            sha256=digest, uri=f"cas://{digest}", mime=mime,
            size_bytes=size, meta=meta or {}, lineage=lineage or [],
        )

    def put_bytes(self, data: bytes, mime: str, **kw) -> Artifact:
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(data)
            tmp = Path(t.name)
        try:
            return self.put_file(tmp, mime, **kw)
        finally:
            tmp.unlink(missing_ok=True)

    def path(self, a: Artifact) -> Path:
        return self._shard(a.sha256)

    def publish_for_remotion(self, a: Artifact, job_id: str, filename: str) -> str:
        """Enlaza el activo en public/omega/<job_id>/ y devuelve la ruta relativa para staticFile()."""
        if self.public_root is None:
            raise RuntimeError("CAS.public_root no configurado.")
            
        rel = Path("omega") / job_id / filename
        dest = self.public_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        if not dest.exists():
            try:
                dest.hardlink_to(self.path(a))
            except Exception:
                shutil.copy2(self.path(a), dest)
                
        return str(rel).replace("\\", "/")
