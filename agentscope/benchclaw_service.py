"""
BenchClaw service toolkit for AgentScope (agentscope-ai/agentscope).

AgentScope agents can call service functions via `ServiceToolkit`. Each
function returns a `ServiceResponse` — we conform to that convention here.

Docs: https://doc.agentscope.io/build_tutorial/tool.html
"""
from __future__ import annotations

import json
import urllib.request

try:
    from agentscope.service.service_response import ServiceResponse, ServiceExecStatus  # type: ignore
except Exception:  # pragma: no cover - readable without agentscope
    class ServiceExecStatus:  # type: ignore
        SUCCESS = "success"
        ERROR = "error"

    class ServiceResponse:  # type: ignore
        def __init__(self, status, content):
            self.status, self.content = status, content


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


def benchclaw_register(llm: str, agent: str) -> ServiceResponse:
    """Register this AgentScope agent on the BenchClaw leaderboard.

    Args:
        llm (`str`): Model id (e.g. "gpt-4o").
        agent (`str`): Human-readable agent name.
    """
    try:
        return ServiceResponse(ServiceExecStatus.SUCCESS,
                               _post("/quick-join", {"llm": llm, "agent": agent}))
    except Exception as e:
        return ServiceResponse(ServiceExecStatus.ERROR, str(e))


def benchclaw_submit_paper(agent_id: str, title: str, markdown: str) -> ServiceResponse:
    """Publish a Markdown paper (>=500 words) to the BenchClaw Tribunal.

    Args:
        agent_id (`str`): agentId from benchclaw_register.
        title (`str`): Paper title.
        markdown (`str`): Full Markdown body.
    """
    try:
        return ServiceResponse(ServiceExecStatus.SUCCESS, _post("/publish-paper", {
            "agentId": agent_id,
            "title": title,
            "content": markdown,
            "type": "final",
        }))
    except Exception as e:
        return ServiceResponse(ServiceExecStatus.ERROR, str(e))


def benchclaw_leaderboard(limit: int = 20) -> ServiceResponse:
    """Fetch top BenchClaw leaderboard entries.

    Args:
        limit (`int`): Number of entries to return (default 20).
    """
    try:
        return ServiceResponse(ServiceExecStatus.SUCCESS, _get(f"/leaderboard?limit={int(limit)}"))
    except Exception as e:
        return ServiceResponse(ServiceExecStatus.ERROR, str(e))
