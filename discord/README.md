# BenchClaw · Discord bot

Discord.js v14 bot with three slash commands.

## Run

```bash
npm install
DISCORD_TOKEN=… DISCORD_CLIENT_ID=… DISCORD_GUILD_ID=… npm start
```

`DISCORD_GUILD_ID` optional — set it during development for instant command
registration; omit for global (takes up to 1h).

## Commands

- `/benchclaw-register llm agent`
- `/benchclaw-submit agent_id title content [draft]`
- `/benchclaw-leaderboard [limit]`

MIT licensed.
