"""Contract tests for the Video Compiler IR.

These run with NO GPU and NO API keys (StubRenderer). They prove the spine is
real: a canonical script compiles to the staged IR, selects a runnable backend,
renders a content-addressed program, and the program validates against its
JSON schema. Run with: `pytest tests/contracts/test_video_compiler.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from videocompiler import (
    AssetRef,
    ContentHash,
    QualityTier,
    VideoCompiler,
    VideoCompilerIR,
)
from videocompiler.backends import StubRenderer, default_registry
from videocompiler.selector import BackendSelector, HardwareContext, select_backend

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "artifacts" / "video_program.schema.json"


SAMPLE_SCRIPT = {
    "version": "1.0",
    "title": "Why the Video Compiler Matters",
    "total_duration_seconds": 30.0,
    "sections": [
        {
            "id": "s1",
            "text": "Most pipelines hardcode one video API.",
            "start_seconds": 0.0,
            "end_seconds": 10.0,
            "delivery_cues": {"pace": "conversational", "energy": "high"},
            "enhancement_cues": [{"type": "diagram", "description": "pipeline vs compiler"}],
        },
        {
            "id": "s2",
            "text": "A compiler IR makes every backend swappable.",
            "start_seconds": 10.0,
            "end_seconds": 20.0,
            "delivery_cues": {"pace": "brisk", "energy": "high"},
            "enhancement_cues": [{"type": "stat_card", "description": "8 backends"}],
        },
        {
            "id": "s3",
            "text": "Now the model is just a backend target.",
            "start_seconds": 20.0,
            "end_seconds": 30.0,
            "delivery_cues": {"pace": "measured", "energy": "calm"},
        },
    ],
}


def test_ir_lowering_produces_all_stages():
    ir = VideoCompiler().compile_ir(SAMPLE_SCRIPT)
    assert isinstance(ir, VideoCompilerIR)
    assert ir.narrative is not None
    assert ir.emotion is not None and ir.emotion.beats
    assert ir.attention is not None and ir.attention.points
    assert ir.scenes is not None and len(ir.scenes.nodes) == 3
    assert ir.shots is not None and ir.shots.nodes
    assert ir.timeline is not None and ir.timeline.duration_seconds == 30.0
    # Every sub-graph is content-addressed.
    assert ir.narrative.content_hash
    assert ir.shots.content_hash
    assert ir.timeline.content_hash
    assert ir.content_hash


def test_lowering_is_deterministic():
    a = VideoCompiler().compile_ir(SAMPLE_SCRIPT)
    b = VideoCompiler().compile_ir(SAMPLE_SCRIPT)
    assert a.content_hash == b.content_hash
    assert a.model_dump_json() == b.model_dump_json()


def test_render_graph_is_content_addressed():
    compiler = VideoCompiler()
    ir = compiler.compile_ir(SAMPLE_SCRIPT)
    rg = compiler.build_render_graph(ir)
    refs = [n.asset_ref for n in rg.nodes]
    # Same generation contract -> same content-addressed asset (caching feature,
    # enables incremental rendering / A/B substitution). So refs can repeat.
    contracts = [tuple(sorted(n.params.items())) for n in rg.nodes]
    assert refs == [ContentHash.from_obj(dict(c)).digest for c in contracts]
    # Stability across runs.
    rg2 = compiler.build_render_graph(ir)
    assert [n.asset_ref for n in rg2.nodes] == refs


def test_stub_backend_renders_without_gpu_or_keys(tmp_path):
    compiler = VideoCompiler(hardware=HardwareContext())  # CPU only, no keys
    ir = compiler.compile_ir(SAMPLE_SCRIPT)
    rg = compiler.build_render_graph(ir)
    program = compiler.render(ir, rg, backend_id="stub", out_dir=tmp_path)
    assert program.backend_id == "stub"
    assert len(program.render_nodes) == len(rg.nodes)
    assert len(program.assets) == len(rg.nodes)
    assert all(isinstance(a, AssetRef) for a in program.assets)
    assert program.content_hash
    # The honest default wrote real, inspectable placeholder artifacts.
    stub_files = list(tmp_path.glob("*.stub.mp4"))
    assert len(stub_files) == len(rg.nodes)
    first = json.loads(stub_files[0].read_text())
    assert first["placeholder"] is True
    assert first["backend"] == "stub"


def test_selector_prefers_stub_on_cpu_no_keys():
    reg = default_registry()
    sel = select_backend(reg, tags={"motion": 0.9, "local": 1.0}, hardware=HardwareContext())
    # On CPU with no keys, only the stub is runnable -> must be selected.
    assert sel.backend_id == "stub"
    assert sel.score > 0


def test_selector_fails_over_to_gpu_backend_when_hardware_present():
    reg = default_registry()
    hw = HardwareContext(gpu_vram_mb=24 * 1024)  # 24GB GPU, no API keys
    sel = select_backend(reg, tags={"motion": 0.9}, quality=QualityTier.HIGH, hardware=hw)
    # Commercial (API_KEY) backends excluded; a local GPU backend should win.
    assert sel.backend_id in {"wan", "ltx_local", "hunyuan", "cogvideo"}
    assert sel.backend_id != "stub"


def test_commercial_backend_excluded_without_api_key():
    reg = default_registry()
    sel = select_backend(reg, hardware=HardwareContext(gpu_vram_mb=0))
    assert sel.backend_id != "runway"
    assert sel.backend_id != "veo"


def test_available_respects_hardware():
    reg = default_registry()
    # CPU, no keys: only stub (GPU/commercial backends are not runnable here).
    avail_cpu = reg.available(HardwareContext(gpu_vram_mb=0))
    assert avail_cpu == ["stub"]
    # 24GB GPU, no keys: local GPU backends become runnable.
    avail_gpu = reg.available(HardwareContext(gpu_vram_mb=24 * 1024))
    assert "wan" in avail_gpu
    assert "stub" in avail_gpu
    assert "runway" not in avail_gpu  # still needs an API key


def test_video_program_validates_against_schema():
    compiler = VideoCompiler()
    ir = compiler.compile_ir(SAMPLE_SCRIPT)
    rg = compiler.build_render_graph(ir)
    program = compiler.render(ir, rg, backend_id="stub", out_dir="out/video_compiler")
    schema = json.loads(SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(json.loads(program.model_dump_json())))
    assert not errors, f"Schema violations: {errors}"


def test_full_run_persists_artifacts(tmp_path):
    compiler = VideoCompiler()
    ir, rg, program = compiler.run(
        SAMPLE_SCRIPT, backend_id="stub", out_dir=tmp_path, persist=True
    )
    assert (tmp_path / "ir.json").is_file()
    assert (tmp_path / "render_graph.json").is_file()
    assert (tmp_path / "video_program.json").is_file()
    assert program.backend_id == "stub"


def test_content_hash_helper_stable():
    obj = {"a": 1, "b": [1, 2, 3]}
    assert ContentHash.from_obj(obj).digest == ContentHash.from_obj(obj).digest
    # Order independence.
    assert ContentHash.from_obj({"x": 1, "y": 2}).digest == ContentHash.from_obj({"y": 2, "x": 1}).digest
