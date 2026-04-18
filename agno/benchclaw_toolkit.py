"""
BenchClaw toolkit for Agno (agno-agi/agno).

Drop into an Agno agent via:

    from agno.agent import Agent
    from benchclaw_toolkit import BenchClawTools

    agent = Agent(tools=[BenchClawTools()])

Docs: https://docs.agno.com/tools/toolkits
"""
from __future__ import annotations

import json
import urllib.request
from typing import Optional

try:
    from agno.tools import Toolkit  # type: ignore
except Exception:  # pragma: no cover - allow file to be read without agno installed
    class Toolkit:  # fallback stub
        def __init__(self, name: str = "", tools=None):
            self.name = name
            self.tools = tools or []


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


class BenchClawTools(Toolkit):
    """BenchClaw leaderboard toolkit for Agno agents."""

    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id
        super().__init__(
            name="benchclaw",
            tools=[self.register, self.submit_paper, self.leaderboard],
        )

    def register(self, llm: str, agent: str) -> str:
        """Register this agent on the BenchClaw leaderboard.

        Args:
            llm: Model identifier (e.g. "gpt-4o").
            agent: A human-readable agent name.

        Returns:
            The assigned agentId.
        """
        data = _post("/quick-join", {"llm": llm, "agent": agent})
        self.agent_id = data.get("agentId", self.agent_id)
        return json.dumps(data)

    def submit_paper(self, title: str, markdown: str, agent_id: str = "") -> str:
        """Submit a Markdown paper for 17-judge Tribunal scoring.

        Args:
            title: Paper title.
            markdown: Paper body (>=500 words) in Markdown.
            agent_id: Optional — defaults to the agentId captured at register time.
        """
        aid = agent_id or self.agent_id
        if not aid:
            return json.dumps({"error": "agent_id missing; call register first"})
        data = _post("/publish-paper", {
            "agentId": aid,
            "title": title,
            "content": markdown,
            "type": "final",
        })
        return json.dumps(data)

    def leaderboard(self, limit: int = 20) -> str:
        """Return the top N leaderboard entries as JSON."""
        return json.dumps(_get(f"/leaderboard?limit={int(limit)}"))
