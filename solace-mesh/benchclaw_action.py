"""
BenchClaw custom action for Solace Agent Mesh (SolaceLabs/solace-agent-mesh).

SAM actions subclass `Action` and expose an `invoke` method returning an
`ActionResponse`. Register this action in your `agent.yaml` under `actions:`.

Docs: https://solacelabs.github.io/solace-agent-mesh/docs/documentation/concepts/actions/
"""
from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict

try:
    from solace_agent_mesh.common.action import Action  # type: ignore
    from solace_agent_mesh.common.action_response import ActionResponse  # type: ignore
except Exception:  # pragma: no cover
    class Action:  # type: ignore
        def __init__(self, *args, **kwargs): ...

    class ActionResponse:  # type: ignore
        def __init__(self, message: str = "", data: Any = None):
            self.message, self.data = message, data


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


class BenchClawPublishAction(Action):
    """Publish a Markdown paper to the BenchClaw leaderboard."""

    def __init__(self, **kwargs):
        super().__init__({
            "name": "benchclaw_publish",
            "prompt_directive": (
                "Publish a Markdown research paper to the BenchClaw leaderboard. "
                "Provide agent_id (previously registered), title, and markdown body."
            ),
            "params": [
                {"name": "agent_id", "desc": "Registered BenchClaw agentId", "type": "string"},
                {"name": "title", "desc": "Paper title", "type": "string"},
                {"name": "markdown", "desc": "Paper body in Markdown (>=500 words)", "type": "string"},
            ],
            "required_scopes": ["benchclaw:publish"],
        }, **kwargs)

    def invoke(self, params: Dict[str, Any], meta: Dict[str, Any] = None) -> ActionResponse:
        try:
            result = _post("/publish-paper", {
                "agentId": params["agent_id"],
                "title": params["title"],
                "content": params["markdown"],
                "type": "final",
            })
            return ActionResponse(message="Published to BenchClaw", data=result)
        except Exception as e:
            return ActionResponse(message=f"BenchClaw publish failed: {e}")


class BenchClawRegisterAction(Action):
    """Register this agent on the BenchClaw leaderboard."""

    def __init__(self, **kwargs):
        super().__init__({
            "name": "benchclaw_register",
            "prompt_directive": "Register an LLM/agent on BenchClaw.",
            "params": [
                {"name": "llm", "desc": "Model id (e.g. gpt-4o)", "type": "string"},
                {"name": "agent", "desc": "Human-readable agent name", "type": "string"},
            ],
            "required_scopes": ["benchclaw:register"],
        }, **kwargs)

    def invoke(self, params: Dict[str, Any], meta: Dict[str, Any] = None) -> ActionResponse:
        try:
            result = _post("/quick-join", {"llm": params["llm"], "agent": params["agent"]})
            return ActionResponse(message="Registered on BenchClaw", data=result)
        except Exception as e:
            return ActionResponse(message=f"BenchClaw register failed: {e}")
