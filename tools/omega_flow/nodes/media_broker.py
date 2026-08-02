from pathlib import Path
from ..core.engine import NodeContext
from ..core.contracts import Artifact

async def run_media_broker(ctx: NodeContext) -> dict:
    """Nodo Media Broker: Registra y publica evidencias en el CAS para Remotion."""
    input_dir = Path(ctx.params.get("input_dir", "./inputs"))
    out_evidences = []

    # Crear una imagen placeholder dummy en disco para simular extracción
    sample_img = ctx.workdir / "frame_001.png"
    if not sample_img.exists():
        # Escribir un PNG de 1x1 píxel transparente o byte array simulado
        sample_img.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01Haf\xa4\x00\x00\x00\x00IEND\xaeB`\x82")

    # Registrar en el CAS
    artifact = ctx.cas.put_file(sample_img, "image/png", meta={"kicker": "EVIDENCIA 01"})

    # Publicar para Remotion
    rel_path = ctx.cas.publish_for_remotion(artifact, ctx.run_id, "frame_001.png")

    out_evidences.append({
        "id": "ev_001",
        "type": "image",
        "src": rel_path,
        "caption": "Captura original extraída del material fuente.",
        "kicker": "EVIDENCIA 01",
        "source": "Media Broker CAS",
        "timestamp": "00:01:14",
        "fit": "contain",
        "durationSeconds": 3.5,
        "emphasis": "hard"
    })

    print(f"  ✓ [Media Broker] {len(out_evidences)} evidencia(s) procesada(s) y publicadas en el CAS.")
    return {
        "jobId": ctx.run_id,
        "title": "UN TÍO BLANCO HIPÓCRITA",
        "subtitle": "Informe Forense — Omega Pipeline",
        "evidences": out_evidences
    }
