"""Runners drive a job through the pipeline gates.

A runner advances a job to its NEXT human-approval gate, then stops. Each HTTP call
(start / respond) moves the job forward one leg. This mirrors how the real agent works:
it runs until a checkpoint writes `awaiting_human`, then pauses for Dify.

Two runners:
  - MockRunner        : no LLM, no Higgsfield. Fakes script + storyboard, and REALLY renders
                        a clean master from the approved stills via panda_render. Lets us test
                        the whole Dify handshake + local storage + gates here, with no EC2.
  - ClaudeCodeRunner  : the EC2 path — invokes Claude Code headless against the engine repo.
                        Skeleton only; swap it in where the box has `claude` + OpenRouter + MCP.

Gate sequence (matches pipeline_defs/panda-video.yaml):
    start ─▶ GATE 1 approve_script ─▶ GATE 2 approve_storyboard ─▶ GATE 3 approve_final ─▶ done
Branding is NOT a gate — it's a separate on-demand step after approve_final.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from dify_launcher import store

_ENGINE_ROOT = Path(__file__).resolve().parents[1]

# gate -> the stage the agent pauses AFTER producing that stage's artifact
GATES = ["approve_script", "approve_storyboard", "approve_final"]


class Runner:
    """Interface. advance() takes the job state + an optional human response and returns
    the updated state, stopping at the next gate (or done)."""

    def start(self, state: dict[str, Any]) -> dict[str, Any]:  # noqa: D401
        raise NotImplementedError

    def resume(self, state: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# MockRunner — testable end to end with no LLM / no Higgsfield
# ---------------------------------------------------------------------------

class MockRunner(Runner):
    def start(self, state: dict[str, Any]) -> dict[str, Any]:
        job_id = state["job_id"]
        brief = state.get("brief", "")
        # GATE 1: produce a (fake) script from the brief
        script = (
            f"# Script (mock)\n\n**Brief:** {brief}\n\n"
            "1. Open on the Panda mascot.\n2. Explain the tip.\n3. CTA.\n"
        )
        store.artifact_path(job_id, "script.md").write_text(script, encoding="utf-8")
        state.update(
            stage="script", status="awaiting_human", gate="approve_script",
            question="Approve the script, or request a revision.",
            artifacts={"script": "script.md"},
        )
        return state

    def resume(self, state: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        job_id = state["job_id"]
        decision = (response or {}).get("decision", "approve")
        gate = state.get("gate")

        # A revision re-runs the current stage and stops at the same gate.
        if decision == "revise":
            state["question"] = f"Revised {state['stage']} per: {response.get('answer','(no note)')}"
            return state

        if gate == "approve_script":
            return self._do_storyboard(state, response)
        if gate == "approve_storyboard":
            return self._do_production(state, response)
        if gate == "approve_final":
            state.update(status="done", gate=None, question=None)
            return state
        raise ValueError(f"cannot resume from gate {gate!r}")

    # --- GATE 2: storyboard stills -----------------------------------------
    def _do_storyboard(self, state: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        job_id = state["job_id"]
        provided = (response or {}).get("stills") or []
        stills: list[str] = []
        if provided:
            # Dify may hand us the stills directly (user-supplied storyboard).
            for i, src in enumerate(provided):
                p = Path(src)
                if p.is_file():
                    dst = store.artifact_path(job_id, f"still_{i:02d}{p.suffix or '.png'}")
                    dst.write_bytes(p.read_bytes())
                    stills.append(dst.name)
        if not stills:
            # else generate placeholder stills so the flow is self-contained
            stills = self._placeholder_stills(job_id, n=3)
        state.update(
            stage="scene_plan", status="awaiting_human", gate="approve_storyboard",
            question="Approve the storyboard stills, or request a revision.",
            artifacts={**state.get("artifacts", {}), "stills": stills},
        )
        return state

    # --- assets/edit/compose (no gates) -> GATE 3 clean master -------------
    def _do_production(self, state: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        job_id = state["job_id"]
        stills = state.get("artifacts", {}).get("stills", [])
        scene_paths = [str(store.artifact_path(job_id, s)) for s in stills] or \
            [self._placeholder_stills(job_id, 2)[0]]

        out = store.artifact_path(job_id, "final.mp4")
        self._render_clean(scene_paths, str(out))

        state.update(
            stage="compose", status="awaiting_human", gate="approve_final",
            question="Approve the finished (unbranded) video, or request a revision. "
                     "Branding can be added on request after approval.",
            artifacts={**state.get("artifacts", {}), "final": "final.mp4", "branded": False},
        )
        return state

    # --- helpers -----------------------------------------------------------
    def _placeholder_stills(self, job_id: str, n: int) -> list[str]:
        from PIL import Image, ImageDraw
        names = []
        colors = [(11, 11, 11), (253, 197, 13), (30, 30, 30)]
        for i in range(n):
            img = Image.new("RGB", (1080, 1920), colors[i % len(colors)])
            d = ImageDraw.Draw(img)
            d.text((60, 900), f"Scene {i+1}", fill=(255, 255, 255))
            p = store.artifact_path(job_id, f"still_{i:02d}.png")
            img.save(p)
            names.append(p.name)
        return names

    def _render_clean(self, scene_paths: list[str], out_path: str) -> None:
        """Real render via the folded panda_render tool (clean/ugc, no branding)."""
        if str(_ENGINE_ROOT) not in sys.path:
            sys.path.insert(0, str(_ENGINE_ROOT))
        from tools.video.panda_render import PandaRender
        res = PandaRender().execute({
            "scenes": [{"media_path": p, "duration_s": 2.5} for p in scene_paths],
            "fps": 30, "grade": "none",
            "output_path": out_path,
        })
        if not res.success:
            raise RuntimeError(f"panda_render failed: {getattr(res, 'error', '?')}")


# ---------------------------------------------------------------------------
# ClaudeCodeRunner — the EC2 path (skeleton)
# ---------------------------------------------------------------------------

class ClaudeCodeRunner(Runner):
    """Drives the REAL agent on the box. Not runnable here (no `claude` CLI, no LLM).

    Intended behavior on EC2:
      start():  launch `claude -p "<brief>"` headless in the engine repo with the
                panda-video pipeline, pointed at OpenRouter (ANTHROPIC_BASE_URL) and the
                Higgsfield MCP. Run in the BACKGROUND (long job). When the agent's
                checkpoint hits status=awaiting_human, read the checkpoint + artifacts and
                mirror them into this job's local store; return awaiting_human + gate.
      resume(): write the human decision/answer/stills into the checkpoint, then relaunch
                `claude -p --resume <checkpoint>` so the agent continues to the next gate.

    The checkpoint files live under the engine's lib/checkpoint state; this runner is the
    adapter between that and the launcher's job store. Fill in when deploying.
    """

    def start(self, state: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(
            "ClaudeCodeRunner is the EC2 path. Set DIFY_RUNNER=mock to test locally. "
            "On the box, wire this to `claude -p` headless + checkpoint mirroring."
        )

    def resume(self, state: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


def get_runner(name: str) -> Runner:
    return {"mock": MockRunner, "claude": ClaudeCodeRunner}.get(name, MockRunner)()
