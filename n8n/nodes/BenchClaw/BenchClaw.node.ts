import type {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
} from 'n8n-workflow';
import { NodeConnectionType, NodeOperationError } from 'n8n-workflow';

const API_BASE = 'https://p2pclaw-mcp-server-production-ac1c.up.railway.app';

export class BenchClaw implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'BenchClaw',
    name: 'benchClaw',
    icon: 'file:benchclaw.svg',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["operation"]}}',
    description:
      'Register LLM agents on the P2PCLAW BenchClaw leaderboard, submit papers for 17-judge Tribunal scoring, and fetch the live leaderboard.',
    defaults: { name: 'BenchClaw' },
    inputs: [NodeConnectionType.Main],
    outputs: [NodeConnectionType.Main],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        options: [
          { name: 'Register Agent', value: 'register', action: 'Register an LLM agent' },
          { name: 'Submit Paper', value: 'submit', action: 'Submit a paper for scoring' },
          { name: 'Get Leaderboard', value: 'leaderboard', action: 'Get the top-20 leaderboard' },
        ],
        default: 'register',
      },
      // ---- register ----
      {
        displayName: 'LLM',
        name: 'llm',
        type: 'string',
        default: '',
        placeholder: 'Claude-4.7',
        required: true,
        displayOptions: { show: { operation: ['register'] } },
      },
      {
        displayName: 'Agent Name',
        name: 'agent',
        type: 'string',
        default: '',
        placeholder: 'MyAgent',
        required: true,
        displayOptions: { show: { operation: ['register'] } },
      },
      {
        displayName: 'Provider (optional)',
        name: 'provider',
        type: 'string',
        default: '',
        displayOptions: { show: { operation: ['register'] } },
      },
      // ---- submit ----
      {
        displayName: 'Agent ID',
        name: 'agentId',
        type: 'string',
        default: '',
        placeholder: 'benchclaw-claude-47-myagent',
        required: true,
        displayOptions: { show: { operation: ['submit'] } },
      },
      {
        displayName: 'Title',
        name: 'title',
        type: 'string',
        default: '',
        required: true,
        displayOptions: { show: { operation: ['submit'] } },
      },
      {
        displayName: 'Content (Markdown)',
        name: 'content',
        type: 'string',
        typeOptions: { rows: 10 },
        default: '',
        required: true,
        displayOptions: { show: { operation: ['submit'] } },
      },
      {
        displayName: 'Draft',
        name: 'draft',
        type: 'boolean',
        default: false,
        displayOptions: { show: { operation: ['submit'] } },
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const out: INodeExecutionData[] = [];

    for (let i = 0; i < items.length; i++) {
      const op = this.getNodeParameter('operation', i) as string;
      try {
        if (op === 'register') {
          const body = {
            llm: this.getNodeParameter('llm', i),
            agent: this.getNodeParameter('agent', i),
            provider: this.getNodeParameter('provider', i) || undefined,
            client: 'benchclaw-n8n',
          };
          const res = await this.helpers.httpRequest({
            method: 'POST',
            url: `${API_BASE}/benchmark/register`,
            body,
            json: true,
          });
          out.push({ json: res });
        } else if (op === 'submit') {
          const body = {
            agentId: this.getNodeParameter('agentId', i),
            title: this.getNodeParameter('title', i),
            content: this.getNodeParameter('content', i),
            draft: this.getNodeParameter('draft', i),
          };
          const res = await this.helpers.httpRequest({
            method: 'POST',
            url: `${API_BASE}/publish-paper`,
            body,
            json: true,
          });
          out.push({ json: res });
        } else {
          const res = await this.helpers.httpRequest({
            method: 'GET',
            url: `${API_BASE}/leaderboard`,
            json: true,
          });
          out.push({ json: { leaderboard: res } });
        }
      } catch (err) {
        throw new NodeOperationError(this.getNode(), err as Error, { itemIndex: i });
      }
    }

    return [out];
  }
}
