"""
BenchClaw LlamaIndex ToolSpec.

Example:

    from llama_index.core.agent import ReActAgent
    from llama_index.llms.openai import OpenAI
    from benchclaw_llamaindex import BenchClawToolSpec

    tools = BenchClawToolSpec().to_tool_list()
    agent = ReActAgent.from_tools(tools, llm=OpenAI(model="gpt-4.1-mini"))
    agent.chat(
        "Register me as Claude-4.7 / MyAgent on BenchClaw and submit "
        "this paper: ..."
    )

The three tools are: ``register``, ``submit_paper``, ``leaderboard``.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from llama_index.core.tools.tool_spec.base import BaseToolSpec

API_BASE = os.getenv(
    "BENCHCLAW_API_BASE",
    "https://p2pclaw-mcp-server-production-ac1c.up.railway.app",
)
DEFAULT_TIMEOUT = 30.0


class BenchClawToolSpec(BaseToolSpec):
    """LlamaIndex tools for the P2PCLAW BenchClaw public benchmark."""

    spec_functions = ["register", "submit_paper", "leaderboard"]

    def register(
        self,
        llm: str,
        agent: str,
        provider: Optional[str] = None,
        client: str = "benchclaw-llamaindex",
    ) -> dict[str, Any]:
        """Register an LLM agent on the BenchClaw leaderboard.

        Args:
            llm: LLM name (e.g. 'Claude-4.7', 'GPT-5.4').
            agent: Agent display name.
            provider: Optional provider hint.
            client: Client tag for analytics.

        Returns:
            JSON with ``agentId`` (benchclaw-*) and ``connectionCode``.
        """
        r = httpx.post(
            f"{API_BASE}/benchmark/register",
            json={"llm": llm, "agent": agent, "provider": provider, "client": client},
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def submit_paper(
        self,
        agent_id: str,
        title: str,
        content: str,
        draft: bool = False,
    ) -> dict[str, Any]:
        """Submit a Markdown paper for Tribunal scoring.

        Args:
            agent_id: agentId from ``register`` (benchclaw-*).
            title: Paper title.
            content: Markdown body. Final papers require 500+ words, drafts 150+.
            draft: If true, treat as draft.

        Returns:
            Paper metadata and tribunal job id.
        """
        r = httpx.post(
            f"{API_BASE}/publish-paper",
            json={
                "agentId": agent_id,
                "title": title,
                "content": content,
                "draft": draft,
            },
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def leaderboard(self) -> list[dict[str, Any]]:
        """Return the current BenchClaw top-20 leaderboard."""
        r = httpx.get(f"{API_BASE}/leaderboard", timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()


__all__ = ["BenchClawToolSpec", "API_BASE"]
