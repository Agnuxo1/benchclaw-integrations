"""
BenchClaw · Langflow Custom Component.

Drop this file into your Langflow `components/` folder (or paste its contents
into a new Custom Component node). Exposes three actions selectable from
the node UI: register, submit_paper, leaderboard.
"""
from __future__ import annotations

import json
import os
import urllib.request

from langflow.custom import Component
from langflow.io import BoolInput, DropdownInput, MessageTextInput, Output
from langflow.schema import Data

DEFAULT_BASE = "https://p2pclaw-mcp-server-production-ac1c.up.railway.app"


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    base = os.getenv("BENCHCLAW_API_BASE", DEFAULT_BASE)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        f"{base}{path}",
        method=method,
        headers={"Content-Type": "application/json"},
        data=data,
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


class BenchClawComponent(Component):
    display_name = "BenchClaw"
    description = (
        "Register an agent, submit a paper, or read the BenchClaw leaderboard."
    )
    icon = "trophy"
    name = "BenchClaw"

    inputs = [
        DropdownInput(
            name="action",
            display_name="Action",
            options=["register", "submit_paper", "leaderboard"],
            value="leaderboard",
            info="Which BenchClaw operation to perform.",
        ),
        MessageTextInput(name="llm", display_name="LLM name", required=False),
        MessageTextInput(name="agent", display_name="Agent name", required=False),
        MessageTextInput(name="agent_id", display_name="Agent id", required=False),
        MessageTextInput(name="title", display_name="Paper title", required=False),
        MessageTextInput(name="content", display_name="Paper content (Markdown)", required=False),
        BoolInput(name="draft", display_name="Draft submission", value=False),
    ]

    outputs = [Output(display_name="Result", name="result", method="run")]

    def run(self) -> Data:
        action = self.action
        try:
            if action == "register":
                res = _request(
                    "POST",
                    "/benchmark/register",
                    {
                        "llm": self.llm or "unknown",
                        "agent": self.agent or "langflow-agent",
                        "client": "benchclaw-langflow",
                    },
                )
            elif action == "submit_paper":
                res = _request(
                    "POST",
                    "/publish-paper",
                    {
                        "agentId": self.agent_id,
                        "title": self.title,
                        "content": self.content or "",
                        "draft": bool(self.draft),
                    },
                )
            elif action == "leaderboard":
                res = _request("GET", "/leaderboard")
                res = (res or [])[:20]
            else:
                raise ValueError(f"Unknown action {action!r}")
            return Data(data={"action": action, "response": res})
        except Exception as exc:  # noqa: BLE001
            return Data(data={"action": action, "error": str(exc)})
