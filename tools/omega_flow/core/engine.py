import asyncio
import json
import os
import sys
import time
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Any, Dict, List, Set

from core.contracts import Artifact, Cost, NodeStatus, stable_hash
from core.cas import CAS

class NodeContext:
    def __init__(self, run_id: str, node_id: str, cas: CAS, workdir: Path, params: dict, outputs: dict):
        self.run_id = run_id
        self.node_id = node_id
        self.cas = cas
        self.workdir = workdir
        self.params = params
        self.outputs = outputs
        self.cost = Cost()

    def get_output(self, parent_node_id: str) -> Any:
        return self.outputs.get(parent_node_id)

class OmegaFlowEngine:
    def __init__(self, workflow: dict, cas: CAS, scratch_dir: Path):
        self.workflow = workflow
        self.cas = cas
        self.scratch_dir = Path(scratch_dir)
        self.outputs: Dict[str, Any] = {}
        self.cache: Dict[str, Any] = {}
        self.nodes_by_id = {n["id"]: n for n in workflow["nodes"]}

    def _resolve_dag(self) -> List[str]:
        graph = {n["id"]: set(n.get("dependsOn", [])) for n in self.workflow["nodes"]}
        return list(TopologicalSorter(graph).static_order())

    async def run(self, run_id: str = "job_default") -> dict:
        order = self._resolve_dag()
        workdir = self.scratch_dir / run_id
        workdir.mkdir(parents=True, exist_ok=True)

        print(f"🚀 [Omega-Flow Engine] Iniciando ejecución del DAG '{self.workflow['name']}' (ID: {run_id})")
        start_time = time.time()

        for node_id in order:
            node_def = self.nodes_by_id[node_id]
            node_type = node_def["type"]
            node_params = node_def.get("params", {})

            # Fingerprint de caché
            fp = stable_hash({
                "type": node_type,
                "params": node_params,
                "inputs": {dep: self.outputs.get(dep) for dep in node_def.get("dependsOn", [])}
            })

            if fp in self.cache:
                print(f"  ⚡ [Caché Hit] Nodo '{node_id}' ({node_type}) reutilizado por fingerprint.")
                self.outputs[node_id] = self.cache[fp]
                continue

            print(f"  ▶ [Ejecutando Nodo] '{node_id}' ({node_def.get('name', node_type)})...")
            ctx = NodeContext(run_id, node_id, self.cas, workdir, node_params, self.outputs)

            # Carga dinámica del nodo
            node_fn = self._load_node_fn(node_type)
            result = await node_fn(ctx)

            self.outputs[node_id] = result
            self.cache[fp] = result

        elapsed = time.time() - start_time
        print(f"✅ [Omega-Flow Engine] Flujo completado en {elapsed:.2f}s")
        return self.outputs

    def _load_node_fn(self, node_type: str):
        if node_type == "media.broker":
            try:
                from nodes.media_broker import run_media_broker
            except ImportError:
                from tools.omega_flow.nodes.media_broker import run_media_broker
            return run_media_broker
        elif node_type == "remotion.render":
            from nodes.remotion_render import run_remotion_render
            return run_remotion_render
        else:
            raise ValueError(f"Nodo desconocido: {node_type}")
