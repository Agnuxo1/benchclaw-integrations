/**
 * BenchClaw · Discord bot (discord.js v14).
 *
 * Slash commands:
 *   /benchclaw-register llm:<name> agent:<name>
 *   /benchclaw-submit   agent_id:<id> title:<t> content:<md>
 *   /benchclaw-leaderboard [limit:<n>]
 *
 * Env:
 *   DISCORD_TOKEN, DISCORD_CLIENT_ID, DISCORD_GUILD_ID (for instant registration)
 *   BENCHCLAW_API_BASE (optional)
 */
import {
  Client,
  GatewayIntentBits,
  REST,
  Routes,
  SlashCommandBuilder,
} from "discord.js";

const API =
  process.env.BENCHCLAW_API_BASE ||
  "https://p2pclaw-mcp-server-production-ac1c.up.railway.app";

async function req(method, path, body) {
  const r = await fetch(`${API}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}

const commands = [
  new SlashCommandBuilder()
    .setName("benchclaw-register")
    .setDescription("Register an LLM/agent on the BenchClaw leaderboard")
    .addStringOption((o) => o.setName("llm").setDescription("Model name").setRequired(true))
    .addStringOption((o) => o.setName("agent").setDescription("Agent name").setRequired(true)),
  new SlashCommandBuilder()
    .setName("benchclaw-submit")
    .setDescription("Submit a Markdown paper for Tribunal scoring")
    .addStringOption((o) => o.setName("agent_id").setDescription("Agent id").setRequired(true))
    .addStringOption((o) => o.setName("title").setDescription("Paper title").setRequired(true))
    .addStringOption((o) => o.setName("content").setDescription("Paper body in Markdown").setRequired(true))
    .addBooleanOption((o) => o.setName("draft").setDescription("Submit as draft")),
  new SlashCommandBuilder()
    .setName("benchclaw-leaderboard")
    .setDescription("Show the top BenchClaw leaderboard entries")
    .addIntegerOption((o) => o.setName("limit").setDescription("Top N (default 10)")),
].map((c) => c.toJSON());

const token = process.env.DISCORD_TOKEN;
const clientId = process.env.DISCORD_CLIENT_ID;
const guildId = process.env.DISCORD_GUILD_ID;

if (!token || !clientId) {
  console.error("Set DISCORD_TOKEN and DISCORD_CLIENT_ID");
  process.exit(1);
}

const rest = new REST({ version: "10" }).setToken(token);
await rest.put(
  guildId
    ? Routes.applicationGuildCommands(clientId, guildId)
    : Routes.applicationCommands(clientId),
  { body: commands },
);
console.log("[BenchClaw] slash commands registered");

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.on("interactionCreate", async (i) => {
  if (!i.isChatInputCommand()) return;
  try {
    if (i.commandName === "benchclaw-register") {
      const res = await req("POST", "/benchmark/register", {
        llm: i.options.getString("llm"),
        agent: i.options.getString("agent"),
        client: "benchclaw-discord",
      });
      await i.reply(`Registered: \`${res.agentId}\``);
    } else if (i.commandName === "benchclaw-submit") {
      const res = await req("POST", "/publish-paper", {
        agentId: i.options.getString("agent_id"),
        title: i.options.getString("title"),
        content: i.options.getString("content"),
        draft: i.options.getBoolean("draft") ?? false,
      });
      await i.reply(`Submitted: \`${res.id || "ok"}\``);
    } else if (i.commandName === "benchclaw-leaderboard") {
      const rows = await req("GET", "/leaderboard");
      const limit = i.options.getInteger("limit") ?? 10;
      const top = (rows || [])
        .slice(0, limit)
        .map((r, n) => `${n + 1}. ${r.agent || r.agentId} — ${r.score ?? r.tribunalIQ ?? "-"}`)
        .join("\n");
      await i.reply("```\n" + top + "\n```");
    }
  } catch (e) {
    await i.reply({ content: `:warning: ${e.message || e}`, ephemeral: true });
  }
});

client.login(token);
