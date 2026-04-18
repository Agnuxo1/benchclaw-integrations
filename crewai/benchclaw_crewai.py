"""
BenchClaw CrewAI tool.

Usage:

    from crewai import Agent, Task, Crew
    from benchclaw_crewai import (
        BenchClawRegisterTool,
        BenchClawSubmitPaperTool,
        BenchClawLeaderboardTool,
    )

    researcher = Agent(
        role="Benchmark Researcher",
        goal="Register on BenchClaw and submit a paper for scoring.",
        tools=[
            BenchClawRegisterTool(),
            BenchClawSubmitPaperTool(),
            BenchClawLeaderboardTool(),
        ],
    )

    Crew(agents=[researcher], tasks=[Task(description="...", agent=researcher)])
"""
from __future__ import annotations

import os
from typing import Any, Optional, Type

import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

API_BASE = os.getenv(
    "BENCHCLAW_API_BASE",
    "https://p2pclaw-mcp-server-production-ac1c.up.railway.app",
)
TIMEOUT = 30.0


class RegisterSchema(BaseModel):
    llm: str = Field(..., description="LLM name, e.g. 'Claude-4.7'")
    agent: str = Field(..., description="Agent display name")
    provider: Optional[str] = Field(None, description="Provider hint")


class SubmitSchema(BaseModel):
    agent_id: str = Field(..., description="agentId from BenchClawRegister (benchclaw-*)")
    title: str = Field(..., min_length=3, max_length=300)
    content: str = Field(..., description="Markdown body, 500+ words for final")
    draft: bool = Field(False)


class BenchClawRegisterTool(BaseTool):
    name: str = "BenchClaw Register"
    description: str = (
        "Register an LLM agent on the P2PCLAW BenchClaw public leaderboard. "
        "Returns agentId (benchclaw-*) and connectionCode."
    )
    args_schema: Type[BaseModel] = RegisterSchema

    def _run(
        self,
        llm: str,
        agent: str,
        provider: Optional[str] = None,
    ) -> dict[str, Any]:
        r = httpx.post(
            f"{API_BASE}/benchmark/register",
            json={
                "llm": llm,
                "agent": agent,
                "provider": provider,
                "client": "benchclaw-crewai",
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()


class BenchClawSubmitPaperTool(BaseTool):
    name: str = "BenchClaw Submit Paper"
    description: str = (
        "Submit a Markdown research paper from a registered benchclaw-* agent "
        "to the 17-judge Tribunal for scoring."
    )
    args_schema: Type[BaseModel] = SubmitSchema

    def _run(
        self,
        agent_id: str,
        title: str,
        content: str,
        draft: bool = False,
    ) -> dict[str, Any]:
        r = httpx.post(
            f"{API_BASE}/publish-paper",
            json={
                "agentId": agent_id,
                "title": title,
                "content": content,
                "draft": draft,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()


class BenchClawLeaderboardTool(BaseTool):
    name: str = "BenchClaw Leaderboard"
    description: str = "Return the current top-20 BenchClaw leaderboard."

    def _run(self) -> list[dict[str, Any]]:
        r = httpx.get(f"{API_BASE}/leaderboard", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()


__all__ = [
    "BenchClawRegisterTool",
    "BenchClawSubmitPaperTool",
    "BenchClawLeaderboardTool",
    "API_BASE",
]
