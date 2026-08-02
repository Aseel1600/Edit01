#!/usr/bin/env python3
"""
Omega-Flow CLI Runner
Ejecutor de workflows .omega.json impulsado por el motor DAG asíncrono y Content-Addressable Store (CAS).
"""

import sys
import json
import asyncio
from pathlib import Path

# Resolver rutas relativas
MODULE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = MODULE_DIR.parent.parent
CAS_ROOT = PROJECT_DIR / ".cas"
PUBLIC_ROOT = PROJECT_DIR / "remotion-composer" / "public"
SCRATCH_DIR = PROJECT_DIR / "scratch"

from core.cas import CAS
from core.engine import OmegaFlowEngine

def main():
    args = sys.argv[1:]
    
    if len(args) == 0 or args[0] in ["-h", "--help"]:
        print("Uso: python3 runner.py run <path_to_workflow.json>")
        sys.exit(0)

    cmd = args[0]
    workflow_path_str = args[1] if len(args) > 1 else str(MODULE_DIR / "workflows" / "un_tio_blanco_hipocrita.omega.json")

    if cmd == "run":
        wf_path = Path(workflow_path_str)
        if not wf_path.exists():
            print(f"❌ Error: Archivo de workflow no encontrado en {wf_path}")
            sys.exit(1)

        with open(wf_path, "r", encoding="utf-8") as f:
            workflow_def = json.load(f)

        cas = CAS(root=CAS_ROOT, public_root=PUBLIC_ROOT)
        engine = OmegaFlowEngine(workflow=workflow_def, cas=cas, scratch_dir=SCRATCH_DIR)

        print("="*60)
        print(f" ⚡ OMEGA-FLOW CLI (Garantía de Atomicidad Estricta) ⚡")
        print("="*60)

        results = asyncio.run(engine.run(run_id="job_omega_live"))

        print("\n" + "="*60)
        print(" 📊 RESULTADOS DEL DAG:")
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
