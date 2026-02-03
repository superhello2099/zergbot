<div align="center">

<img src="assets/zergbot-logo-wide.png" alt="ZergBot Logo" width="500">

### Open-Source AI Agent Framework for Any Hardware

[![PyPI version](https://img.shields.io/pypi/v/zergbot.svg)](https://pypi.org/project/zergbot/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/superhello2099/zergbot?style=social)](https://github.com/superhello2099/zergbot)

**Deploy AI agents on 4090 • 5090 • A100 • Mac • Cloud — with any LLM backend**

[Installation](#installation) • [Quick Start](#quick-start) • [Features](#features) • [Documentation](#documentation)

</div>

---

## What is ZergBot?

ZergBot is an **open-source AI agent framework** that runs on any hardware with any OpenAI-compatible model. Unlike cloud-locked frameworks, ZergBot gives you full control over your AI infrastructure.

```
┌──────────────────────────────────────────────────────────────┐
│  LLM Backend (your choice)                                   │
│  GPT-4 • Claude • Llama • Qwen • Mistral • Custom Models     │
│  via OpenAI API • vLLM • Ollama • LM Studio                  │
└──────────────────────────────────────────────────────────────┘
                              ▲
                              │ OpenAI-compatible API
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  🐛 ZergBot Agent Framework                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ Agent Loop  │ │ Tool System │ │ Memory      │            │
│  │ • Planning  │ │ • Files     │ │ • Session   │            │
│  │ • Execution │ │ • Shell     │ │ • Long-term │            │
│  │ • Reflection│ │ • Web       │ │ • Context   │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ Channels    │ │ Subagents   │ │ Scheduler   │            │
│  │ • WhatsApp  │ │ • Spawn     │ │ • Cron Jobs │            │
│  │ • Telegram  │ │ • Parallel  │ │ • Heartbeat │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## Features

- ✅ **Hardware Agnostic** — Run on NVIDIA (4090/5090/A100/A800), Apple Silicon, or cloud
- ✅ **Model Agnostic** — OpenAI, Anthropic, Llama, Qwen, or any OpenAI-compatible API
- ✅ **Built-in Tools** — File operations, shell commands, web search, web fetch
- ✅ **Subagent Spawning** — Create child agents for parallel task execution
- ✅ **Multi-Channel** — WhatsApp and Telegram integration
- ✅ **Scheduled Tasks** — Cron-based job scheduling
- ✅ **Session Memory** — Persistent conversation history
- ✅ **Extensible Skills** — Add custom capabilities via skill files
- ✅ **API Gateway** — REST API for external integrations

---

## Installation

```bash
pip install zergbot
```

Or install from source:

```bash
git clone https://github.com/superhello2099/zergbot.git
cd zergbot
pip install -e .
```

---

## Quick Start

```bash
# First-time setup
zergbot onboard

# Chat with your agent
zergbot agent -m "What can you do?"
```

**Example Output:**

```
$ zergbot agent -m "Create a hello world Python script"

🐛 I'll create a hello world script for you.

[Tool: write_file] Writing to /tmp/hello.py...
[Tool: exec] Running: python /tmp/hello.py

Output:
Hello, World!

Done! The script has been created and executed successfully.
```

---

## Configuration

Edit `~/.zergbot/config.json`:

<details>
<summary><b>Cloud API (OpenAI/Claude)</b></summary>

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

</details>

<details>
<summary><b>Local Model (vLLM/Ollama/LM Studio)</b></summary>

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
      "model": "openai/llama-3.1-70b"
    }
  }
}
```

</details>

<details>
<summary><b>GPU Server (A800/4090/5090)</b></summary>

```json
{
  "providers": {
    "openai": {
      "apiKey": "sk-local",
      "apiBase": "http://your-gpu-server:8000/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/your-model"
    }
  }
}
```

</details>

---

## Built-in Tools

| Tool         | Description               | Example                         |
| ------------ | ------------------------- | ------------------------------- |
| `read_file`  | Read file contents        | Read config files, logs, code   |
| `write_file` | Create or overwrite files | Generate scripts, save data     |
| `edit_file`  | Surgical edits to files   | Fix bugs, update configs        |
| `list_dir`   | List directory contents   | Browse project structure        |
| `exec`       | Execute shell commands    | Run scripts, git operations     |
| `web_search` | Search the internet       | Research, find documentation    |
| `web_fetch`  | Fetch and parse web pages | Extract content, scrape data    |
| `spawn`      | Create subagents          | Parallel task execution         |
| `message`    | Send messages             | WhatsApp/Telegram notifications |

---

## Channels

### WhatsApp

```bash
zergbot channels login
# Scan QR code with WhatsApp
```

### Telegram

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Add token to `~/.zergbot/config.json`:
   ```json
   {
     "channels": {
       "telegram": {
         "enabled": true,
         "token": "your-bot-token"
       }
     }
   }
   ```
3. Start gateway: `zergbot gateway`

---

## Subagent Spawning

ZergBot can spawn child agents for parallel work:

```bash
zergbot agent -m "Spawn an agent to research Python async patterns while you write a summary of JavaScript promises"
```

The main agent coordinates while subagents work in parallel.

---

## Scheduled Tasks

```bash
# Add a daily task
zergbot cron add "0 9 * * *" "Summarize my calendar for today"

# List scheduled tasks
zergbot cron list

# Remove a task
zergbot cron remove <job-id>
```

---

## API Gateway

Start the REST API server:

```bash
zergbot gateway --host 0.0.0.0 --port 8080
```

Endpoints:

- `POST /chat` — Send message to agent
- `GET /health` — Health check
- `GET /sessions` — List sessions

---

## Why "Zerg"?

In StarCraft, the Zerg swarm wins through **speed** and **numbers**. ZergBot follows the same philosophy:

| Principle  | Implementation                          |
| ---------- | --------------------------------------- |
| **Speed**  | Deploy in minutes, not hours            |
| **Swarm**  | Spawn multiple agents for parallel work |
| **Adapt**  | Run on any hardware, use any model      |
| **Evolve** | Extensible skill system                 |

---

## Roadmap

- [x] Core agent loop
- [x] Tool system
- [x] WhatsApp/Telegram channels
- [x] Subagent spawning
- [x] Cron scheduling
- [ ] Docker image
- [ ] Web UI
- [ ] Plugin marketplace

---

## Contributing

Contributions welcome! Please read our contributing guidelines (coming soon).

```bash
# Development setup
git clone https://github.com/superhello2099/zergbot.git
cd zergbot
pip install -e ".[dev]"
```

---

## License

MIT License — Use it, fork it, modify it, sell it.

---

<div align="center">

**Built by [NATIVE2099](https://github.com/superhello2099)**

[Report Bug](https://github.com/superhello2099/zergbot/issues) • [Request Feature](https://github.com/superhello2099/zergbot/issues)

</div>
