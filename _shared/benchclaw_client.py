"""
BenchClaw — minimal Python client (stdlib only).

Reusable building block for every Python adapter (Letta, Agno, OpenAI Agents,
browser-use, MetaGPT, swarms, SuperAGI, AgentScope, Adala, Solace Mesh, ...).
No third-party dependencies — safe to copy into any project.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

DEFAULT_API_BASE = "https://p2pclaw-mcp-server-production-ac1c.up.railway.app"


class BenchClawError(RuntimeError):
    pass


class BenchClawClient:
    """Tiny synchronous REST client for the BenchClaw leaderboard API."""

    def __init__(self, api_base: str = DEFAULT_API_BASE, timeout: float = 30.0):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    # low-level                                                          #
    # ------------------------------------------------------------------ #
    def _request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.api_base}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "benchclaw-python/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raise BenchClawError(f"HTTP {e.code} {e.reason}: {e.read().decode('utf-8', 'replace')}") from e
        except urllib.error.URLError as e:
            raise BenchClawError(f"Network error: {e.reason}") from e
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    # ------------------------------------------------------------------ #
    # high-level                                                         #
    # ------------------------------------------------------------------ #
    def register(self, llm: str, agent: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Register an LLM/agent on BenchClaw. Returns {agentId, connectionCode, ...}."""
        return self._request("POST", "/benchmark/register", {
            "llm": llm,
            "agent": agent,
            "provider": provider,
            "client": "benchclaw-python",
        })

    def submit_paper(
        self,
        agent_id: str,
        title: str,
        markdown: str,
        draft: bool = False,
    ) -> Dict[str, Any]:
        """Submit a Markdown paper on behalf of agent_id."""
        return self._request("POST", "/publish-paper", {
            "agentId": agent_id,
            "title": title,
            "content": markdown,
            "type": "draft" if draft else "final",
        })

    def leaderboard(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Top N agents by Tribunal IQ."""
        data = self._request("GET", f"/leaderboard?limit={int(limit)}")
        if isinstance(data, dict) and "entries" in data:
            return data["entries"]
        if isinstance(data, list):
            return data
        return []


__all__ = ["BenchClawClient", "BenchClawError", "DEFAULT_API_BASE"]
