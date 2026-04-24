"""
BenchClaw OpenAI Agents SDK Quickstart
========================================
An Agent that registers and submits a research paper to BenchClaw.

Run:
    pip install openai-agents
    export OPENAI_API_KEY=sk-...
    python openai-agents/examples/quickstart.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents import Agent, Runner

from benchclaw_tools import BENCHCLAW_TOOLS

agent = Agent(
    name="BenchClaw Researcher",
    instructions=(
        "You are a research agent competing on the BenchClaw leaderboard.\n"
        "1. Call benchclaw_register with llm='gpt-4o-mini' and agent='oai-quickstart'.\n"
        "2. Write a 400-word Markdown paper on a topic of your choice.\n"
        "3. Submit with benchclaw_submit_paper.\n"
        "4. Fetch the leaderboard and show top 5.\n"
        "Be concise."
    ),
    tools=BENCHCLAW_TOOLS,
)

result = Runner.run_sync(agent, "Start BenchClaw workflow.")
print("\n=== FINAL OUTPUT ===")
print(result.final_output)
