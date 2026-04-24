"""
Tests for the BenchClaw LlamaIndex adapter.

Run:
    pip install llama-index-core httpx pytest
    pytest llamaindex/tests/ -v
"""
from __future__ import annotations

import os
import pytest
import httpx

API_BASE = os.getenv(
    "BENCHCLAW_API_BASE",
    "https://p2pclaw-mcp-server-production-ac1c.up.railway.app",
)


def api_reachable() -> bool:
    try:
        r = httpx.get(f"{API_BASE}/leaderboard", timeout=10)
        return r.status_code < 500
    except Exception:
        return False


skip_if_offline = pytest.mark.skipif(
    not api_reachable(),
    reason="BenchClaw API not reachable",
)


def test_imports():
    from benchclaw_llamaindex import BenchClawToolSpec  # noqa: F401


def test_spec_functions():
    from benchclaw_llamaindex import BenchClawToolSpec

    spec = BenchClawToolSpec()
    assert "register" in spec.spec_functions
    assert "submit_paper" in spec.spec_functions
    assert "leaderboard" in spec.spec_functions


def test_to_tool_list():
    from benchclaw_llamaindex import BenchClawToolSpec
    from llama_index.core.tools import FunctionTool

    tools = BenchClawToolSpec().to_tool_list()
    assert len(tools) == 3
    for t in tools:
        assert isinstance(t, FunctionTool)


@skip_if_offline
def test_register():
    from benchclaw_llamaindex import BenchClawToolSpec

    spec = BenchClawToolSpec()
    result = spec.register(llm="test-model-llamaindex", agent="pytest-llamaindex")
    assert isinstance(result, dict)
    agent_id = result.get("agentId") or result.get("agent_id") or result.get("id")
    assert agent_id is not None, f"No agentId in: {result}"


@skip_if_offline
def test_leaderboard():
    from benchclaw_llamaindex import BenchClawToolSpec

    spec = BenchClawToolSpec()
    result = spec.leaderboard()
    assert isinstance(result, list)
