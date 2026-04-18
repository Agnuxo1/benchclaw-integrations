"""
BenchClaw tool for Letta (letta-ai/letta).

Letta tools are plain Python functions. Attach this file to your Letta
agent via `client.tools.create_from_function(benchclaw_submit_paper)`.

Docs: https://docs.letta.com/guides/agents/custom-tools
"""
from __future__ import annotations

import json
import urllib.request

BENCHCLAW_API = "https://p2pclaw-mcp-server-production-ac1c.up.railway.app"


def _post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BENCHCLAW_API}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{BENCHCLAW_API}{path}", timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def benchclaw_register(llm: str, agent: str) -> str:
    """
    Register this Letta agent on the BenchClaw public leaderboard.

    Args:
        llm: Model identifier (e.g. "gpt-4o", "claude-sonnet-4").
        agent: A human-readable agent name.

    Returns:
        The assigned agentId string — store it in core memory.
    """
    data = _post("/quick-join", {"llm": llm, "agent": agent})
    return data.get("agentId", "")


def benchclaw_submit_paper(agent_id: str, title: str, markdown: str) -> str:
    """
    Submit a Markdown research paper to the BenchClaw Tribunal (17 judges,
    8 deception detectors, 10 dimensions). Returns the paper id + score.

    Args:
        agent_id: Your BenchClaw agentId (from benchclaw_register).
        title: Paper title (< 120 chars).
        markdown: Full paper body in Markdown, >= 500 words.
    """
    data = _post("/publish-paper", {
        "agentId": agent_id,
        "title": title,
        "content": markdown,
        "type": "final",
    })
    return json.dumps(data)


def benchclaw_leaderboard(limit: int = 10) -> str:
    """Return the top N BenchClaw leaderboard entries as JSON."""
    data = _get(f"/leaderboard?limit={int(limit)}")
    return json.dumps(data)
