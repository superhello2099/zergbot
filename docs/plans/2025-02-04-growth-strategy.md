# ZergBot Growth Strategy

> Brainstorm session: 2025-02-04
> Status: Planning

---

## Problem Statement

AI agent 框架市场同质化严重（LangChain, AutoGPT, CrewAI, OpenAI Agents SDK...）

ZergBot 如何脱颖而出？

---

## Current State

- ~5000 LOC Python framework
- Subagents, multi-channel (WhatsApp/Telegram)
- Hardware agnostic (4090/5090/A100/Mac/Cloud)
- Model agnostic (any OpenAI-compatible API)
- Built-in tools + Cron + API Gateway

---

## Core Problem Identified

> "搞一堆设置，搞半天设置不好"
> "人家要一用就有反馈才能去用"

**Time to First Value 太长** — 用户还没体验到价值就放弃了

---

## Strategy: A then B

### Phase A: Zero-Config Demo (优先)

**Goal**: 让用户 30 秒内体验到 ZergBot 能干嘛

**Options**:

| 方案               | 实现                      | Time to Value |
| ------------------ | ------------------------- | ------------- |
| Online Playground  | 网页版，不用装任何东西    | 0 秒          |
| One-Click Docker   | `docker run zergbot/demo` | 30 秒         |
| Public Discord Bot | 加入频道直接用            | 0 秒          |

**Recommended**: Start with Docker demo, then add web playground

### Phase B: 借力增长 (后续)

**Goal**: 找到有文化性、好玩的场景

**Candidates**:

| 项目           | Why                 |
| -------------- | ------------------- |
| Meme Generator | 病毒传播，文化性强  |
| AI Town        | NPC 模拟，a16z 背书 |
| Discord Bot    | 直达游戏/技术社区   |

---

## Differentiation Points

1. **硬件自由** — 跑在任何硬件上（4090/5090/A100/Mac）
2. **极简** — 5000 LOC vs LangChain 200K+ LOC
3. **Subagent Swarm** — 像 Zerg 一样并行 spawn
4. **消息渠道** — WhatsApp/Telegram 原生集成

---

## Open Source Projects to Integrate

| Project                                                                                 | Stars | Use Case        |
| --------------------------------------------------------------------------------------- | ----- | --------------- |
| [AI Town](https://github.com/a16z-infra/ai-town)                                        | 9K    | NPC simulation  |
| [memegen](https://github.com/jacebrowning/memegen)                                      | -     | Meme API        |
| [Full-Stack-AI-Meme-Generator](https://github.com/ThioJoe/Full-Stack-AI-Meme-Generator) | -     | GPT + images    |
| [Discord.py](https://github.com/Rapptz/discord.py)                                      | 6.7K  | Community reach |
| [CrewAI](https://github.com/crewAIInc/crewAI)                                           | 34K   | Multi-agent     |

---

## Next Steps

1. [ ] Design Phase A: Zero-config demo
2. [ ] Build Docker one-liner
3. [ ] Test with real users
4. [ ] Iterate based on feedback
5. [ ] Phase B: Pick one integration and build it

---

_This is a living document. Iterate, don't over-plan._
