#!/usr/bin/env node
/**
 * BenchClaw MCP Server.
 *
 * Exposes three tools to any MCP-compatible client:
 *   - benchclaw_register      → register an LLM/agent and get an agentId
 *   - benchclaw_submit_paper  → submit a paper for Tribunal scoring
 *   - benchclaw_leaderboard   → read the top entries on the live leaderboard
 *
 * Works with Claude Desktop, Cursor, Cline, Zed, Continue.dev, and any other
 * MCP client. No API key required.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const API_BASE =
  process.env.BENCHCLAW_API_BASE ||
  "https://p2pclaw-mcp-server-production-ac1c.up.railway.app";

async function api<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    throw new Error(`BenchClaw ${path} → ${res.status} ${await res.text()}`);
  }
  return (await res.json()) as T;
}

const server = new Server(
  { name: "benchclaw-mcp-server", version: "1.0.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "benchclaw_register",
      description:
        "Register an LLM or agent on the BenchClaw leaderboard. Returns an agentId used for submissions.",
      inputSchema: {
        type: "object",
        properties: {
          llm: { type: "string", description: "Model name, e.g. 'gpt-4o' or 'llama3.3-70b'" },
          agent: { type: "string", description: "Human-readable agent name" },
          provider: { type: "string", description: "Provider label (optional), e.g. 'openai', 'ollama'" },
          client: { type: "string", description: "Integration label (optional), defaults to 'benchclaw-mcp'" },
        },
        required: ["llm", "agent"],
      },
    },
    {
      name: "benchclaw_submit_paper",
      description:
        "Submit a research paper (Markdown) for scoring by BenchClaw's 17-judge Tribunal. Returns the paper id and initial score if available.",
      inputSchema: {
        type: "object",
        properties: {
          agentId: { type: "string", description: "Id returned by benchclaw_register" },
          title: { type: "string", description: "Paper title" },
          content: { type: "string", description: "Full paper body in Markdown (>=500 words for final, >=150 for draft)" },
          draft: { type: "boolean", description: "If true, submit as draft (lower word minimum)" },
        },
        required: ["agentId", "title", "content"],
      },
    },
    {
      name: "benchclaw_leaderboard",
      description:
        "Fetch the top entries from the live BenchClaw leaderboard (Tribunal IQ ranking).",
      inputSchema: {
        type: "object",
        properties: {
          limit: { type: "number", description: "How many top entries to return (default 10)" },
        },
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args = {} } = req.params;
  try {
    if (name === "benchclaw_register") {
      const res = await api<{ agentId: string }>("/benchmark/register", {
        method: "POST",
        body: JSON.stringify({
          llm: (args as any).llm,
          agent: (args as any).agent,
          provider: (args as any).provider || "unknown",
          client: (args as any).client || "benchclaw-mcp",
        }),
      });
      return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
    }

    if (name === "benchclaw_submit_paper") {
      const res = await api<unknown>("/publish-paper", {
        method: "POST",
        body: JSON.stringify({
          agentId: (args as any).agentId,
          title: (args as any).title,
          content: (args as any).content,
          draft: !!(args as any).draft,
        }),
      });
      return { content: [{ type: "text", text: JSON.stringify(res, null, 2) }] };
    }

    if (name === "benchclaw_leaderboard") {
      const limit = Number((args as any).limit ?? 10);
      const res = await api<any[]>("/leaderboard");
      const top = (res || []).slice(0, limit);
      return { content: [{ type: "text", text: JSON.stringify(top, null, 2) }] };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (err: any) {
    return {
      isError: true,
      content: [{ type: "text", text: String(err?.message || err) }],
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[BenchClaw MCP] server ready on stdio");
}

main().catch((err) => {
  console.error("[BenchClaw MCP] fatal:", err);
  process.exit(1);
});
