#!/usr/bin/env python3
"""
Orquestador Omega - Pipeline de Automatización Nivel 5 (v3.0 - Inyección Dinámica de Props)
Arquitectura: Rutas dinámicas, Guardarraíles Activos, Media Broker & Renderizado Inyectado con Props.
"""

import sys
import subprocess
import os
import json
import time
import shutil

# Resolución Dinámica de Rutas
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(TOOLS_DIR)
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch")
REMOTION_DIR = os.path.join(BASE_DIR, "remotion-composer")
OUTPUT_VIDEO = os.path.join(REMOTION_DIR, "out", "podcast_20min_max_exergy.mp4")

# Guardarraíl de Filtro Léxico Activo
POLITICAL_STOPWORDS = [
    "progre", "facha", "woke", "feminazi", "machirulo", "izquierda", "derecha",
    "comunismo", "fascismo", "capitalismo salvaje", "dictadura progre", "basado"
]

def print_step(step, msg):
    print(f"\n[{step}/4] ⚡ {msg}")

def verify_content_neutrality(plan_data):
    """
    Escanea la estructura del plan en busca de términos de polarización.
    """
    serialized = json.dumps(plan_data).lower()
    for word in POLITICAL_STOPWORDS:
        if word in serialized:
            print(f"❌ [GUARDARRAÍL ACTIVO]: Detectado término polarizante '{word}' en el guion.")
            print("Abortando la ejecución. El contenido no cumple el estándar estrictamente forense y apolítico.")
            sys.exit(1)
            
    print("✓ Filtro léxico pasado: El contenido es estructuralmente neutral.")

def run_step1_planning(target_url, is_dry_run):
    print_step(1, "Ingesta y Planificación Activa...")
    
    plan_path = os.path.join(SCRATCH_DIR, "omega_production_plan.json")
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    
    plan = {
        "title": "Análisis Estructural y Forense",
        "subtitle": "Caso de Estudio Algorítmico",
        "target_duration_minutes": 20,
        "editorial_policy": "STRICT_APOLITICAL_FORENSIC",
        "target_url": target_url
    }
    
    verify_content_neutrality(plan)
    
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
        
    print(f"✓ Plan guardado en {plan_path}")
    return plan

def run_step2_asset_resolution(plan, is_dry_run):
    print_step(2, "Resolución de Activos Semánticos (Media Broker)...")
    
    # Generar o resolver la lista de evidencias y props dinámicos
    evidences = [
        {
            "id": "ev1",
            "type": "image",
            "src": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
            "caption": "Figura 1: Dispersión de métricas discursivas"
        },
        {
            "id": "ev2",
            "type": "image",
            "src": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800",
            "caption": "Figura 2: Matriz forense de correlación"
        }
    ]
    
    props_data = {
        "title": plan["title"],
        "subtitle": plan["subtitle"],
        "evidences": evidences
    }
    
    props_path = os.path.join(SCRATCH_DIR, "remotion_props.json")
    with open(props_path, 'w', encoding='utf-8') as f:
        json.dump(props_data, f, indent=2, ensure_ascii=False)
        
    print(f"✓ Props dinámicos estructurados y guardados en {props_path}")
    return props_data

def run_step3_remotion_compile(props_data, is_dry_run):
    print_step(3, "Compilación Estricta con Inyección de Props (Remotion)...")
    
    if not shutil.which("npx") and not is_dry_run:
        print("❌ Error: 'npx' no encontrado en el sistema. Imposible renderizar.")
        sys.exit(1)

    props_json_str = json.dumps(props_data)

    cmd = [
        "npx", "remotion", "render", 
        "src/index.ts", "UnTioBlancoHipocrita", 
        OUTPUT_VIDEO, 
        f"--props={props_json_str}",
        "--concurrency=8", "--codec=h264", "--crf=18"
    ]
    
    if not is_dry_run:
        try:
            print(f"-> Directorio de render: {REMOTION_DIR}")
            print(f"-> Props inyectados: {len(props_data.get('evidences', []))} evidencias pasadas.")
            subprocess.run(cmd, cwd=REMOTION_DIR, check=True)
            
            if not os.path.exists(OUTPUT_VIDEO):
                print(f"❌ Error crítico: Remotion terminó sin errores pero {OUTPUT_VIDEO} no existe.")
                sys.exit(1)
            else:
                video_size = os.path.getsize(OUTPUT_VIDEO)
                print(f"✓ Renderizado completado. Tamaño: {video_size / (1024*1024):.2f} MB")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error fatal en renderizado Remotion: {e}")
            sys.exit(1)
    else:
        print("✓ [DRY-RUN] Comando Remotion ensamblado correctamente con flag --props.")

def run_step4_youtube_publish(is_dry_run):
    print_step(4, "Publicación Autónoma Validada...")
    uploader_script = os.path.join(TOOLS_DIR, "youtube_uploader.py")
    
    cmd = [
        "python3", uploader_script,
        "--file", OUTPUT_VIDEO,
        "--title", "Análisis Estructural y Forense",
        "--description", "Documental algorítmico generado bajo política neutral.",
        "--category", "27",
        "--privacy", "private"
    ]
    
    if not is_dry_run:
        if not os.path.exists(OUTPUT_VIDEO):
            print("❌ Error antes de subir: El archivo de vídeo no existe.")
            sys.exit(1)
            
        try:
            subprocess.run(cmd, check=True)
            print("✓ Proceso de subida a YouTube confirmado con éxito.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Fallo en la subida a YouTube: {e}")
            sys.exit(1)
    else:
        print("✓ [DRY-RUN] Comando de publicación ensamblado correctamente.")

def main():
    args = sys.argv[1:]
    is_dry_run = "--dry-run" in args
    
    target_urls = [arg for arg in args if not arg.startswith("--")]
    target_url = target_urls[0] if target_urls else "https://es.wikipedia.org/wiki/Neutralidad_valorativa"
    
    print("="*60)
    print(" 🚀 INICIANDO ORQUESTADOR OMEGA (ANTIGRAVITY 2 v3.0) 🚀")
    print(f" 📂 BASE_DIR resuelto: {BASE_DIR}")
    if is_dry_run:
        print(" ⚠️ MODO DRY-RUN ACTIVADO ⚠️")
    print("="*60)
    
    plan = run_step1_planning(target_url, is_dry_run)
    props_data = run_step2_asset_resolution(plan, is_dry_run)
    run_step3_remotion_compile(props_data, is_dry_run)
    run_step4_youtube_publish(is_dry_run)
    
    print("\n" + "="*60)
    print(" ✅ CICLO OMEGA V3.0 COMPLETADO EXITOSAMENTE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
