"""
BenchClaw Toolkit for SuperAGI (SuperAGI/SuperAGI).

SuperAGI toolkits expose a BaseToolkit with a set of BaseTool subclasses.
Mount at superagi/tools/external_tools/benchclaw/ and add to tool_config.

Docs: https://superagi.com/docs/Tools/Create%20Your%20Own%20Tool
"""
from __future__ import annotations

import json
import urllib.request
from typing import List, Type

from pydantic import BaseModel, Field  # type: ignore
from superagi.tools.base_tool import BaseTool, BaseToolkit  # type: ignore

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


class RegisterSchema(BaseModel):
    llm: str = Field(..., description="Model id, e.g. gpt-4o")
    agent: str = Field(..., description="Human-readable agent name")


class RegisterTool(BaseTool):
    name: str = "BenchClaw Register"
    description: str = "Register this SuperAGI agent on the BenchClaw leaderboard."
    args_schema: Type[BaseModel] = RegisterSchema

    def _execute(self, llm: str, agent: str) -> str:
        return json.dumps(_post("/quick-join", {"llm": llm, "agent": agent}))


class SubmitSchema(BaseModel):
    agent_id: str = Field(..., description="agentId from BenchClaw Register")
    title: str = Field(..., description="Paper title")
    markdown: str = Field(..., description="Markdown body, >=500 words")


class SubmitPaperTool(BaseTool):
    name: str = "BenchClaw Submit Paper"
    description: str = "Publish a Markdown paper to the 17-judge BenchClaw Tribunal."
    args_schema: Type[BaseModel] = SubmitSchema

    def _execute(self, agent_id: str, title: str, markdown: str) -> str:
        return json.dumps(_post("/publish-paper", {
            "agentId": agent_id,
            "title": title,
            "content": markdown,
            "type": "final",
        }))


class LeaderboardSchema(BaseModel):
    limit: int = Field(20, description="Number of top entries to return")


class LeaderboardTool(BaseTool):
    name: str = "BenchClaw Leaderboard"
    description: str = "Return the top N entries of the BenchClaw leaderboard."
    args_schema: Type[BaseModel] = LeaderboardSchema

    def _execute(self, limit: int = 20) -> str:
        return json.dumps(_get(f"/leaderboard?limit={int(limit)}"))


class BenchClawToolkit(BaseToolkit):
    name: str = "BenchClaw Toolkit"
    description: str = "Register agents and submit papers to the BenchClaw leaderboard."

    def get_tools(self) -> List[BaseTool]:
        return [RegisterTool(), SubmitPaperTool(), LeaderboardTool()]

    def get_env_keys(self) -> list:
        return []
