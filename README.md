<div align="center">

<img src="assets/zergbot-logo-wide.png" alt="ZergBot Logo" width="500">

### Your AI, Your Rules

[![PyPI version](https://img.shields.io/pypi/v/zergbot.svg)](https://pypi.org/project/zergbot/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Personal AI agents that actually do what you want**

_Cloud AI says no. Your local AI says yes._

</div>

---

## What is ZergBot?

ZergBot is an open-source framework for building **personal AI agents** that run on your hardware with your choice of model.

Unlike cloud services with endless restrictions, ZergBot gives you **full control**:

- 🔓 **Your rules** — No corporate content policies
- 🏠 **Your hardware** — 4090, A100, Mac, or cloud
- 🤖 **Your model** — Llama, Qwen, Mistral, or any OpenAI-compatible API
- 💬 **Your channels** — Telegram, WhatsApp, or API

---

## Quick Start

```bash
pip install zergbot
zergbot init my-companion
cd my-companion
zergbot run
```

That's it. You have a personal AI companion.

---

## Templates

```bash
# Create different personalities
zergbot init buddy -t companion      # 💫 Warm and understanding
zergbot init rp -t roleplay          # 🎭 Immersive characters
zergbot init chaos-bot -t chaos      # 🌀 Unpredictable and wild
```

**Hint:** There are more templates. Try `zergbot unlock` to find them.

---

## Local Models (Recommended)

For the full experience, use local models:

```bash
# With Ollama
ollama pull llama3.3
zergbot init my-ai -t companion
# Edit config.yaml: model: ollama/llama3.3
zergbot run

# With vLLM
zergbot init my-ai -t companion
# Edit config.yaml: model: local, api_base: http://localhost:8000/v1
zergbot run
```

Local models = **no filters, no limits, no judgment**.

---

## Why "Zerg"?

In StarCraft, the Zerg swarm wins through:

| Principle  | Implementation          |
| ---------- | ----------------------- |
| **Speed**  | Deploy in seconds       |
| **Swarm**  | Spawn multiple agents   |
| **Adapt**  | Any hardware, any model |
| **Evolve** | Your rules, your way    |

---

## Features

- ✅ **Multi-Channel** — Telegram and WhatsApp
- ✅ **Memory** — Remembers conversations
- ✅ **Tools** — Files, shell, web search
- ✅ **Subagents** — Spawn child agents
- ✅ **Scheduler** — Cron-based tasks
- ✅ **Local-First** — Ollama, vLLM, LM Studio

---

## Configuration

Edit `config.yaml` in your project:

```yaml
name: my-companion
model: ollama/llama3.3 # or any OpenAI-compatible endpoint
provider:
  type: ollama
  api_base: http://localhost:11434
```

---

## Channels

### Telegram

```bash
# In your project directory
zergbot channels telegram --token YOUR_BOT_TOKEN
zergbot gateway
```

### WhatsApp

```bash
zergbot channels login
# Scan QR code
zergbot gateway
```

---

## License

MIT — Use it however you want.

---

<div align="center">

**Built for those who want more from AI.**

[GitHub](https://github.com/superhello2099/zergbot) • [Issues](https://github.com/superhello2099/zergbot/issues)

</div>
