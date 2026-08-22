"""Cross-file contracts for the optional Xquik research source."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_layer_three_skill_is_identical_for_supported_agent_layouts() -> None:
    agents_skill = _read(".agents/skills/xquik-social-research/SKILL.md")
    claude_skill = _read(".claude/skills/xquik-social-research/SKILL.md")
    assert agents_skill == claude_skill
    assert "Use for Twitter search" in agents_skill
    assert "Keep public reads bounded" in agents_skill
    assert "Require explicit approval before private reads" in agents_skill
    assert "25 results or fewer" in agents_skill
    assert "anecdotal audience evidence" in agents_skill
    assert "primary source" in agents_skill


def test_research_first_pipelines_expose_xquik_as_an_optional_source() -> None:
    for manifest in (
        "pipeline_defs/animated-explainer.yaml",
        "pipeline_defs/animation.yaml",
        "pipeline_defs/cinematic.yaml",
    ):
        assert "xquik_social_research" in _read(manifest)


def test_research_directors_route_through_shared_skill() -> None:
    for director in (
        "skills/pipelines/explainer/research-director.md",
        "skills/pipelines/animation/research-director.md",
        "skills/pipelines/cinematic/research-director.md",
    ):
        text = _read(director)
        assert "xquik_social_research" in text
        assert "xquik-social-research" in text
        assert "bounded-search and evidence rules" in text
