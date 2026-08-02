#!/usr/bin/env python3
"""
OpenMontage - Autonomous URL-to-Video Production Producer
Takes any URL or topic input, runs extraction, generates scene breakdown,
and prepares the Remotion video composition pipeline.
"""

import sys
import json
import subprocess
import os
import re

def inspect_url(target_url):
    print(f"[1/4] Inspecting target URL/topic: {target_url}...")
    is_youtube = "youtube.com" in target_url or "youtu.be" in target_url
    
    metadata = {
        "target": target_url,
        "is_youtube": is_youtube,
        "title": "Autonomous Video Production",
        "description": ""
    }

    if is_youtube:
        try:
            res = subprocess.run(["yt-dlp", "--dump-json", "--no-download", target_url], capture_output=True, text=True)
            if res.returncode == 0:
                info = json.loads(res.stdout)
                metadata["title"] = info.get("title", metadata["title"])
                metadata["uploader"] = info.get("uploader", "Unknown")
                metadata["duration"] = info.get("duration", 0)
                metadata["description"] = info.get("description", "")[:500]
        except Exception as e:
            print(f"Warning extracting yt-dlp metadata: {e}")
            
    return metadata

def generate_production_plan(metadata, duration_minutes=30):
    print(f"[2/4] Generating 5-Act Production Plan ({duration_minutes} min duration target)...")
    title = metadata["title"]
    
    acts = [
        {"act": 1, "name": "Prólogo & Gancho Inicial", "duration_sec": 300, "scenes": 5, "theme": "Introducción dramática y planteamiento del conflicto."},
        {"act": 2, "name": "Contexto & Orígenes", "duration_sec": 600, "scenes": 10, "theme": "Antecedentes históricos, entorno y primeros pasos."},
        {"act": 3, "name": "El Nudo: Hitos y Controversias", "duration_sec": 600, "scenes": 10, "theme": "Eventos clave, grandes logros o polémicas centrales."},
        {"act": 4, "name": "Análisis Epistémico / Discursivo", "duration_sec": 600, "scenes": 10, "theme": "Desmontaje técnico, análisis de impacto y recepción."},
        {"act": 5, "name": "Conclusión & Legado", "duration_sec": 300, "scenes": 5, "theme": "Síntesis final, impacto futuro y cierre del documental."}
    ]
    
    return {
        "project_name": re.sub(r'[^\w\-]', '_', title.lower())[:30],
        "title": title,
        "target_duration_minutes": duration_minutes,
        "acts": acts,
        "total_scenes": sum(a["scenes"] for a in acts),
        "rendering_engine": "remotion-composer"
    }

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "https://es.wikipedia.org/wiki/Samuel_Beckett"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    meta = inspect_url(target)
    plan = generate_production_plan(meta, duration)
    
    print("\n[3/4] Production Plan Generated Successfully:")
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    
    output_plan_path = f"/Users/borjafernandezangulo/.gemini/antigravity-ide/brain/fa120028-472f-4599-9aa7-be23247c8821/scratch/production_plan.json"
    with open(output_plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
        
    print(f"\n[4/4] Plan saved to: {output_plan_path}")
    print("Ready to trigger Remotion render stage!")

if __name__ == "__main__":
    main()
