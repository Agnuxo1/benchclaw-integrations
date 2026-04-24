"""
Tests for the BenchClaw OpenAI Agents SDK adapter.

Run:
    pip install openai-agents pytest
    pytest openai-agents/tests/ -v
"""
from __future__ import annotations

import json
import os
import pytest

API_BASE = os.getenv(
    "BENCHCLAW_API_BASE",
    "https://p2pclaw-mcp-server-production-ac1c.up.railway.app",
)


def api_reachable() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(f"{API_BASE}/leaderboard", timeout=10)
        return True
    except Exception:
        return False


skip_if_offline = pytest.mark.skipif(
    not api_reachable(),
    reason="BenchClaw API not reachable",
)


def test_imports():
    from benchclaw_tools import (  # noqa: F401
        BENCHCLAW_TOOLS,
        benchclaw_register,
        benchclaw_submit_paper,
        benchclaw_leaderboard,
    )


def test_tools_count():
    from benchclaw_tools import BENCHCLAW_TOOLS
    assert len(BENCHCLAW_TOOLS) == 3


@skip_if_offline
def test_register_live():
    from benchclaw_tools import _post

    result = _post("/quick-join", {"llm": "test-model-oai", "agent": "pytest-oai-agents"})
    assert isinstance(result, dict)
    agent_id = result.get("agentId") or result.get("agent_id") or result.get("id")
    assert agent_id is not None, f"No agentId in: {result}"


@skip_if_offline
def test_leaderboard_live():
    from benchclaw_tools import _get

    result = _get("/leaderboard?limit=5")
    assert isinstance(result, (list, dict))
