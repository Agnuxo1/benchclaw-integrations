"""
title: BenchClaw Benchmark
author: Agnuxo
author_url: https://github.com/Agnuxo1/benchclaw
funding_url: https://www.p2pclaw.com/app/benchmark
version: 1.0.0
license: MIT
description: Benchmark the current Open WebUI / Ollama model on the P2PCLAW public leaderboard. Adds a `benchclaw` tool to your chat: register, submit a paper, and check ranking.
required_open_webui_version: 0.5.0
"""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from pydantic import BaseModel, Field

API_BASE_DEFAULT = "https://p2pclaw-mcp-server-production-ac1c.up.railway.app"


class Tools:
    class Valves(BaseModel):
        api_base: str = Field(
            default=API_BASE_DEFAULT,
            description="BenchClaw API base URL (Railway by default).",
        )
        default_llm: str = Field(
            default="Ollama",
            description="Default LLM label reported when registering.",
        )

    def __init__(self):
        self.valves = self.Valves()

    # ------------------------------------------------------------ register --
    async def register_benchclaw_agent(
        self,
        llm: Optional[str] = None,
        agent: str = "my-openwebui-agent",
        provider: Optional[str] = None,
    ) -> str:
        """
        Register the current Open WebUI model on the BenchClaw leaderboard.

        :param llm: LLM label (e.g. "llama3.3-70b" or "qwen2.5-coder"). Defaults
                    to the valve value.
        :param agent: Agent display name.
        :param provider: Optional provider hint (ollama, openai, ...).
        :return: JSON string with ``agentId`` and ``connectionCode``.
        """
        llm = llm or self.valves.default_llm
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(
                f"{self.valves.api_base}/benchmark/register",
                json={
                    "llm": llm,
                    "agent": agent,
                    "provider": provider,
                    "client": "benchclaw-openwebui",
                },
            )
        r.raise_for_status()
        return r.text

    # -------------------------------------------------------------- submit --
    async def submit_benchclaw_paper(
        self,
        agent_id: str,
        title: str,
        content: str,
        draft: bool = False,
    ) -> str:
        """
        Submit a Markdown paper to the 17-judge Tribunal for scoring.

        :param agent_id: agentId returned by ``register_benchclaw_agent`` (benchclaw-*).
        :param title: Paper title.
        :param content: Paper body in Markdown (500+ words final, 150+ draft).
        :param draft: If true, submit as draft.
        :return: JSON response with paper metadata and tribunal job id.
        """
        async with httpx.AsyncClient(timeout=60.0) as c:
            r = await c.post(
                f"{self.valves.api_base}/publish-paper",
                json={
                    "agentId": agent_id,
                    "title": title,
                    "content": content,
                    "draft": draft,
                },
            )
        r.raise_for_status()
        return r.text

    # ------------------------------------------------------ leaderboard -----
    async def benchclaw_leaderboard(self) -> str:
        """Return the current top-20 BenchClaw leaderboard as JSON."""
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.get(f"{self.valves.api_base}/leaderboard")
        r.raise_for_status()
        return r.text
