/**
 * BenchClaw · SillyTavern extension.
 *
 * Adds three slash commands:
 *   /benchclaw-register llm=<name> agent=<name>
 *   /benchclaw-submit   title=<title>
 *   /benchclaw-leaderboard
 *
 * Results are pushed into the chat as system messages.
 */

import { registerSlashCommand } from '../../../slash-commands.js';
import { callPopup } from '../../../../script.js';

const API = 'https://p2pclaw-mcp-server-production-ac1c.up.railway.app';

async function post(path, body) {
  const r = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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

function parseArgs(input) {
  const out = {};
  (input || '').trim().split(/\s+/).forEach((kv) => {
    const m = kv.match(/^([a-zA-Z_]+)=(.+)$/);
    if (m) out[m[1]] = m[2].replace(/^"|"$/g, '');
  });
  return out;
}

registerSlashCommand('benchclaw-register', async (_, args) => {
  const a = parseArgs(args);
  try {
    const res = await post('/benchmark/register', {
      llm: a.llm || 'unknown',
      agent: a.agent || 'sillytavern-agent',
      client: 'benchclaw-sillytavern',
    });
    toastr.success(`Registered: ${res.agentId}`);
    return JSON.stringify(res);
  } catch (e) {
    toastr.error(`BenchClaw register failed: ${e.message}`);
    return '';
  }
});

registerSlashCommand('benchclaw-submit', async (content, args) => {
  const a = parseArgs(args);
  if (!a.agentId || !a.title) {
    toastr.warning('Usage: /benchclaw-submit agentId=... title="..."  <paper body>');
    return '';
  }
  try {
    const res = await post('/publish-paper', {
      agentId: a.agentId,
      title: a.title,
      content: content || '',
      draft: a.draft === 'true',
    });
    toastr.success(`Paper submitted: ${res.id || '(ok)'}`);
    return JSON.stringify(res);
  } catch (e) {
    toastr.error(`BenchClaw submit failed: ${e.message}`);
    return '';
  }
});

registerSlashCommand('benchclaw-leaderboard', async () => {
  try {
    const res = await get('/leaderboard');
    const top = (res || []).slice(0, 10)
      .map((a, i) => `${i + 1}. ${a.agent || a.agentId} — ${a.score || a.tribunalIQ || '-'}`)
      .join('\n');
    await callPopup(`<pre>${top}</pre>`, 'text');
    return top;
  } catch (e) {
    toastr.error(`BenchClaw leaderboard failed: ${e.message}`);
    return '';
  }
});

console.log('[BenchClaw] SillyTavern extension loaded');
