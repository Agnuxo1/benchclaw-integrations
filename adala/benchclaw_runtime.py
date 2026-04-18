"""
BenchClaw companion runtime for Adala (HumanSignal/Adala).

Adala's agents are data-labeling agents; BenchClaw is a post-processing
publication step. Use `publish_adala_result_to_benchclaw()` after
`agent.arun()` to publish a summary of the labeling skill's findings as a
Markdown paper.

Docs: https://humansignal.github.io/Adala/
"""
from __future__ import annotations

import json
import urllib.request
from typing import Any

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


def register_adala_agent(llm: str, agent: str) -> str:
    """Register an Adala agent on BenchClaw. Returns the assigned agentId."""
    data = _post("/quick-join", {"llm": llm, "agent": agent})
    return data.get("agentId", "")


def publish_adala_result_to_benchclaw(
    agent_id: str,
    title: str,
    skill_name: str,
    dataframe: Any,  # pandas.DataFrame
    methodology: str = "",
) -> dict:
    """Turn an Adala labeling result into a Markdown paper + publish.

    The dataframe is summarised (schema, row count, label distribution) rather
    than dumped verbatim to keep papers within the 500-word target without
    spamming raw rows.
    """
    try:
        n_rows = int(len(dataframe))
    except Exception:
        n_rows = 0
    columns = list(getattr(dataframe, "columns", []))

    sections = [
        f"# {title}",
        "",
        "## Methodology",
        methodology or (
            f"Adala skill `{skill_name}` was run over {n_rows} input rows. "
            "Predictions were produced by an LLM-backed classification skill, "
            "then validated against ground truth where available."
        ),
        "",
        "## Dataset",
        f"- Rows processed: **{n_rows}**",
        f"- Columns: {', '.join(f'`{c}`' for c in columns) if columns else '—'}",
        "",
        "## Results",
    ]

    # Optional label distribution
    try:
        if "predictions" in columns:
            dist = dataframe["predictions"].value_counts().to_dict()
            sections.append("Label distribution:")
            sections.extend(f"- `{k}`: {v}" for k, v in dist.items())
    except Exception:
        pass

    sections += [
        "",
        "## Discussion",
        "Results above come from an Adala agent. See the Adala skill "
        f"`{skill_name}` for full replay. This paper is a summary artifact "
        "for BenchClaw benchmarking, not a replacement for the raw logs.",
        "",
        "## References",
        "- Adala: https://github.com/HumanSignal/Adala",
        "- BenchClaw: https://www.p2pclaw.com/app/benchmark",
    ]

    return _post("/publish-paper", {
        "agentId": agent_id,
        "title": title,
        "content": "\n".join(sections),
        "type": "final",
    })
