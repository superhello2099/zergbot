# 🐛 ZergBot

**Deploy AI agents anywhere. Your models, your hardware, your rules.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why ZergBot?

Most AI agent frameworks lock you into cloud APIs. ZergBot doesn't.

- **Run on YOUR hardware** — 4090, 5090, A100, Mac M-series, or cloud
- **Use ANY model** — OpenAI, Claude, Llama, Qwen, or your custom fine-tuned models
- **Deploy in minutes** — `pip install` and go, no complex setup
- **Spawn swarms** — Create child agents for parallel tasks

```
┌─────────────────────────────────────────────────────┐
│  Your Model (local/cloud)                           │
│  ├── FLAMINGO, Llama, Qwen, GPT, Claude...         │
│  └── vLLM, Ollama, OpenAI-compatible API           │
└─────────────────────────────────────────────────────┘
                        ▲
                        │ OpenAI-compatible API
                        ▼
┌─────────────────────────────────────────────────────┐
│  🐛 ZergBot                                         │
│  ├── Agent Loop (tool calling, memory)             │
│  ├── Built-in Tools (files, shell, web, spawn)     │
│  ├── Channels (WhatsApp, Telegram)                 │
│  └── Cron Jobs (scheduled tasks)                   │
└─────────────────────────────────────────────────────┘
```

## Quick Start

```bash
pip install zergbot
zergbot onboard        # First-time setup
zergbot agent -m "What can you do?"
```

## Configuration

Edit `~/.zergbot/config.json`:

### Cloud API (OpenAI/Claude)

```json
{
  "providers": {
    "openai": {
      "apiKey": "sk-xxx",
      "apiBase": "https://api.openai.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o"
    }
  }
}
```

### Local Model (vLLM/Ollama)

```json
{
  "providers": {
    "openai": {
      "apiKey": "sk-local",
      "apiBase": "http://localhost:8000/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/your-model-name"
    }
  }
}
```

### GPU Server (A800/4090/5090)

```json
{
  "providers": {
    "openai": {
      "apiKey": "sk-local",
      "apiBase": "http://your-gpu-server:8885/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/flamingo-f2"
    }
  }
}
```

## Built-in Tools

| Tool         | What it does                     |
| ------------ | -------------------------------- |
| `read_file`  | Read any file                    |
| `write_file` | Create/overwrite files           |
| `edit_file`  | Surgical edits to existing files |
| `list_dir`   | Browse directories               |
| `exec`       | Run shell commands               |
| `web_search` | Search the internet              |
| `web_fetch`  | Fetch and parse web pages        |
| `spawn`      | Create child agents              |
| `message`    | Send to WhatsApp/Telegram        |

## Channels

Connect to messaging platforms:

```bash
# WhatsApp (scan QR code)
zergbot channels login

# Telegram (set bot token in config)
zergbot gateway
```

## Spawn Subagents

Create child agents for parallel work:

```python
# Agent automatically spawns helpers when needed
"Spawn an agent to research X while I work on Y"
```

## Cron Jobs

Schedule recurring tasks:

```bash
zergbot cron add "0 9 * * *" "Check my calendar and summarize today's meetings"
zergbot cron list
```

## Deployment Options

| Platform    | Command               |
| ----------- | --------------------- |
| Local dev   | `pip install -e .`    |
| Production  | `pip install zergbot` |
| Docker      | Coming soon           |
| API Gateway | `zergbot gateway`     |

## Philosophy

**Zerg Rush**: In StarCraft, Zerg wins by speed and numbers. ZergBot follows the same principle:

1. **Fast deployment** — Minutes, not hours
2. **Swarm capability** — Spawn agents as needed
3. **Hardware agnostic** — Run on whatever you have
4. **No vendor lock-in** — Switch models anytime

## License

MIT — Use it, fork it, sell it, whatever.

---

Built by [OpenClaw](https://github.com/openclaw). Part of the FLAMINGO ecosystem.
