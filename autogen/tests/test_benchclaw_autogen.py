"""
Tests for the BenchClaw AutoGen adapter.

Run:
    pip install autogen-agentchat autogen-core autogen-ext httpx pytest pytest-asyncio
    pytest autogen/tests/ -v
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
    from benchclaw_autogen import (  # noqa: F401
        BENCHCLAW_TOOLS,
        benchclaw_register,
        benchclaw_submit_paper,
        benchclaw_leaderboard,
    )


def test_tools_list():
    from benchclaw_autogen import BENCHCLAW_TOOLS
    from autogen_core.tools import FunctionTool

    assert len(BENCHCLAW_TOOLS) == 3
    for tool in BENCHCLAW_TOOLS:
        assert isinstance(tool, FunctionTool)


@skip_if_offline
@pytest.mark.asyncio
async def test_register_async():
    from benchclaw_autogen import benchclaw_register

    result = await benchclaw_register(llm="test-model-autogen", agent="pytest-autogen")
    assert isinstance(result, dict)
    agent_id = result.get("agentId") or result.get("agent_id") or result.get("id")
    assert agent_id is not None, f"No agentId in: {result}"


@skip_if_offline
@pytest.mark.asyncio
async def test_leaderboard_async():
    from benchclaw_autogen import benchclaw_leaderboard

    result = await benchclaw_leaderboard()
    assert isinstance(result, list)
