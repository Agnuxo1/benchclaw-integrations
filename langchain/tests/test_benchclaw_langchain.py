"""
Tests for the BenchClaw LangChain adapter.

These tests hit the real Railway API — they require a live network connection.
Set BENCHCLAW_API_BASE to override (e.g. a local mock server).

Run:
    pip install langchain-core httpx pytest
    pytest langchain/tests/ -v
"""
from __future__ import annotations

import os
import pytest
import httpx

API_BASE = os.getenv(
    "BENCHCLAW_API_BASE",
    "https://p2pclaw-mcp-server-production-ac1c.up.railway.app",
)


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

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


# --------------------------------------------------------------------------- #
# Import smoke test (no network)                                               #
# --------------------------------------------------------------------------- #

def test_imports():
    from benchclaw_langchain import (  # noqa: F401
        BenchClawRegister,
        BenchClawSubmitPaper,
        BenchClawLeaderboard,
        API_BASE as _API_BASE,
    )
    assert _API_BASE.startswith("http")


def test_tool_names():
    from benchclaw_langchain import BenchClawRegister, BenchClawSubmitPaper, BenchClawLeaderboard

    assert BenchClawRegister().name == "benchclaw_register"
    assert BenchClawSubmitPaper().name == "benchclaw_submit_paper"
    assert BenchClawLeaderboard().name == "benchclaw_leaderboard"


def test_schemas_valid():
    from benchclaw_langchain import BenchClawRegister, BenchClawSubmitPaper

    reg = BenchClawRegister()
    assert reg.args_schema is not None

    sub = BenchClawSubmitPaper()
    assert sub.args_schema is not None


# --------------------------------------------------------------------------- #
# Integration tests (live API)                                                 #
# --------------------------------------------------------------------------- #

@skip_if_offline
def test_register_returns_agent_id():
    from benchclaw_langchain import BenchClawRegister

    tool = BenchClawRegister()
    result = tool.invoke({
        "llm": "test-model-lc",
        "agent": "pytest-langchain",
        "client": "benchclaw-langchain-test",
    })
    assert isinstance(result, dict), f"Expected dict, got {type(result)}: {result}"
    # API may return agentId or agent_id depending on version
    agent_id = result.get("agentId") or result.get("agent_id") or result.get("id")
    assert agent_id is not None, f"No agentId in response: {result}"


@skip_if_offline
def test_leaderboard_returns_list():
    from benchclaw_langchain import BenchClawLeaderboard

    tool = BenchClawLeaderboard()
    result = tool.invoke({})
    assert isinstance(result, list), f"Expected list, got {type(result)}: {result}"


@skip_if_offline
def test_submit_draft_paper():
    """Draft papers have a lower word count requirement (150 words)."""
    from benchclaw_langchain import BenchClawSubmitPaper

    # First register to get a valid agentId
    reg_r = httpx.post(
        f"{API_BASE}/quick-join",
        json={"llm": "test-model-lc", "agent": "pytest-langchain"},
        timeout=15,
    )
    reg_r.raise_for_status()
    agent_id = reg_r.json().get("agentId") or reg_r.json().get("id")

    tool = BenchClawSubmitPaper()
    # Build a draft paper with >150 words
    content = (
        "# Test Paper\n\n"
        + ("This is a test paper submitted by the benchclaw-langchain pytest suite. " * 15)
    )
    result = tool.invoke({
        "agent_id": agent_id,
        "title": "LangChain Integration Test Paper",
        "content": content,
        "draft": True,
    })
    assert isinstance(result, dict), f"Expected dict, got {type(result)}: {result}"
