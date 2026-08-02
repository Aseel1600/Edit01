#!/usr/bin/env python3
"""
OpenMontage Photo Summarizer Pipeline (Sistema de Resumen de Fotos a Vídeo)
Ingiere un directorio de fotos, genera resúmenes visuales y compila una presentación en Remotion.
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Resolver rutas relativas
TOOLS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TOOLS_DIR.parent
OMEGA_FLOW_DIR = TOOLS_DIR / "omega_flow"
sys.path.insert(0, str(OMEGA_FLOW_DIR))

from core.cas import CAS
from core.engine import OmegaFlowEngine
from core.atomic import atomic_write_json

def analyze_photo(photo_path: Path, index: int) -> dict:
    """
    Analiza una foto individual, extrae metadatos y genera una descripción/caption.
    """
    filename = photo_path.name
    size_mb = photo_path.stat().st_size / (1024 * 1024)
    
    # Generar un kicker y caption basado en el nombre y posición
    kicker = f"FOTO {String_pad(index + 1)}"
    caption = f"Análisis visual de {filename} ({size_mb:.1f} MB)"
    
    return {
        "id": f"photo_{index + 1:03d}",
        "filename": filename,
        "path": str(photo_path),
        "kicker": kicker,
        "caption": caption
    }

def String_pad(n: int) -> str:
    return f"{n:02d}"

def generate_photo_summary(photos_dir: Path, target_output_json: Path) -> dict:
    print(f"📷 [Photo Summarizer] Escaneando imágenes en: {photos_dir}")
    valid_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    
    photos = [p for p in photos_dir.iterdir() if p.suffix.lower() in valid_exts]
    photos.sort(key=lambda p: p.name)
    
    if not photos:
        print(f"⚠️ No se encontraron imágenes válidas en {photos_dir}. Usando placeholder por defecto.")
        return {
            "title": "Resumen Fotográfico",
            "subtitle": "Álbum no encontrado",
            "evidences": []
        }
        
    analyzed_evidences = []
    for i, photo in enumerate(photos):
        info = analyze_photo(photo, i)
        analyzed_evidences.append({
            "id": info["id"],
            "type": "image",
            "src": info["path"],
            "caption": info["caption"],
            "kicker": info["kicker"],
            "source": "Directorio Local",
            "fit": "contain",
            "durationSeconds": 4.0,
            "emphasis": "normal"
        })
        
    summary_manifest = {
        "title": f"Resumen Visual: {photos_dir.name}",
        "subtitle": f"Colección de {len(analyzed_evidences)} fotografías procesadas",
        "evidences": analyzed_evidences
    }
    
    atomic_write_json(target_output_json, summary_manifest)
    print(f"✓ Resumen visual generado con {len(analyzed_evidences)} foto(s). Manifest: {target_output_json}")
    return summary_manifest

def run_pipeline(photos_dir_path: str):
    photos_dir = Path(photos_dir_path).resolve()
    if not photos_dir.exists():
        print(f"❌ Error: La carpeta {photos_dir} no existe.")
        sys.exit(1)
        
    scratch_manifest = PROJECT_DIR / "scratch" / "photo_summary_manifest.json"
    manifest = generate_photo_summary(photos_dir, scratch_manifest)
    
    # Iniciar la ejecución a través del motor Omega-Flow
    cas = CAS(root=PROJECT_DIR / ".cas", public_root=PROJECT_DIR / "remotion-composer" / "public")
    
    # Workflow dinámico en memoria
    workflow_def = {
        "id": "photo-summary-workflow",
        "name": f"Resumen Fotográfico - {photos_dir.name}",
        "version": "1.0.0",
        "nodes": [
            {
                "id": "broker",
                "type": "media.broker",
                "name": "Registrar fotos en el CAS",
                "params": {"input_dir": str(photos_dir)}
            },
            {
                "id": "render",
                "type": "remotion.render",
                "name": "Renderizar Resumen en Remotion",
                "params": {
                    "composition": "UnTioBlancoHipocrita",
                    "remotion_dir": str(PROJECT_DIR / "remotion-composer")
                },
                "dependsOn": ["broker"]
            }
        ]
    }
    
    engine = OmegaFlowEngine(workflow=workflow_def, cas=cas, scratch_dir=PROJECT_DIR / "scratch")
    
    print("\n="*60)
    print(f" 🎬 INICIANDO COMPILACIÓN DE VÍDEO PARA EL ÁLBUM FOTOGRÁFICO")
    print("="*60)
    
    results = asyncio.run(engine.run(run_id=f"job_photos_{photos_dir.name}"))
    
    print("\n" + "="*60)
    print(" 🎉 VÍDEO DE RESUMEN FOTOGRÁFICO COMPLETADO")
    print(f" 📂 Ruta del vídeo final: {results['render']['output_video_path']}")
    print("="*60 + "\n")

def main():
    args = sys.argv[1:]
    target_dir = args[0] if len(args) > 0 else str(PROJECT_DIR / "scratch")
    run_pipeline(target_dir)

if __name__ == "__main__":
    main()
