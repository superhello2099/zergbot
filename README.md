# 🐛 ZergBot

> A lightweight AI agent framework - Rush your tasks with swarm intelligence

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

ZergBot is a lightweight (~4000 lines) AI agent framework that connects to any LLM backend. Like the Zerg swarm, it's fast, efficient, and can be deployed in large numbers.

**Part of the FLAMINGO ecosystem:**

- 🦩 **FLAMINGO** - The brain (LLM model)
- 🐛 **ZergBot** - The executor (agent framework)

## Features

- 🚀 **Lightweight** - Only ~4000 lines of code
- 🔌 **Any LLM Backend** - OpenAI, Claude, local models via OpenAI-compatible API
- 🛠️ **Built-in Tools** - File operations, shell commands, web search, and more
- 📱 **Multi-channel** - WhatsApp, Telegram support
- ⏰ **Cron Jobs** - Scheduled task execution
- 🐣 **Spawn Subagents** - Create child agents for parallel work

## Quick Start

```bash
# Install
pip install zergbot

# Initialize
zergbot onboard

# Chat with agent
zergbot agent -m "Hello, what can you do?"

# Start gateway API
zergbot gateway
```

## Configuration

Edit `~/.zergbot/config.json`:

```json
{
  "agents": {
    "defaults": {
      "model": "openai/gpt-4",
      "maxTokens": 8192
    }
  },
  "providers": {
    "openai": {
      "apiKey": "your-api-key",
      "apiBase": "https://api.openai.com/v1"
    }
  }
}
```

### Use with FLAMINGO (Local Model)

```json
{
  "providers": {
    "openai": {
      "apiKey": "sk-local",
      "apiBase": "http://your-server:8885/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/flamingo-f2"
    }
  }
}
```

## Tools

ZergBot comes with built-in tools:

| Tool         | Description             |
| ------------ | ----------------------- |
| `read_file`  | Read file contents      |
| `write_file` | Write to files          |
| `edit_file`  | Edit existing files     |
| `list_dir`   | List directory contents |
| `exec`       | Execute shell commands  |
| `web_search` | Search the web          |
| `web_fetch`  | Fetch web pages         |
| `spawn`      | Create subagents        |
| `message`    | Send messages           |

## Channels

Connect ZergBot to messaging platforms:

```bash
# WhatsApp
zergbot channels login

# Then scan QR code with WhatsApp
```

## Cron Jobs

Schedule recurring tasks:

```bash
zergbot cron add "0 9 * * *" "Good morning! Check my schedule."
zergbot cron list
```

## License

MIT License - Fork it, modify it, deploy it!

---

_🐛 Rush your tasks. Swarm intelligence at work._
