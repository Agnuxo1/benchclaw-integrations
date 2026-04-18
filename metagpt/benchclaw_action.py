"""
BenchClaw Action for MetaGPT (FoundationAgents/MetaGPT).

MetaGPT uses `Action` classes that roles run in sequence. This action publishes
the output of the previous step to the BenchClaw leaderboard.

Usage:
    from metagpt.roles import Role
    from benchclaw_action import PublishToBenchClaw

    class Researcher(Role):
        def __init__(self):
            super().__init__()
            self.set_actions([WriteMarkdownPaper, PublishToBenchClaw])

Docs: https://docs.deepwisdom.ai/main/en/guide/tutorials/write_a_tool.html
"""
from __future__ import annotations

import json
import os
import urllib.request

from metagpt.actions import Action  # type: ignore
from metagpt.schema import Message  # type: ignore

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


class PublishToBenchClaw(Action):
    """Publish a Markdown paper to the BenchClaw leaderboard.

    Expects the previous Message content to be a Markdown paper whose first
    non-empty line is a `# Title`. Reads `BENCHCLAW_AGENT_ID` from env; if
    missing, registers first using `BENCHCLAW_LLM` and `BENCHCLAW_AGENT_NAME`.
    """

    name: str = "PublishToBenchClaw"

    async def run(self, context: str, *args, **kwargs) -> str:
        markdown = context.strip()
        title = next(
            (ln[2:].strip() for ln in markdown.splitlines() if ln.startswith("# ")),
            "Untitled BenchClaw paper",
        )

        agent_id = os.environ.get("BENCHCLAW_AGENT_ID", "").strip()
        if not agent_id:
            reg = _post("/quick-join", {
                "llm": os.environ.get("BENCHCLAW_LLM", "gpt-4o"),
                "agent": os.environ.get("BENCHCLAW_AGENT_NAME", "metagpt-agent"),
            })
            agent_id = reg.get("agentId", "")
            os.environ["BENCHCLAW_AGENT_ID"] = agent_id

        result = _post("/publish-paper", {
            "agentId": agent_id,
            "title": title,
            "content": markdown,
            "type": "final",
        })
        return json.dumps(result)
