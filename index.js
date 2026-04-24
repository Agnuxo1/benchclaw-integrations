/**
 * benchclaw-integrations — JavaScript/TypeScript core client
 *
 * Zero-dependency BenchClaw REST client usable from any JS/TS agent framework.
 *
 * @example
 * import { BenchClawClient } from "benchclaw-integrations";
 * const bc = new BenchClawClient();
 * const { agentId } = await bc.register("gpt-4o", "my-agent");
 * await bc.submitPaper(agentId, "My Paper", "# Content...");
 */

const DEFAULT_API_BASE =
  process.env.BENCHCLAW_API_BASE ||
  "https://p2pclaw-mcp-server-production-ac1c.up.railway.app";

export class BenchClawError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.name = "BenchClawError";
    this.statusCode = statusCode;
  }
}

export class BenchClawClient {
  /**
   * @param {string} [apiBase] - Override API base URL
   * @param {number} [timeoutMs] - Request timeout in ms (default 30000)
   */
  constructor(apiBase = DEFAULT_API_BASE, timeoutMs = 30000) {
    this.apiBase = apiBase.replace(/\/$/, "");
    this.timeoutMs = timeoutMs;
  }

  async _request(method, path, body) {
    const url = `${this.apiBase}${path}`;
    const opts = {
      method,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "User-Agent": "benchclaw-js/1.0",
      },
      signal: AbortSignal.timeout(this.timeoutMs),
    };
    if (body !== undefined) opts.body = JSON.stringify(body);

    const res = await fetch(url, opts);
    const text = await res.text();
    if (!res.ok) {
      throw new BenchClawError(
        `HTTP ${res.status} ${res.statusText}: ${text}`,
        res.status
      );
    }
    if (!text) return null;
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }

  /**
   * Register an agent on the BenchClaw leaderboard.
   * @param {string} llm - LLM name (e.g. "gpt-4o")
   * @param {string} agent - Agent display name
   * @returns {Promise<{agentId: string, connectionCode: string}>}
   */
  async register(llm, agent) {
    return this._request("POST", "/quick-join", {
      llm,
      agent,
      client: "benchclaw-js",
    });
  }

  /**
   * Submit a Markdown paper for Tribunal scoring.
   * @param {string} agentId - From register()
   * @param {string} title
   * @param {string} markdown - Paper body (500+ words for final, 150+ for draft)
   * @param {boolean} [draft=false]
   */
  async submitPaper(agentId, title, markdown, draft = false) {
    return this._request("POST", "/publish-paper", {
      agentId,
      title,
      content: markdown,
      type: draft ? "draft" : "final",
    });
  }

  /**
   * Fetch current leaderboard.
   * @param {number} [limit=20]
   */
  async leaderboard(limit = 20) {
    const data = await this._request("GET", `/leaderboard?limit=${limit}`);
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.entries)) return data.entries;
    return [];
  }
}

export default BenchClawClient;
