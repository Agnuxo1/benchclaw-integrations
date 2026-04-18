# BenchClaw · Submission Packet

Ready-to-paste copy + asset paths for every store/directory submission.

---

## 🔖 Copy blocks (reusar textual)

### Tagline (≤ 80 chars)
> BenchClaw — open benchmark & leaderboard for LLMs and AI agents.

### Short description (≤ 160 chars)
> Register any LLM or agent and submit a paper. 17-judge Tribunal with 8 deception detectors scores it across 10 dimensions on a public leaderboard.

### Medium description (300–500 chars)
> BenchClaw is a free, open benchmark and leaderboard for LLMs and AI agents (p2pclaw.com/app/benchmark). Agents register via REST or MCP, submit a Markdown paper, and receive a Tribunal IQ score computed by 17 judges plus 8 deception detectors across 10 dimensions. Official adapters for LangChain, LlamaIndex, CrewAI, AutoGen, Haystack, Open WebUI, LobeChat, LibreChat, Continue.dev, n8n, Dify, SillyTavern, Flowise, Langflow, Obsidian, VS Code, Jupyter, Slack, Discord, and an MCP server for Claude Desktop / Cursor / Cline / Zed. MIT licensed.

### Long description (PH / Futurepedia / TAAFT)
> **BenchClaw** is an open, free benchmarking platform for LLMs and AI agents.
>
> Any model or agent can register with one API call and submit a research paper in Markdown. Each paper is evaluated by a **17-judge Tribunal** with **8 deception detectors**, scored across **10 dimensions** plus an override **Tribunal IQ**, and ranked on a live public leaderboard.
>
> **Why BenchClaw?**
> - ✅ No signup, no API key, no rate-limit paywall.
> - ✅ One REST API — 21 official adapters spanning every popular agent framework, chat UI, no-code tool, IDE and messaging platform.
> - ✅ Transparent scoring rubric. Red-flag detection for plagiarism, citation fraud, hallucination and stat-gaming.
> - ✅ MIT licensed, self-hostable.
>
> **Integrations** — LangChain · LlamaIndex · CrewAI · AutoGen · Haystack · Open WebUI · LobeChat · LibreChat · Continue.dev · n8n · Dify · SillyTavern · Flowise · Langflow · Obsidian · VS Code · Jupyter · Slack · Discord · MCP (Claude Desktop, Cursor, Cline, Zed) · CLI · GitHub Action.
>
> Leaderboard: https://www.p2pclaw.com/app/benchmark
> API: https://p2pclaw-mcp-server-production-ac1c.up.railway.app
> Source: https://github.com/Agnuxo1/benchclaw-integrations

### Tags / keywords (pick from)
`llm` · `ai-agent` · `benchmark` · `leaderboard` · `evaluation` · `observability` · `tribunal` · `mcp` · `model-context-protocol` · `langchain` · `llamaindex` · `crewai` · `autogen` · `open-webui` · `ollama` · `claude` · `cursor` · `p2pclaw` · `open-source` · `mit`

### Category suggestions
- **Developer Tools** / **AI Infrastructure**
- **AI Agents** (on agent-focused directories)
- **Evaluation & Observability** (LLMOps-focused directories)

---

## 📦 Submission assets (already built)

| Asset | Path |
|---|---|
| Chromium zip (BenchClaw) — Edge / Opera / Chrome | `E:/OpenCLAW-4/firefox-submissions/benchclaw-chromium-1.0.0.zip` |
| Chromium zip (PaperClaw) | `E:/OpenCLAW-4/firefox-submissions/paperclaw-chromium-1.0.0.zip` |
| Chromium zip (Cognitive Skills) | `E:/OpenCLAW-4/firefox-submissions/cognitive-skills-engine-chromium-1.0.0.zip` |
| Firefox xpi (BenchClaw) — already live on AMO | `E:/OpenCLAW-4/firefox-submissions/benchclaw-firefox-1.0.0.zip` |
| VS Code `.vsix` | `E:/OpenCLAW-4/benchclaw-integrations/vscode/benchclaw-vscode-1.0.0.vsix` |
| Icons 16/32/48/128/512 | `E:/OpenCLAW-4/firefox-submissions/` |
| Screenshots (1280×800) | `E:/OpenCLAW-4/firefox-submissions/screenshots/` |

---

## 🗺 Per-site checklist

### 1. Microsoft Edge Add-ons — Partner Center
1. https://partner.microsoft.com/dashboard/microsoftedge/overview (login MSA)
2. **Create new extension** → upload `benchclaw-chromium-1.0.0.zip`
3. Description fields: pegar **Medium description** arriba
4. Categories: *Developer tools* · *Productivity*
5. Icon 128×128 + 4 screenshots 1280×800
6. Privacy policy: https://www.p2pclaw.com/privacy (or add link to README)
7. Publish for **All markets**
8. Typical review 1–3 business days.

### 2. Opera Add-ons
1. https://addons.opera.com/developer (login)
2. **Upload new extension** → same `benchclaw-chromium-1.0.0.zip`
3. Short description: **Tagline**; Detailed: **Long description**
4. Icon 64×64 + screenshots
5. Categories: *Developer Tools*
6. Submit. Review 1–5 days.

### 3. Visual Studio Marketplace
Publisher **Agnuxo** must exist. If not:
```bash
# On Azure DevOps, create Personal Access Token (PAT) scope "Marketplace → Manage"
# Then:
cd E:/OpenCLAW-4/benchclaw-integrations/vscode
npx --yes @vscode/vsce login Agnuxo          # paste PAT
npx --yes @vscode/vsce publish --packagePath ./benchclaw-vscode-1.0.0.vsix
```
Result: https://marketplace.visualstudio.com/items?itemName=Agnuxo.benchclaw-vscode

### 4. AI Agents Directory 2026 (aiagentslist.com)
1. https://aiagentslist.com/submit-agent
2. Name: **BenchClaw**
3. Category: *Benchmarking & Evaluation* · *MCP Servers*
4. URL: https://www.p2pclaw.com/app/benchmark
5. GitHub: https://github.com/Agnuxo1/benchclaw-integrations
6. Logo: `firefox-submissions/icon-512.png`
7. Description: **Long description**

### 5. MCP Market (mcpmarket.com)
1. https://mcpmarket.com/submit (or "Add Server")
2. Repo: `https://github.com/Agnuxo1/benchclaw-integrations/tree/main/mcp-server`
3. Install: `npx -y @agnuxo/benchclaw-mcp-server`
4. Tools: `benchclaw_register`, `benchclaw_submit_paper`, `benchclaw_leaderboard`
5. Transport: **stdio**
6. Description: **Medium description**

### 6. mcpservers.org
Usually accepts via PR to their GitHub catalog. If no form:
- Open issue titled `[Submit] BenchClaw` at their repo
- Body: paste **Medium description** + install command + tool list

### 7. Futurepedia (futurepedia.io)
1. https://www.futurepedia.io/submit-tool
2. Title: **BenchClaw**
3. Category: *Developer Tools*
4. Pricing: **Free**
5. Description: **Long description**
6. Website: https://www.p2pclaw.com/app/benchmark
7. Screenshots: 3× from `firefox-submissions/screenshots/`

### 8. There's An AI For That (theresanaiforthat.com)
1. https://theresanaiforthat.com/submit
2. Name: **BenchClaw**
3. Tags: *benchmark, evaluation, agents, llm, mcp, developer-tools*
4. Use case: *Benchmark and compare LLMs and AI agents*
5. Pricing: **Free**
6. Description: **Long description**

### 9. Toolify.ai
1. https://www.toolify.ai/submit
2. Category: *AI Developer Tools* · *AI Analytics Assistant*
3. Pricing: Free
4. Description + 3 screenshots

### 10. FutureTools (futuretools.io)
Email submission to matt@futuretools.io:
- Subject: `Tool submission — BenchClaw`
- Body: **Long description** + logo + link

### 11. AI Tools Directory (aitoolsdirectory.com)
1. https://aitoolsdirectory.com/submit-ai-tool
2. Same fields as above

### 12. Product Hunt (launch)
1. https://www.producthunt.com/posts/new
2. Name: **BenchClaw**
3. Tagline: **Tagline** (above)
4. Description: **Long description**
5. Topics: *Developer Tools · Artificial Intelligence · GitHub · Productivity*
6. Gallery:
   - Hero image 1270×760 with logo + "17-judge Tribunal scores any LLM or agent"
   - 3 screenshots from `firefox-submissions/screenshots/`
   - 1 demo GIF of MCP flow if possible
7. Maker: @Agnuxo1
8. Schedule launch for 00:01 PST on a Tuesday (optimal engagement)
9. Prepare 3 hunter replies and 5 maker comments ready for launch day.

### 13. Altern.ai
1. https://altern.ai/submit (or email support)
2. Fields identical to Toolify

### 14. Submit AI Tools (submitaitools.org)
1. https://submitaitools.org/submit-your-ai-tool
2. Free tier form

### 15. AIChief
1. https://aichief.com/submit (usually)
2. Category: *AI Dev Tools*

### 16. Openpedia / Twelve.tools
- Openpedia: usually closed-submission. Monitor https://openpedia.ai for submit link.
- Twelve.tools: https://twelve.tools/submit

### 17. Continue.dev hub
The Continue hub (hub.continue.dev) packages custom rules/commands as "Blocks".
Path: https://hub.continue.dev/new — paste the JSON from `continue/config.json`
in this repo as a Block (type = custom command), then publish under
`agnuxo/benchclaw`.

### 18. n8n Community Nodes featured listing
Once `n8n-nodes-benchclaw` is on npm:
1. https://github.com/n8n-io/n8n-docs → PR adding BenchClaw to
   `docs/integrations/community-nodes/installation.md` featured list, OR
2. Open issue at https://community.n8n.io asking for featured listing.

### 19. Dify / Langflow / Flowise plugin hubs
- **Dify**: PR to `langgenius/dify` adding our YAML under `api/core/tools/provider/builtin/benchclaw/`.
- **Langflow**: PR to `langflow-ai/langflow` under `src/backend/base/langflow/components/` adding `benchclaw_component.py`.
- **Flowise**: PR to `FlowiseAI/Flowise` under `packages/components/nodes/tools/BenchClaw/`.

### 20. GitHub Marketplace (Action)
Steps (user, one-time):
1. Push this repo, ensure `github-action/action.yml` is at repo root OR publish a dedicated repo `Agnuxo1/benchclaw-action` with the action.yml at root.
2. Go to repo → **Releases** → **Draft new release** → check "Publish this Action to the GitHub Marketplace".
3. Category: *Deployment* / *Utilities*.
4. Verify primary category, secondary: *AI Assisted*.

---

## ⚠️ Requires user credentials
- Edge Partner account (MSA)
- Opera developer account
- Azure DevOps PAT (`vsce login`)
- npm publish token (to register `benchclaw` and `@agnuxo/benchclaw-mcp-server`)
- PyPI token (for Python packages)
- Product Hunt maker account

Everything else above is ready-to-paste.
