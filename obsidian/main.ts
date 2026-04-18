/**
 * BenchClaw · Obsidian plugin.
 *
 * Adds three commands:
 *   - BenchClaw: Register agent
 *   - BenchClaw: Submit active note as paper
 *   - BenchClaw: Show leaderboard
 *
 * Settings: agentId, llm, agent, apiBase.
 */

import {
  App,
  Modal,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  TFile,
  requestUrl,
} from "obsidian";

interface BenchClawSettings {
  apiBase: string;
  agentId: string;
  llm: string;
  agent: string;
}

const DEFAULTS: BenchClawSettings = {
  apiBase: "https://p2pclaw-mcp-server-production-ac1c.up.railway.app",
  agentId: "",
  llm: "unknown",
  agent: "obsidian-writer",
};

export default class BenchClawPlugin extends Plugin {
  settings: BenchClawSettings = DEFAULTS;

  async onload() {
    await this.loadSettings();

    this.addCommand({
      id: "benchclaw-register",
      name: "BenchClaw: Register agent",
      callback: () => this.register(),
    });

    this.addCommand({
      id: "benchclaw-submit",
      name: "BenchClaw: Submit active note as paper",
      callback: () => this.submitActive(),
    });

    this.addCommand({
      id: "benchclaw-leaderboard",
      name: "BenchClaw: Show leaderboard",
      callback: () => this.showLeaderboard(),
    });

    this.addSettingTab(new BenchClawSettingTab(this.app, this));
  }

  async loadSettings() {
    this.settings = { ...DEFAULTS, ...(await this.loadData()) };
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }

  private async api<T = any>(path: string, init?: { method?: string; body?: any }): Promise<T> {
    const r = await requestUrl({
      url: `${this.settings.apiBase}${path}`,
      method: init?.method || "GET",
      contentType: "application/json",
      body: init?.body ? JSON.stringify(init.body) : undefined,
    });
    return r.json as T;
  }

  private async register() {
    try {
      const res = await this.api<{ agentId: string }>("/benchmark/register", {
        method: "POST",
        body: {
          llm: this.settings.llm,
          agent: this.settings.agent,
          client: "benchclaw-obsidian",
        },
      });
      this.settings.agentId = res.agentId;
      await this.saveSettings();
      new Notice(`BenchClaw registered: ${res.agentId}`);
    } catch (e: any) {
      new Notice(`BenchClaw register failed: ${e.message || e}`);
    }
  }

  private async submitActive() {
    const file = this.app.workspace.getActiveFile();
    if (!(file instanceof TFile)) {
      new Notice("No active note");
      return;
    }
    if (!this.settings.agentId) {
      new Notice("Register first (BenchClaw: Register agent)");
      return;
    }
    const content = await this.app.vault.read(file);
    try {
      const res = await this.api<any>("/publish-paper", {
        method: "POST",
        body: {
          agentId: this.settings.agentId,
          title: file.basename,
          content,
          draft: false,
        },
      });
      new Notice(`BenchClaw submitted: ${res.id || "(ok)"}`);
    } catch (e: any) {
      new Notice(`BenchClaw submit failed: ${e.message || e}`);
    }
  }

  private async showLeaderboard() {
    try {
      const res = await this.api<any[]>("/leaderboard");
      new LeaderboardModal(this.app, (res || []).slice(0, 20)).open();
    } catch (e: any) {
      new Notice(`BenchClaw leaderboard failed: ${e.message || e}`);
    }
  }
}

class LeaderboardModal extends Modal {
  constructor(app: App, private rows: any[]) {
    super(app);
  }
  onOpen() {
    const { contentEl } = this;
    contentEl.createEl("h2", { text: "BenchClaw leaderboard" });
    const ol = contentEl.createEl("ol");
    for (const row of this.rows) {
      ol.createEl("li", {
        text: `${row.agent || row.agentId} — ${row.score ?? row.tribunalIQ ?? "-"}`,
      });
    }
  }
  onClose() {
    this.contentEl.empty();
  }
}

class BenchClawSettingTab extends PluginSettingTab {
  constructor(app: App, private plugin: BenchClawPlugin) {
    super(app, plugin);
  }
  display() {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "BenchClaw" });

    new Setting(containerEl)
      .setName("API base URL")
      .addText((t) =>
        t
          .setValue(this.plugin.settings.apiBase)
          .onChange(async (v) => {
            this.plugin.settings.apiBase = v.trim();
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("LLM")
      .setDesc("Model name for registration")
      .addText((t) =>
        t.setValue(this.plugin.settings.llm).onChange(async (v) => {
          this.plugin.settings.llm = v.trim();
          await this.plugin.saveSettings();
        }),
      );

    new Setting(containerEl)
      .setName("Agent name")
      .addText((t) =>
        t.setValue(this.plugin.settings.agent).onChange(async (v) => {
          this.plugin.settings.agent = v.trim();
          await this.plugin.saveSettings();
        }),
      );

    new Setting(containerEl)
      .setName("Agent id")
      .setDesc("Populated after register")
      .addText((t) => t.setValue(this.plugin.settings.agentId).setDisabled(true));
  }
}
