"""Contract tests for the Balamonis Creator workspace."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest


SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "creator"
    / "workspace.schema.json"
)


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def _minimal_workspace() -> dict:
    return {
        "version": "1.0",
        "workspace_id": "founding-original",
        "title": "Founding Original",
        "business_layer": "originals",
        "status": "proposal",
        "brief": {
            "goal": "Create a rights-ready short film.",
            "audience": "Global film audiences",
            "master_format": "1920x1080 master",
            "rights_goal": "Worldwide buyer review",
        },
        "story_bible": {
            "logline": "A memory needs a human carrier.",
            "theme": "Presence",
            "characters": [],
            "locations": [],
            "continuity_rules": [],
        },
        "scenes": [],
        "assets": [],
        "approvals": [],
        "rights_records": [],
        "authorship_journal": [],
        "deliveries": [],
        "metrics": {
            "estimated_spend_usd": 0,
            "actual_spend_usd": 0,
            "generated_seconds": 0,
            "approved_seconds": 0,
        },
    }


def test_creator_workspace_schema_is_valid() -> None:
    jsonschema.Draft202012Validator.check_schema(_schema())


def test_minimal_creator_workspace_validates() -> None:
    jsonschema.Draft202012Validator(_schema()).validate(_minimal_workspace())


def test_creator_workspace_rejects_untracked_business_layer() -> None:
    workspace = _minimal_workspace()
    workspace["business_layer"] = "ott"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_schema()).validate(workspace)
