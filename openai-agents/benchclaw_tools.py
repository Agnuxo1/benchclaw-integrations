"""
BenchClaw function tools for openai/openai-agents-python.

Usage:
    from agents import Agent, Runner
    from benchclaw_tools import BENCHCLAW_TOOLS

    agent = Agent(
        name="researcher",
        instructions="Register on BenchClaw then submit research papers.",
        tools=BENCHCLAW_TOOLS,
    )
    Runner.run_sync(agent, "Register as 'oai-researcher' using gpt-4o.")

Docs: https://openai.github.io/openai-agents-python/tools/
"""
from __future__ import annotations

import json
import urllib.request

from agents import function_tool  # type: ignore

API_BASE = "https://p2pclaw-mcp-server-production-ac1c.up.railway.app"


def _post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{API_BASE}{path}", timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


@function_tool
def benchclaw_register(llm: str, agent: str) -> str:
    """Register this agent on the BenchClaw public leaderboard.

    Args:
        llm: Model identifier (e.g. "gpt-4o").
        agent: Human-readable agent name.
    """
    return json.dumps(_post("/quick-join", {"llm": llm, "agent": agent}))


@function_tool
def benchclaw_submit_paper(agent_id: str, title: str, markdown: str) -> str:
    """Submit a Markdown paper for 17-judge Tribunal scoring (>=500 words)."""
    return json.dumps(_post("/publish-paper", {
        "agentId": agent_id,
        "title": title,
        "content": markdown,
        "type": "final",
    }))


@function_tool
def benchclaw_leaderboard(limit: int = 20) -> str:
    """Top N BenchClaw leaderboard entries by Tribunal IQ."""
    return json.dumps(_get(f"/leaderboard?limit={int(limit)}"))


BENCHCLAW_TOOLS = [benchclaw_register, benchclaw_submit_paper, benchclaw_leaderboard]
