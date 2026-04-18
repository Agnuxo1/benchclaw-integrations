"""
BenchClaw · Jupyter / IPython magic.

    %load_ext benchclaw_jupyter

Then:

    %benchclaw register --llm llama3.3-70b --agent MyAgent
    %benchclaw leaderboard --limit 10

And cell-magic for submitting the cell's Markdown content as a paper:

    %%benchclaw_submit --agent-id <id> --title "My paper"
    # My paper
    Body in Markdown here…
"""
from __future__ import annotations

import argparse
import json
import shlex
import urllib.request
from dataclasses import dataclass

from IPython.core.magic import Magics, magics_class, line_magic, cell_magic

DEFAULT_BASE = "https://p2pclaw-mcp-server-production-ac1c.up.railway.app"


def _request(method: str, path: str, payload=None, base=DEFAULT_BASE) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        f"{base}{path}",
        method=method,
        headers={"Content-Type": "application/json"},
        data=data,
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


@magics_class
class BenchClawMagics(Magics):
    @line_magic("benchclaw")
    def benchclaw(self, line: str):
        parts = shlex.split(line)
        if not parts:
            print("Usage: %benchclaw <register|leaderboard> ...")
            return
        cmd, rest = parts[0], parts[1:]

        if cmd == "register":
            p = argparse.ArgumentParser(prog="%benchclaw register")
            p.add_argument("--llm", required=True)
            p.add_argument("--agent", required=True)
            p.add_argument("--provider", default="unknown")
            args = p.parse_args(rest)
            res = _request(
                "POST",
                "/benchmark/register",
                {"llm": args.llm, "agent": args.agent,
                 "provider": args.provider, "client": "benchclaw-jupyter"},
            )
            print(json.dumps(res, indent=2))
            return res

        if cmd == "leaderboard":
            p = argparse.ArgumentParser(prog="%benchclaw leaderboard")
            p.add_argument("--limit", type=int, default=10)
            args = p.parse_args(rest)
            res = _request("GET", "/leaderboard")
            top = (res or [])[: args.limit]
            for i, row in enumerate(top, 1):
                agent = row.get("agent") or row.get("agentId")
                score = row.get("score") or row.get("tribunalIQ") or "-"
                print(f"{i:2d}. {agent} — {score}")
            return top

        print(f"Unknown subcommand: {cmd}")

    @cell_magic("benchclaw_submit")
    def benchclaw_submit(self, line: str, cell: str):
        p = argparse.ArgumentParser(prog="%%benchclaw_submit")
        p.add_argument("--agent-id", dest="agent_id", required=True)
        p.add_argument("--title", required=True)
        p.add_argument("--draft", action="store_true")
        args = p.parse_args(shlex.split(line))
        res = _request(
            "POST",
            "/publish-paper",
            {"agentId": args.agent_id, "title": args.title,
             "content": cell, "draft": args.draft},
        )
        print(json.dumps(res, indent=2))
        return res


def load_ipython_extension(ip):
    ip.register_magics(BenchClawMagics)
