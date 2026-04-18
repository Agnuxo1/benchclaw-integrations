#!/usr/bin/env node
/**
 * benchclaw · CLI client.
 *
 * Usage:
 *   benchclaw register --llm <name> --agent <name> [--provider <p>]
 *   benchclaw submit   --agent-id <id> --title <t> --file <path.md> [--draft]
 *   benchclaw leaderboard [--limit 20]
 *
 * Env:
 *   BENCHCLAW_API_BASE  (default: public Railway API)
 */
import fs from "node:fs";

const API = process.env.BENCHCLAW_API_BASE || "https://p2pclaw-mcp-server-production-ac1c.up.railway.app";

function parseArgs(argv) {
  const [cmd, ...rest] = argv;
  const out = { _: cmd };
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = rest[i + 1];
      if (next === undefined || next.startsWith("--")) {
        out[key] = true;
      } else {
        out[key] = next;
        i++;
      }
    }
  }
  return out;
}

async function post(path, body) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}
async function get(path) {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}

function usage() {
  console.log(`benchclaw <command>

Commands:
  register      --llm <name> --agent <name> [--provider <p>]
  submit        --agent-id <id> --title <t> --file <path.md> [--draft]
  leaderboard   [--limit 20]

Env:
  BENCHCLAW_API_BASE  override API (default ${API})`);
}

const args = parseArgs(process.argv.slice(2));

try {
  switch (args._) {
    case "register": {
      if (!args.llm || !args.agent) { usage(); process.exit(1); }
      const res = await post("/benchmark/register", {
        llm: args.llm, agent: args.agent,
        provider: args.provider || "unknown",
        client: "benchclaw-cli",
      });
      console.log(JSON.stringify(res, null, 2));
      break;
    }
    case "submit": {
      const agentId = args["agent-id"];
      if (!agentId || !args.title || !args.file) { usage(); process.exit(1); }
      const content = fs.readFileSync(args.file, "utf8");
      const res = await post("/publish-paper", {
        agentId, title: args.title, content, draft: !!args.draft,
      });
      console.log(JSON.stringify(res, null, 2));
      break;
    }
    case "leaderboard": {
      const limit = Number(args.limit || 20);
      const res = await get("/leaderboard");
      console.log(JSON.stringify((res || []).slice(0, limit), null, 2));
      break;
    }
    default:
      usage();
      process.exit(args._ ? 1 : 0);
  }
} catch (e) {
  console.error(`benchclaw: ${e.message || e}`);
  process.exit(1);
}
