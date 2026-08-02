import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED_CACHED = "skipped_cached"

@dataclass(frozen=True)
class Artifact:
    """Handle inmutable a un blob en el Content-Addressable Store (CAS)."""
    sha256: str
    uri: str
    mime: str
    size_bytes: int
    meta: dict = field(default_factory=dict)
    lineage: list = field(default_factory=list)

    @property
    def digest(self) -> str:
        return self.sha256

@dataclass
class Cost:
    usd: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    gpu_seconds: float = 0.0

    def __add__(self, other: "Cost") -> "Cost":
        return Cost(
            usd=self.usd + other.usd,
            tokens_in=self.tokens_in + other.tokens_in,
            tokens_out=self.tokens_out + other.tokens_out,
            gpu_seconds=self.gpu_seconds + other.gpu_seconds,
        )

def stable_hash(obj: Any) -> str:
    """Calcula un hash SHA256 determinista para cualquier estructura de datos."""
    def norm(o: Any) -> Any:
        if isinstance(o, Artifact):
            return {"__artifact__": o.sha256}
        if isinstance(o, dict):
            return {k: norm(o[k]) for k in sorted(o)}
        if isinstance(o, (list, tuple)):
            return [norm(x) for x in o]
        if isinstance(o, (str, int, float, bool)) or o is None:
            return o
        if isinstance(o, datetime):
            return o.astimezone(timezone.utc).isoformat()
        return repr(o)

    payload = json.dumps(norm(obj), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()
