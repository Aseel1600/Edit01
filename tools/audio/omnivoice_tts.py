"""OmniVoice local voice cloning and prompt-based voice design tool.

Wraps k2-fsa/OmniVoice with voice-cloning support (via reference audio)
and voice design (via instruct prompt), utilizing local GPU (CUDA/MPS) or CPU.
"""

from __future__ import annotations

import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)
from tools.audio.vietnamese_text_formatter import format_for_voice
from tools.audio.edge_tts import EdgeTTS


class OmniVoiceTTS(BaseTool):
    name = "omnivoice_tts"
    version = "1.0.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "omnivoice"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL

    dependencies = []
    install_instructions = (
        "Clone OmniVoice repository:\n"
        "  git clone https://github.com/k2-fsa/OmniVoice tools/OmniVoice\n"
        "  pip install -r tools/OmniVoice/requirements.txt\n"
    )
    agent_skills = ["text-to-speech"]
    fallback = "edge_tts"
    fallback_tools = ["edge_tts", "piper_tts", "elevenlabs_tts"]

    capabilities = [
        "text_to_speech",
        "voice_cloning",
        "voice_design",
        "multilingual",
        "local_gpu_acceleration",
    ]
    supports = {
        "voice_cloning": True,
        "multilingual": True,
        "offline": True,
        "native_audio": True,
    }
    best_for = [
        "local GPU Vietnamese voice cloning from reference audio",
        "zero-cost offline voice cloning without cloud API subscriptions",
        "custom emotion and pitch guidance with voice design prompts",
    ]
    not_good_for = [
        "low-spec machines without GPU where ultra-fast inference is needed (use edge_tts)",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to synthesize"},
            "language": {
                "type": "string",
                "default": "vi",
                "description": "Language code (e.g. vi, en, zh)",
            },
            "ref_audio_path": {
                "type": "string",
                "description": "Path to reference audio file for voice cloning (wav/mp3)",
            },
            "ref_text": {
                "type": "string",
                "description": "Transcript of the reference audio for higher cloning fidelity",
            },
            "voice_instruct": {
                "type": "string",
                "description": "Voice design instructions (e.g. 'male, low pitch', 'female, cheerful')",
            },
            "voice_id": {
                "type": "string",
                "default": "nam-dao-ly",
                "description": "Pre-configured voice ID located in voices/<voice_id>/ (e.g. nam-dao-ly, nu-doc-truyen)",
            },
            "speed": {
                "type": "number",
                "default": 1.0,
                "description": "Playback speed factor",
            },
            "output_path": {
                "type": "string",
                "description": "Path to output generated audio file",
            },
            "format_vietnamese": {
                "type": "boolean",
                "default": True,
                "description": "Whether to format numbers/units into Vietnamese words",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=4096, vram_mb=4096, disk_mb=2000, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=[])
    idempotency_key_fields = ["text", "ref_audio_path", "voice_instruct", "voice_id", "speed"]
    side_effects = ["writes audio file to output_path"]
    user_visible_verification = ["Play generated audio file to verify voice cloning fidelity and clarity"]

    def _get_omnivoice_dir(self) -> pathlib.Path:
        env_dir = os.environ.get("OMNIVOICE_DIR")
        if env_dir and pathlib.Path(env_dir).exists():
            return pathlib.Path(env_dir).resolve()

        root = pathlib.Path(__file__).resolve().parent.parent.parent
        candidates = [
            root / "tools" / "OmniVoice",
            root / "lib" / "OmniVoice",
            pathlib.Path.home() / ".openmontage" / "OmniVoice",
            pathlib.Path.home() / ".local" / "share" / "OmniVoice",
        ]
        for c in candidates:
            if c.exists() and (c / "omnivoice").exists():
                return c.resolve()
        return (root / "tools" / "OmniVoice").resolve()

    def _get_python_executable(self) -> str:
        env_py = os.environ.get("OMNIVOICE_PYTHON")
        if env_py and pathlib.Path(env_py).exists() and os.access(env_py, os.X_OK):
            return env_py

        candidates = [
            pathlib.Path("/Users/huutq/Desktop/WorkingSpace/Taka/taka-tales/env/bin/python"),
            pathlib.Path(sys.executable),
            pathlib.Path(".venv/bin/python"),
            pathlib.Path("env/bin/python"),
        ]
        for c in candidates:
            if c.exists() and os.access(c, os.X_OK):
                return str(c)
        return sys.executable

    def get_status(self) -> ToolStatus:
        omni_dir = self._get_omnivoice_dir()
        if omni_dir.exists():
            return ToolStatus.AVAILABLE
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        t0 = time.time()
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(
                success=False,
                error="Parameter 'text' is required and must not be empty.",
                duration_seconds=time.time() - t0,
            )

        language = inputs.get("language", "vi").lower()
        if inputs.get("format_vietnamese", True):
            text = format_for_voice(text, language=language)

        output_path_str = inputs.get("output_path")
        if output_path_str:
            out_path = pathlib.Path(output_path_str).resolve()
        else:
            out_path = (pathlib.Path("scratch") / f"omnivoice_{int(time.time() * 1000)}.wav").resolve()

        out_path.parent.mkdir(parents=True, exist_ok=True)

        omni_dir = self._get_omnivoice_dir()
        python_exe = self._get_python_executable()

        if not omni_dir.exists():
            print(f"[OmniVoiceTTS] OmniVoice repo not found at {omni_dir}. Falling back to Edge-TTS...")
            edge_tool = EdgeTTS()
            return edge_tool.execute({
                **inputs,
                "text": text,
                "language": language,
                "output_path": str(out_path.with_suffix(".mp3")),
                "format_vietnamese": False,
            })

        # Resolve voice clone audio
        ref_audio_path = inputs.get("ref_audio_path")
        ref_text = inputs.get("ref_text")
        voice_id = inputs.get("voice_id") or "nam-dao-ly"
        voice_instruct = inputs.get("voice_instruct")
        speed = inputs.get("speed", 1.0)

        root = pathlib.Path(__file__).resolve().parent.parent.parent
        if not ref_audio_path and voice_id:
            search_dirs = [
                root / "voices" / voice_id,
                pathlib.Path.home() / ".openmontage" / "voices" / voice_id,
            ]
            if os.environ.get("VOICES_DIR"):
                search_dirs.insert(0, pathlib.Path(os.environ["VOICES_DIR"]) / voice_id)

            for vdir in search_dirs:
                if vdir.exists():
                    for ext in [".mp3", ".wav", ".flac", ".m4a"]:
                        cand = vdir / f"ref{ext}"
                        if cand.exists() and cand.stat().st_size > 0:
                            ref_audio_path = str(cand.resolve())
                            break
                    if not ref_text:
                        for txt_file in [vdir / "ref.txt", vdir / "ref_text.txt"]:
                            if txt_file.exists():
                                ref_text = txt_file.read_text(encoding="utf-8").strip().replace("\n", " ")
                                break
                if ref_audio_path:
                    break

        # Split multi-sentence text to prevent OmniVoice duration truncation
        import re
        sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text) if s.strip()]
        if not sentences:
            sentences = [text]

        sub_env = os.environ.copy()
        sub_env["PYTHONPATH"] = str(omni_dir)

        if len(sentences) == 1:
            cmd = [
                python_exe,
                "-m", "omnivoice.cli.infer",
                "--model", "k2-fsa/OmniVoice",
                "--text", sentences[0],
                "--language", language,
                "--output", str(out_path),
            ]
            if ref_audio_path:
                cmd += ["--ref_audio", str(ref_audio_path)]
                if ref_text:
                    cmd += ["--ref_text", str(ref_text)]
            elif voice_instruct:
                cmd += ["--instruct", str(voice_instruct)]
            if speed != 1.0:
                cmd += ["--speed", str(speed)]

            try:
                print(f"[OmniVoiceTTS] Running CLI: {' '.join(cmd)}")
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    env=sub_env,
                    cwd=str(omni_dir),
                    timeout=180,
                )
            except Exception as e:
                print(f"[OmniVoiceTTS] Execution failed: {e}. Falling back to Edge-TTS...")
                edge_tool = EdgeTTS()
                return edge_tool.execute({
                    **inputs,
                    "text": text,
                    "language": language,
                    "output_path": str(out_path.with_suffix(".mp3")),
                    "format_vietnamese": False,
                })
        else:
            temp_dir = out_path.parent / f"_omni_temp_{int(time.time()*1000)}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            part_files = []
            try:
                for idx, sent in enumerate(sentences):
                    part_wav = temp_dir / f"part_{idx:03d}.wav"
                    cmd = [
                        python_exe,
                        "-m", "omnivoice.cli.infer",
                        "--model", "k2-fsa/OmniVoice",
                        "--text", sent,
                        "--language", language,
                        "--output", str(part_wav),
                    ]
                    if ref_audio_path:
                        cmd += ["--ref_audio", str(ref_audio_path)]
                        if ref_text:
                            cmd += ["--ref_text", str(ref_text)]
                    elif voice_instruct:
                        cmd += ["--instruct", str(voice_instruct)]
                    if speed != 1.0:
                        cmd += ["--speed", str(speed)]

                    print(f"[OmniVoiceTTS] Synthesizing sentence [{idx+1}/{len(sentences)}]: {sent}")
                    subprocess.run(
                        cmd,
                        check=True,
                        capture_output=True,
                        text=True,
                        env=sub_env,
                        cwd=str(omni_dir),
                        timeout=180,
                    )
                    if part_wav.exists() and part_wav.stat().st_size > 0:
                        part_files.append(part_wav)

                if not part_files:
                    raise RuntimeError("No audio chunks generated by OmniVoice.")

                # Concatenate with FFmpeg
                concat_list = temp_dir / "concat.txt"
                with open(concat_list, "w", encoding="utf-8") as f:
                    for pf in part_files:
                        f.write(f"file '{pf.resolve()}'\n")

                ext = out_path.suffix.lower()
                c_args = ["-c:a", "libmp3lame", "-q:a", "2"] if ext == ".mp3" else ["-c:a", "pcm_s16le"]
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), *c_args, str(out_path)],
                    check=True,
                    capture_output=True,
                )
                file_size = out_path.stat().st_size if out_path.exists() else 0
                return ToolResult(
                    success=True,
                    data={
                        "output_path": str(out_path),
                        "file_size_bytes": file_size,
                        "ref_audio_path": ref_audio_path,
                        "voice_instruct": voice_instruct,
                        "character_count": len(text),
                        "sentence_count": len(sentences),
                        "formatted_text": text,
                    },
                    artifacts=[str(out_path)],
                    cost_usd=0.0,
                    duration_seconds=time.time() - t0,
                )
            except Exception as e:
                print(f"[OmniVoiceTTS] Chunked execution failed: {e}. Falling back to Edge-TTS...")
                edge_tool = EdgeTTS()
                return edge_tool.execute({
                    **inputs,
                    "text": text,
                    "language": language,
                    "output_path": str(out_path.with_suffix(".mp3")),
                    "format_vietnamese": False,
                })
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
