#!/usr/bin/env python3
"""
OpenMontage Nexus Engine v2.0 - Core Basado en Ingeniería Inversa de N8N
Soporte para INodeExecutionData, ExpressionEvaluator ($json / $node), Hooks y Reintentos.
"""

import sys
import os
import json
import asyncio
import re
import time
from typing import List, Dict, Any

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(TOOLS_DIR)

# ============================================================================
# ESTÁNDAR DE DATOS DE N8N: INodeExecutionData
# ============================================================================

class NodeExecutionItem:
    def __init__(self, json_data: Dict[str, Any], binary_data: Dict[str, Any] = None):
        self.json = json_data
        self.binary = binary_data or {}

    def to_dict(self):
        return {"json": self.json, "binary": self.binary}

# Type alias para listas de ítems
NodeDataItems = List[NodeExecutionItem]

# ============================================================================
# EVALUADOR DE EXPRESIONES (N8N Expression Evaluator Replica)
# ============================================================================

class ExpressionEvaluator:
    @staticmethod
    def resolve(template: str, current_item: NodeExecutionItem, history: Dict[str, NodeDataItems]) -> str:
        """
        Resuelve sintaxis tipo {{ $json.key }} o {{ $node["NombreNodo"].json.key }}
        """
        if not isinstance(template, str) or "{{" not in template:
            return template

        def replacer(match):
            expr = match.group(1).strip()
            
            # Caso 1: $json.prop
            if expr.startswith("$json."):
                prop = expr[6:]
                return str(current_item.json.get(prop, f"[Error: {prop} no encontrado]"))
                
            # Caso 2: $node["NombreNodo"].json.prop
            node_match = re.match(r'\$node\["([^"]+)"\]\.json\.(.+)', expr)
            if node_match:
                node_name = node_match.group(1)
                prop = node_match.group(2)
                if node_name in history and len(history[node_name]) > 0:
                    return str(history[node_name][0].json.get(prop, f"[Error: {prop} en {node_name} no encontrado]"))
                return f"[Error: Nodo {node_name} no ejecutado]"
                
            return match.group(0)

        return re.sub(r'\{\{(.*?)\}\}', replacer, template)

# ============================================================================
# HOOKS DE OBSERVABILIDAD (N8N WorkflowHooks)
# ============================================================================

class WorkflowHooks:
    @staticmethod
    def on_workflow_start(workflow_name: str):
        print(f"⚡ [NEXUS HOOK] Iniciando flujo: {workflow_name}")

    @staticmethod
    def on_node_before_execute(node_name: str):
        print(f"  ▶ [NEXUS HOOK] Ejecutando nodo: {node_name}...")

    @staticmethod
    def on_node_after_execute(node_name: str, item_count: int, duration_ms: float):
        print(f"  ✓ [NEXUS HOOK] Nodo '{node_name}' finalizado: {item_count} ítem(s) en {duration_ms:.2f}ms")

    @staticmethod
    def on_workflow_success(workflow_name: str, total_time: float):
        print(f"✅ [NEXUS HOOK] Flujo '{workflow_name}' completado con éxito en {total_time:.2f}s")

# ============================================================================
# CLASE BASE DE NODO NATIVO V2
# ============================================================================

class NexusNodeV2:
    def __init__(self, node_id: str, name: str, continue_on_fail: bool = False, max_retries: int = 1):
        self.node_id = node_id
        self.name = name
        self.continue_on_fail = continue_on_fail
        self.max_retries = max_retries
        self.parameters = {}

    async def execute(self, input_items: NodeDataItems, history: Dict[str, NodeDataItems]) -> NodeDataItems:
        raise NotImplementedError

# ============================================================================
# IMPLEMENTACIÓN DE NODOS NATIVOS V2 (REVERSED FROM N8N CORE)
# ============================================================================

class IngestURLNodeV2(NexusNodeV2):
    async def execute(self, input_items: NodeDataItems, history: Dict[str, NodeDataItems]) -> NodeDataItems:
        results = []
        for item in input_items:
            url = item.json.get("url", "https://es.wikipedia.org/wiki/Epistemologia")
            # Simular extracción de metadatos
            results.append(NodeExecutionItem({
                "title": "Análisis Estructural y Forense",
                "source_url": url,
                "author": "Analista Anónimo",
                "status": "INGESTED"
            }))
        return results

class ApoliticalGuardrailNodeV2(NexusNodeV2):
    async def execute(self, input_items: NodeDataItems, history: Dict[str, NodeDataItems]) -> NodeDataItems:
        results = []
        stopwords = ["progre", "woke", "facha", "machirulo"]
        for item in input_items:
            serialized = json.dumps(item.json).lower()
            for word in stopwords:
                if word in serialized:
                    raise ValueError(f"Término polarizante '{word}' detectado.")
            
            # Resolver expresión usando la sintaxis de N8N
            resolved_title = ExpressionEvaluator.resolve("ANÁLISIS NEUTRAL: {{ $json.title }}", item, history)
            
            results.append(NodeExecutionItem({
                "verified_title": resolved_title,
                "neutrality": "PASSED_STRICT"
            }))
        return results

class FXFlowSynthesisNodeV2(NexusNodeV2):
    async def execute(self, input_items: NodeDataItems, history: Dict[str, NodeDataItems]) -> NodeDataItems:
        results = []
        for item in input_items:
            # Obtener el título resuelto del nodo anterior usando la expresión de N8N
            title = ExpressionEvaluator.resolve('{{ $node["FiltroApolitico"].json.verified_title }}', item, history)
            
            results.append(NodeExecutionItem({
                "project_title": title,
                "evidences": [
                    {"id": "ev1", "type": "image", "src": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800"},
                    {"id": "ev2", "type": "image", "src": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800"}
                ]
            }))
        return results

class RemotionCompilerNodeV2(NexusNodeV2):
    async def execute(self, input_items: NodeDataItems, history: Dict[str, NodeDataItems]) -> NodeDataItems:
        results = []
        for item in input_items:
            output_mp4 = os.path.join(BASE_DIR, "remotion-composer", "out", "podcast_20min_max_exergy.mp4")
            results.append(NodeExecutionItem({
                "output_video_path": output_mp4,
                "frames": 36000,
                "status": "COMPILED"
            }))
        return results

# ============================================================================
# MOTOR DE EJECUCIÓN N8N REPLICADO (WorkflowExecute)
# ============================================================================

class NexusEngineV2:
    def __init__(self, workflow_name: str = "Nexus Pipeline"):
        self.workflow_name = workflow_name
        self.nodes: List[NexusNodeV2] = []
        self.node_history: Dict[str, NodeDataItems] = {}

    def add_node(self, node: NexusNodeV2):
        self.nodes.append(node)

    async def run(self, initial_items: NodeDataItems):
        WorkflowHooks.on_workflow_start(self.workflow_name)
        start_time = time.time()
        
        current_data = initial_items

        for node in self.nodes:
            WorkflowHooks.on_node_before_execute(node.name)
            node_start = time.time()
            
            executed_successfully = False
            last_error = None
            
            for attempt in range(1, node.max_retries + 1):
                try:
                    output_data = await node.execute(current_data, self.node_history)
                    self.node_history[node.name] = output_data
                    current_data = output_data
                    executed_successfully = True
                    break
                except Exception as e:
                    last_error = e
                    print(f"  ⚠️ Intento {attempt}/{node.max_retries} falló en nodo '{node.name}': {e}")
                    await asyncio.sleep(0.2)

            if not executed_successfully:
                if node.continue_on_fail:
                    print(f"  ⚠️ [ContinueOnFail] Ignorando error en nodo '{node.name}'...")
                    error_item = [NodeExecutionItem({"error": str(last_error), "failed_node": node.name})]
                    self.node_history[node.name] = error_item
                    current_data = error_item
                else:
                    print(f"❌ [ABORT] Fallo crítico en nodo '{node.name}': {last_error}")
                    sys.exit(1)

            duration_ms = (time.time() - node_start) * 1000
            WorkflowHooks.on_node_after_execute(node.name, len(current_data), duration_ms)

        total_time = time.time() - start_time
        WorkflowHooks.on_workflow_success(self.workflow_name, total_time)
        return current_data

# ============================================================================
# CLI DE DEMOSTRACIÓN V2
# ============================================================================

def main():
    print("="*60)
    print(" 🚀 EJECUTANDO NEXUS ENGINE V2.0 (REVERSED N8N CORE) 🚀")
    print("="*60)

    # Entradas iniciales tipo INodeExecutionData[]
    initial_items = [
        NodeExecutionItem({"url": "https://es.wikipedia.org/wiki/Epistemologia"})
    ]

    engine = NexusEngineV2("Pipeline de Producción Autónomo")
    
    # Grafo de nodos con nombres explícitos para expresiones
    n1 = IngestURLNodeV2("1", "Ingesta")
    n2 = ApoliticalGuardrailNodeV2("2", "FiltroApolitico", max_retries=2)
    n3 = FXFlowSynthesisNodeV2("3", "SintesisVisual")
    n4 = RemotionCompilerNodeV2("4", "CompiladorRemotion")
    
    engine.add_node(n1)
    engine.add_node(n2)
    engine.add_node(n3)
    engine.add_node(n4)

    final_output = asyncio.run(engine.run(initial_items))

    print("\n" + "="*60)
    print(" 📊 RESULTADO FINAL DEL GRAFO (INodeExecutionData[]):")
    print(json.dumps([item.to_dict() for item in final_output], indent=2, ensure_ascii=False))
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
