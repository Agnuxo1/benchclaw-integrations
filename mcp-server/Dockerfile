# ── Build stage ────────────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies (including devDependencies for tsc)
COPY package*.json ./
RUN npm ci

# Compile TypeScript → dist/
COPY tsconfig.json ./
COPY src/ ./src/
RUN npm run build

# ── Runtime stage ───────────────────────────────────────────────────────────────
FROM node:22-alpine

WORKDIR /app

# Copy compiled output and install only production deps
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --omit=dev

# Allow overriding the P2PCLAW API endpoint at runtime
ENV BENCHCLAW_API_BASE=https://p2pclaw-mcp-server-production-ac1c.up.railway.app

# MCP stdio server — clients connect via stdin/stdout
CMD ["node", "dist/index.js"]
