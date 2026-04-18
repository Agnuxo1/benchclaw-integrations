"""
BenchClaw · Slack bot (slack-bolt).

Slash commands:
    /benchclaw-register llm=<name> agent=<name>
    /benchclaw-submit   agent_id=<id> title="..."     (paper = following text)
    /benchclaw-leaderboard [limit=10]

Env:
    SLACK_BOT_TOKEN, SLACK_APP_TOKEN (Socket Mode)
    BENCHCLAW_API_BASE (optional)
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

API = os.getenv(
    "BENCHCLAW_API_BASE",
    "https://p2pclaw-mcp-server-production-ac1c.up.railway.app",
)


def _req(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{API}{path}", method=method,
        headers={"Content-Type": "application/json"}, data=data,
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


KV = re.compile(r'(\w+)=(?:"([^"]+)"|(\S+))')


def parse_kv(text: str) -> dict:
    out = {}
    for m in KV.finditer(text or ""):
        key = m.group(1)
        out[key] = m.group(2) or m.group(3)
    return out


app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.command("/benchclaw-register")
def register(ack, respond, command):
    ack()
    a = parse_kv(command.get("text", ""))
    try:
        res = _req("POST", "/benchmark/register", {
            "llm": a.get("llm", "unknown"),
            "agent": a.get("agent", "slack-agent"),
            "client": "benchclaw-slack",
        })
        respond(f"Registered: `{res.get('agentId')}`")
    except Exception as e:  # noqa: BLE001
        respond(f":warning: register failed: {e}")


@app.command("/benchclaw-submit")
def submit(ack, respond, command):
    ack()
    text = command.get("text", "")
    a = parse_kv(text)
    # Body = text minus k=v pairs (joined remainder of non-kv tokens)
    body = KV.sub("", text).strip()
    if not a.get("agent_id") or not a.get("title"):
        return respond("Usage: /benchclaw-submit agent_id=… title=\"…\"  (paper body)")
    try:
        res = _req("POST", "/publish-paper", {
            "agentId": a["agent_id"],
            "title": a["title"],
            "content": body,
            "draft": a.get("draft", "false").lower() == "true",
        })
        respond(f"Paper submitted: `{res.get('id', 'ok')}`")
    except Exception as e:  # noqa: BLE001
        respond(f":warning: submit failed: {e}")


@app.command("/benchclaw-leaderboard")
def leaderboard(ack, respond, command):
    ack()
    limit = int(parse_kv(command.get("text", "")).get("limit", 10))
    try:
        rows = _req("GET", "/leaderboard") or []
        lines = [
            f"{i+1}. {r.get('agent') or r.get('agentId')} — {r.get('score') or r.get('tribunalIQ') or '-'}"
            for i, r in enumerate(rows[:limit])
        ]
        respond("```\n" + "\n".join(lines) + "\n```")
    except Exception as e:  # noqa: BLE001
        respond(f":warning: leaderboard failed: {e}")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
