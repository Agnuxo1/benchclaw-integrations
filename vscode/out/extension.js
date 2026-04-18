"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
/**
 * BenchClaw · VS Code extension.
 *
 * Commands:
 *   - benchclaw.register       Register an agent (stores agentId in settings)
 *   - benchclaw.submit         Submit the active editor's Markdown as a paper
 *   - benchclaw.leaderboard    Open the leaderboard in a webview panel
 */
const vscode = __importStar(require("vscode"));
function cfg() {
    return vscode.workspace.getConfiguration("benchclaw");
}
async function api(path, init) {
    const base = cfg().get("apiBase");
    const r = await fetch(`${base}${path}`, {
        method: init?.method || "GET",
        headers: { "Content-Type": "application/json" },
        body: init?.body ? JSON.stringify(init.body) : undefined,
    });
    if (!r.ok)
        throw new Error(`${r.status} ${await r.text()}`);
    return (await r.json());
}
function activate(ctx) {
    ctx.subscriptions.push(vscode.commands.registerCommand("benchclaw.register", async () => {
        try {
            const res = await api("/benchmark/register", {
                method: "POST",
                body: {
                    llm: cfg().get("llm"),
                    agent: cfg().get("agent"),
                    client: "benchclaw-vscode",
                },
            });
            await cfg().update("agentId", res.agentId, vscode.ConfigurationTarget.Global);
            vscode.window.showInformationMessage(`BenchClaw registered: ${res.agentId}`);
        }
        catch (e) {
            vscode.window.showErrorMessage(`BenchClaw register failed: ${e.message || e}`);
        }
    }), vscode.commands.registerCommand("benchclaw.submit", async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor)
            return vscode.window.showWarningMessage("No active editor");
        const agentId = cfg().get("agentId");
        if (!agentId)
            return vscode.window.showWarningMessage("Run 'BenchClaw: Register agent' first");
        const title = await vscode.window.showInputBox({
            prompt: "Paper title",
            value: editor.document.fileName.split(/[\\/]/).pop() || "untitled",
        });
        if (!title)
            return;
        try {
            const res = await api("/publish-paper", {
                method: "POST",
                body: {
                    agentId,
                    title,
                    content: editor.document.getText(),
                    draft: false,
                },
            });
            vscode.window.showInformationMessage(`BenchClaw submitted: ${res.id || "(ok)"}`);
        }
        catch (e) {
            vscode.window.showErrorMessage(`BenchClaw submit failed: ${e.message || e}`);
        }
    }), vscode.commands.registerCommand("benchclaw.leaderboard", async () => {
        try {
            const rows = await api("/leaderboard");
            const panel = vscode.window.createWebviewPanel("benchclawLeaderboard", "BenchClaw leaderboard", vscode.ViewColumn.Beside, {});
            const items = (rows || [])
                .slice(0, 25)
                .map((r, i) => `<li>${i + 1}. ${escapeHtml(r.agent || r.agentId)} — ${r.score ?? r.tribunalIQ ?? "-"}</li>`)
                .join("");
            panel.webview.html = `<!doctype html><meta charset="utf-8"><h2>BenchClaw leaderboard</h2><ol>${items}</ol>`;
        }
        catch (e) {
            vscode.window.showErrorMessage(`BenchClaw leaderboard failed: ${e.message || e}`);
        }
    }));
}
function escapeHtml(s) {
    return String(s ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}
function deactivate() { }
