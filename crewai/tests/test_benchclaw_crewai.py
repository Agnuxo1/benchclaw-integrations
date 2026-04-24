"""
Tests for the BenchClaw CrewAI adapter.

Run:
    pip install crewai httpx pytest
    pytest crewai/tests/ -v
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
    from benchclaw_crewai import (  # noqa: F401
        BenchClawRegisterTool,
        BenchClawSubmitPaperTool,
        BenchClawLeaderboardTool,
    )


def test_tool_names():
    from benchclaw_crewai import BenchClawRegisterTool, BenchClawSubmitPaperTool, BenchClawLeaderboardTool

    assert BenchClawRegisterTool().name == "BenchClaw Register"
    assert BenchClawSubmitPaperTool().name == "BenchClaw Submit Paper"
    assert BenchClawLeaderboardTool().name == "BenchClaw Leaderboard"


def test_schemas_present():
    from benchclaw_crewai import BenchClawRegisterTool, BenchClawSubmitPaperTool

    assert BenchClawRegisterTool().args_schema is not None
    assert BenchClawSubmitPaperTool().args_schema is not None


@skip_if_offline
def test_register_returns_agent_id():
    from benchclaw_crewai import BenchClawRegisterTool

    tool = BenchClawRegisterTool()
    result = tool._run(llm="test-model-crewai", agent="pytest-crewai")
    assert isinstance(result, dict)
    agent_id = result.get("agentId") or result.get("agent_id") or result.get("id")
    assert agent_id is not None, f"No agentId in: {result}"


@skip_if_offline
def test_leaderboard():
    from benchclaw_crewai import BenchClawLeaderboardTool

    tool = BenchClawLeaderboardTool()
    result = tool._run()
    assert isinstance(result, list)
