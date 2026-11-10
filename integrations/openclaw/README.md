# OpenClaw Integration

OpenClaw agents are installed as workspaces containing `SOUL.md`, `AGENTS.md`,
and `IDENTITY.md` files. The installer copies each workspace into
`~/.openclaw/agency-agents/` and registers it when the `openclaw` CLI is
available.

Before installing, generate the OpenClaw workspaces:

```bash
# Bash (Linux / macOS)
./scripts/convert.sh --tool openclaw

# Or Cross-platform Python (Windows / macOS / Linux)
python scripts/convert_openclaw.py
```

## Install

```bash
./scripts/install.sh --tool openclaw
```

## Activate an Agent

After installation, agents are available by `agentId` in OpenClaw sessions.

If the OpenClaw gateway is already running, restart it after installation:

```bash
openclaw gateway restart
```

## Regenerate

```bash
./scripts/convert.sh --tool openclaw
```
