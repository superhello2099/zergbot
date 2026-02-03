# Teardown: Onboarding Experience

**Date**: 2025-02-04
**Target**: Dify (114K stars) vs CrewAI (34K stars)
**Goal**: 学习如何让用户 30 秒上手
**Depth**: Quick

---

## Executive Summary

**Dify 赢在"零设置"**：Cloud 版本让用户 0 秒体验，Docker 版本 3 分钟跑起来。

**CrewAI 赢在"CLI 体验"**：`crewai create crew` 一行命令生成完整项目结构。

**ZergBot 应该两者都学**：先做 Docker 一行启动，再考虑 Cloud playground。

---

## Dify (114K stars) Teardown

### Onboarding Path

```
用户看到 README
    ↓
两条路:
├─ Cloud (推荐): cloud.dify.ai → 0 秒开始
└─ Self-host: docker compose up -d → 3 分钟
    ↓
打开 localhost/install → 看到 Dashboard
    ↓
开始创建第一个 AI 应用
```

### Key Design Decisions

| 决策             | 为什么                         | 代价          | 评价 |
| ---------------- | ------------------------------ | ------------- | ---- |
| Cloud 优先       | 零门槛，用户先体验再决定自托管 | 需要运营成本  | 👍   |
| Docker Compose   | 不用配 Python 环境             | 需要装 Docker | 👍   |
| 可视化 Dashboard | 非技术用户也能用               | 开发成本高    | 👍   |
| .env.example     | 复制即用，不用手写配置         | -             | 👍   |

### Extractable Patterns

| 模式                    | ZergBot 可以用吗      |
| ----------------------- | --------------------- |
| "Zero setup" Cloud 版   | ⏳ Phase 2 (需要托管) |
| Docker Compose 一行启动 | ✅ Phase 1 立即做     |
| .env.example 模板       | ✅ 已有，可优化       |
| 可视化 Dashboard        | ⏳ 未来 (先 CLI)      |

---

## CrewAI (34K stars) Teardown

### Onboarding Path

```
用户看到 README
    ↓
pip install crewai
    ↓
crewai create crew my_project  ← 一行生成项目
    ↓
cd my_project && crewai run
    ↓
看到 AI agents 协作输出
```

### Key Design Decisions

| 决策        | 为什么                       | 代价           | 评价 |
| ----------- | ---------------------------- | -------------- | ---- |
| CLI 脚手架  | 新手不用从零写代码           | 需要维护模板   | 👍   |
| YAML 配置   | 非程序员也能改               | 学习成本       | 🤔   |
| 预置示例    | Trip Planner, Stock Analysis | 维护成本       | 👍   |
| 无 Cloud 版 | 专注开发者                   | 错过非技术用户 | 🤔   |

### Extractable Patterns

| 模式                        | ZergBot 可以用吗       |
| --------------------------- | ---------------------- |
| `crewai create crew` 脚手架 | ✅ 可做 `zergbot init` |
| 预置示例项目                | ✅ 必须有              |
| YAML agent 配置             | 🤔 考虑，但先 Python   |
| 视频教程链接                | ✅ Phase 2             |

---

## ZergBot Action Items

### Phase A1: Docker One-Liner (本周)

**目标**: `docker run zergbot/demo` 一行跑起来

**学 Dify**:

- 预配置 API key (用 OpenRouter 免费额度)
- 启动后自动打开浏览器
- 包含 3 个示例任务

**Dockerfile 草图**:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
ENV ZERGBOT_DEMO_MODE=1
ENV OPENROUTER_API_KEY=sk-or-demo-xxx  # 免费额度
EXPOSE 8080
CMD ["zergbot", "demo", "--web"]
```

### Phase A2: CLI 脚手架 (下周)

**学 CrewAI**:

```bash
zergbot init my-agent        # 生成项目结构
cd my-agent
zergbot run                  # 一行运行
```

**生成的结构**:

```
my-agent/
├── config.yaml      # Agent 配置
├── skills/          # 自定义 skills
├── main.py          # 入口
└── README.md        # 使用说明
```

### Phase A3: 示例项目 (下下周)

**学两家**:

1. **Meme Generator** — 输入话题，输出梗图
2. **Research Agent** — 输入问题，输出报告
3. **Code Helper** — 读代码，回答问题

---

## Comparison Matrix

| 特性             | Dify      | CrewAI | ZergBot (目标) |
| ---------------- | --------- | ------ | -------------- |
| Cloud Playground | ✅        | ❌     | ⏳ Phase 2     |
| Docker One-Liner | ✅        | ❌     | ✅ Phase A1    |
| CLI 脚手架       | ❌        | ✅     | ✅ Phase A2    |
| 预置示例         | ✅        | ✅     | ✅ Phase A3    |
| 可视化 UI        | ✅        | ❌     | ⏳ 未来        |
| Time to Value    | 0s / 3min | 5min   | 30s (目标)     |

---

## Next Steps

1. [ ] 创建 `Dockerfile` 和 `docker-compose.demo.yml`
2. [ ] 实现 `zergbot demo --web` 命令
3. [ ] 申请 OpenRouter 免费 API key 用于 demo
4. [ ] 写 3 个示例任务
5. [ ] 测试 "30 秒体验" 是否达成

---

_This teardown is a living document. Update as we build._
