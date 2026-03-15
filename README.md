# OpenClaw Config 🦞

**本仓库是虚拟机 OpenClaw（龙虾🦞）的一切配置、规则、脚本的唯一归档地。**

> 其他 AI（WorkBuddy 等）的相关文件存放在各自的仓库，与本仓库分开管理。

> **当前版本**：OpenClaw v2026.3.11 | **Gateway**：v2026.3.13 | **接入方式**：Tailscale HTTPS | **最后更新**：2026-03-15

---

## 📑 目录

- [整体架构](#整体架构)
- [各组件详解](#各组件详解)
  - [运行环境](#运行环境虚拟机)
  - [Tailscale 反向代理](#tailscale-反向代理怎么访问龙虾)
  - [Gateway（网关服务）](#gateway网关服务)
  - [规则文件体系（workspace）](#规则文件体系workspace)
  - [记忆体系（Memory）](#记忆体系memory)
  - [Memory Search（向量语义检索）](#memory-search向量语义检索)
  - [模型体系](#模型体系)
  - [心跳机制](#心跳机制)
  - [MCP 工具](#mcp-工具)
  - [Skills 技能文件](#skills-技能文件)
  - [飞书机器人](#飞书机器人)
  - [定时任务（规则同步）](#定时任务规则同步)
- [GitHub 仓库管理方案](#github-仓库管理方案)
- [文件结构](#文件结构)
- [龙虾现有能力 & 可提升方向](#龙虾现有能力--可提升方向)

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│  宿主机（Windows）                                                        │
│                                                                           │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────────────┐  │
│  │  WorkBuddy  │    │  飞书 PC 客户端   │    │  Windows 定时任务       │  │
│  │  (AI助手)   │    │  （主人使用）     │    │  每天 03:00            │  │
│  └──────┬──────┘    └────────┬─────────┘    │  从 GitHub 拉规则      │  │
│         │SSH                  │飞书API        └──────────┬─────────────┘  │
└─────────┼────────────────────┼────────────────────────  ─┼───────────────┘
          │                    │                            │
          ▼                    ▼                            ▼ SSH
┌─────────────────────────────────────────────────────────────────────────┐
│  虚拟机（Ubuntu，内网 192.168.x.x）                                       │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  openclaw-gateway（用户级 systemd 服务）                            │  │
│  │                                                                     │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │  │
│  │  │bind: loopback│  │  MCP 工具层   │  │  workspace/ 规则文件体系  │  │  │
│  │  │只听127.0.0.1 │  │ filesystem   │  │  AGENTS.md  AI_RULES.md  │  │  │
│  │  │不暴露公网    │  │ fetch        │  │  SOUL.md    USER.md       │  │  │
│  │  └─────────────┘  │ websearch    │  │  TOOLS.md   KNOWLEDGE_BASE│  │  │
│  │                    │ desktop-cmd  │  │  skills/（8个Skill文件）   │  │  │
│  │  ┌─────────────┐  └──────────────┘  └──────────────────────────┘  │  │
│  │  │ 飞书长连接   │                                                   │  │
│  │  │ 收消息→执行  │  ┌──────────────────────────────────────────┐   │  │
│  │  │ →回复        │  │  Memory Search（向量语义检索）             │   │  │
│  │  └─────────────┘  │                                          │   │  │
│  │                    │  ┌──────────────┐   ┌─────────────────┐  │   │  │
│  │                    │  │ 对话模型     │   │ Embedding 模型  │  │   │  │
│  │                    │  │ (StepFun/    │   │ Qwen            │  │   │  │
│  │                    │  │  Qwen/etc.)  │   │ text-embedding  │  │   │  │
│  │                    │  │ 生成回答     │   │ -v3             │  │   │  │
│  │                    │  └──────┬───────┘   │ 向量检索文档    │  │   │  │
│  │                    │         │ 接收检索到  └───────┬─────────┘  │   │  │
│  │                    │         │ 的上下文片段          │ 找相关文档  │   │  │
│  │                    │  ┌──────▼──────────────────────▼─────────┐  │   │  │
│  │                    │  │  SQLite 向量数据库（main.sqlite）       │  │   │  │
│  │                    │  │  65 文件 · 143 chunks · 1024维向量      │  │   │  │
│  │                    │  │  索引范围：memory/ + workspace/         │  │   │  │
│  │                    │  └────────────────────────────────────────┘  │   │  │
│  │                    └──────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  Tailscale（system 级 systemd 服务）                                    │  │
│  │  tailscale serve --bg → 把 127.0.0.1:port 转发到 HTTPS 公网地址        │  │
│  └─────────────────────────────────┬──────────────────────────────────────┘  │
└─────────────────────────────────────┼─────────────────────────────────────────┘
                                      │ HTTPS（加密，需 Tailscale 鉴权）
                                      ▼
                         https://xzy0626-vmware-virtual-platform
                                  .tail6f9a39.ts.net
                              （外网访问入口，脱敏展示）
```

---

## 各组件详解

### 运行环境（虚拟机）

| 项目 | 配置 |
|------|------|
| 操作系统 | Ubuntu Linux |
| 用户 | xzy0626 |
| 虚拟化方式 | VMware（跑在 Windows 宿主机上） |
| 内网 IP | 192.168.x.x（脱敏） |
| Node.js | v22.22.0 |
| Python | 3.12.3 |
| Git | 已配置，可直接 commit/push |

---

### Tailscale 反向代理（怎么访问龙虾）

**核心问题**：龙虾的 Gateway 只监听 `127.0.0.1`（本机回环），外网根本访问不到。
Tailscale 解决了这个问题：把本机服务「反向代理」到一个带 HTTPS 的公网地址。

**工作原理**：

```
外网设备
    │ HTTPS（TLS 自动签发）
    ▼
Tailscale 网络（只有加入了 tailnet 的设备才能访问）
    │
    ▼
虚拟机内的 Tailscale 守护进程
    │ tailscale serve --bg 命令把流量转发到本机
    ▼
127.0.0.1:PORT（gateway 只听本机）
    │
    ▼
OpenClaw Gateway（处理请求）
```

**关键配置细节**：

| 配置项 | 值 | 原因 |
|--------|-----|------|
| `gateway.bind` | `loopback`（只听 127.0.0.1） | 安全：不暴露公网端口 |
| `gateway.tailscale.mode` | `serve` | 让 Tailscale 做 HTTPS 代理 |
| Tailscale 服务级别 | `system`（系统级 systemd） | 开机自启，无需登录 |
| `tailscale serve` 服务类型 | `oneshot`（启动后进程退出） | 执行 `--bg` 后台注册即结束，serve 配置由 `tailscaled` 持久维护 |
| 对外 HTTPS 地址 | `.tail6f9a39.ts.net`（脱敏） | 固定域名，Tailscale 自动续签证书 |

> **注意**：`systemctl status tailscale-serve` 显示 `inactive` 是**正常现象**——该服务是 oneshot 类型，`ExecStart` 执行 `tailscale serve --bg 18789` 完成后进程退出，serve 代理持续运行中，`curl` 测试验证 HTTP 200。

---

### Gateway（网关服务）

**是什么**：OpenClaw 的核心进程，负责接收请求 → 调用 AI 模型 → 执行工具 → 返回响应。

**服务管理方式**：

```bash
# 查看状态
systemctl --user status openclaw-gateway

# 重启
systemctl --user restart openclaw-gateway

# 开机自启（已配置）
loginctl linger=yes   # 即使没登录，用户级 systemd 也会运行
```

**为什么用「用户级」而不是「系统级」systemd？**

系统级（`/etc/systemd/system/`）需要 D-Bus，在无头虚拟机（没有桌面环境）上会崩溃。用户级（`~/.config/systemd/user/`）+ `loginctl linger=yes` 可以实现同等的开机自启，且更稳定。

**Tailscale 则是系统级**，因为它不依赖 D-Bus，需要在任何用户登录前就启动。

**配置文件**：`~/.openclaw/openclaw.json`（含 API Key，严禁直接 cat 后展示）

---

### 规则文件体系（workspace）

**路径**：`~/.openclaw/workspace/`（`workspaceOnly: true`，文件操作默认限制在此）

这是龙虾的「大脑文件」。每次对话开始，龙虾读这些文件，就等于「想起来了」自己是谁、能做什么、不能做什么。

```
workspace/
├── AGENTS.md          ← 🔑 启动规程（最先读，最高优先级）
│                         v4：包含 L0 硬性拒绝表、启动检查清单
├── AI_RULES.md        ← ⛔ 安全规则（L0-L5 完整规则体系）
│                         v2.4.0-lobster，适配 Linux 环境
├── SOUL.md            ← 💙 龙虾的性格、原则、工作习惯、语气
├── USER.md            ← 👤 主人是谁、工作风格、基础设施（脱敏）
├── SELF_KNOWLEDGE.md  ← 🔍 龙虾的能力说明书（WorkBuddy 怎么配置的）
├── TOOLS.md           ← 🔧 工具使用规范（v3，含 MCP 工具决策树）
├── KNOWLEDGE_BASE.md  ← 📊 结构化状态快照（v1.1，比翻日志快得多）
└── skills/            ← 🎯 技能文件（见下节）
    ├── rules-loader.md
    ├── task-planner.md
    ├── workbuddy-dna.md
    ├── github-sync.md
    ├── feishu-file-reader.md
    ├── knowledge-notebook.md   ← 2026-03-15 新增
    ├── knowledge-ingest.md     ← 2026-03-15 新增
    └── scrapling/              ← 动态网页抓取（Playwright 支持）
```

**规则优先级**（从高到低）：
```
L0 (AI_RULES.md) > SOUL.md > USER.md > AGENTS.md > 用户请求
```

**每次对话启动流程**（自动执行，不需要主人说）：
```
1. [并行] 读 AI_RULES.md、SOUL.md、USER.md、SELF_KNOWLEDGE.md
2. [优先] 读 KNOWLEDGE_BASE.md（快速定位系统状态）
3. 读 memory/今天.md + 昨天.md（最近发生了什么）
4. 检查 round_counter.txt（每 10 轮重读规则）
5. 检查 rule_sync_time.txt（规则是否需要更新）
```

---

### 记忆体系（Memory）

**龙虾每次启动都是空白的**（模型上下文不持久），记忆体系解决了「上次做了什么」的问题。

```
workspace/memory/
├── YYYY-MM-DD.md                     ← 每日日记（对话结束时写入）
│   内容：今天做了什么、遇到什么问题、明天要做什么
│
├── 主题笔记.md                        ← 知识笔记（通过 knowledge-ingest 写入）
│   例：2026-03-15-note-openclaw-embedding-setup.md
│       2026-03-15-embedding-provider-strategy.md
│       2026-03-15-OpenClaw系统配置和技术说明.md
│
├── round_counter.txt                 ← 对话轮数计数器
│   作用：每 10 轮强制重读 AI_RULES.md，防止规则被「聊忘了」
│
├── rule_sync_time.txt                ← 规则最后同步时间
│   作用：超过 48 小时未同步 → 提醒主人检查定时任务
│
└── last_heartbeat.txt                ← 心跳时间戳
    作用：记录最近一次健康自检时间
```

> **注意安全规则**：`MEMORY.md`（长期重要记忆）只在**一对一私聊**中加载，群聊中不加载，防止个人信息泄露。

---

### Memory Search（向量语义检索）

这是 2026-03-15 正式投入运行的新能力，让龙虾可以从几十个文件里**语义搜索**相关内容，而不只是依赖有限的上下文窗口。

#### 工作原理

```
你对龙虾提问
      ↓
──────────────────────────────────────────────────────
[阶段 1]  Qwen text-embedding-v3 出场（Embedding 模型）
          把你的问题转成 1024 维向量
          例：[0.21, -0.83, 0.45, ... 共1024个]
          在 SQLite 向量数据库里找「距离最近」的文档块
          找到：memory/某笔记.md 里的相关段落
          相似度分数：0.40 ~ 0.75
──────────────────────────────────────────────────────
[阶段 2]  上下文拼装
          把找到的段落插入对话上下文：
          <memory>...找到的相关内容...</memory>
──────────────────────────────────────────────────────
[阶段 3]  对话模型出场（StepFun / Qwen / Hunter 等）
          收到：[找到的记忆片段] + [你的问题]
          生成回答
```

**关键点**：Embedding 模型和对话模型是**完全独立**的两件事，互不干扰，可以任意组合切换。

#### 当前配置

| 配置项 | 值 |
|--------|-----|
| Embedding 模型 | `Qwen text-embedding-v3`（阿里云 DashScope） |
| 向量维度 | 1024 |
| 数据库 | SQLite + `sqlite-vec` 插件 |
| 数据库路径 | `~/.openclaw/memory/main.sqlite` |
| 索引范围 | `memory/`（日记+笔记）+ `~/.openclaw/workspace/`（规则文件） |
| 当前索引量 | 65 文件 · 143 chunks |
| 状态 | ✅ Vector: ready，Embeddings: ready |

#### 为什么用 Qwen Embedding

| 方案 | 费用 | 中文效果 | 备注 |
|------|------|---------|------|
| **Qwen text-embedding-v3（当前）** | 0.0007元/千token，全量重建<2分钱 | ⭐⭐⭐⭐⭐ | **推荐，现用** |
| OpenAI text-embedding-3-small | $0.02/百万token | ⭐⭐⭐⭐ | 换 baseUrl+apiKey 即可 |
| Ollama nomic-embed-text | 完全免费 | ⭐⭐⭐ | 需虚拟机装 Ollama |
| Gemini text-embedding-004 | Google 大额免费额度 | ⭐⭐⭐ | 需 Google API Key |

> **费用监控**：阿里云百炼控制台 → 用量与账单 → [https://bailian.console.aliyun.com/](https://bailian.console.aliyun.com/)

#### 如何向记忆库投喂知识

| 方式 | 操作 | 适合场景 |
|------|------|---------|
| 直接粘贴 | 对龙虾说「存入记忆库，主题是XXX：[内容]」 | 短文本、笔记 |
| 飞书文档 | 「把这个飞书文档收录到知识库：[链接]」 | 长文档 |
| 本地文件 | 「把 /path/to/file.md 加入知识库」 | 现有文件 |
| 永久规则 | 让龙虾写进 AGENTS.md | 需每次遵守的规则 |

验证方式：让龙虾执行 `openclaw memory search "关键词"` 确认命中且 score > 0.4。

---

### 模型体系

龙虾配置了 22 个模型，覆盖多个平台，可按任务特点切换。

#### 配置总览

| 别名 | 模型 ID | 上下文 | 模态 | 平台 | 特点 |
|------|---------|--------|------|------|------|
| `qwen-max` | dashscope-qwen/qwen-max-latest | 31k | 文本 | 阿里云 | 高质量推理 |
| `qwen-plus` | dashscope-qwen/qwen-plus-latest | 128k | 文本 | 阿里云 | 均衡性价比 |
| `qwen-turbo` | dashscope-qwen/qwen-turbo-latest | 977k | 文本 | 阿里云 | 超长上下文 |
| `qwen-long` | dashscope-qwen/qwen-long | 9766k | 文本 | 阿里云 | 极长上下文 |
| `qwen-coder` | dashscope-qwen-coder/qwen2.5-coder-32b-instruct | 128k | 文本 | 阿里云 | 代码专用 |
| `qwq` | dashscope-reasoning/qwq-32b | 128k | 文本 | 阿里云 | 深度推理 |
| `qwen3` | dashscope-reasoning/qwen3-235b-a22b | 128k | 文本 | 阿里云 | MoE 大模型 |
| `qwen-vl` | dashscope-vision/qwen-vl-max-latest | 31k | 文本+图片 | 阿里云 | 视觉理解 |
| `deepseek-r1` | dashscope-deepseek/deepseek-r1 | 64k | 文本 | 阿里云路由 | 深度推理 |
| `deepseek-v3` | dashscope-deepseek/deepseek-v3 | 64k | 文本 | 阿里云路由 | 通用强模型 |
| `sf-deepseek-r1` | siliconflow/deepseek-ai/DeepSeek-R1 | 64k | 文本 | 硅基流动 | DeepSeek R1 备用 |
| `sf-deepseek-v3` | siliconflow/deepseek-ai/DeepSeek-V3 | 64k | 文本 | 硅基流动 | DeepSeek V3 备用 |
| `step-2` | stepfun/step-2-16k | 16k | 文本 | StepFun | 快速对话 |
| `step-1` | stepfun/step-1-8k | 8k | 文本 | StepFun | 轻量任务 |
| `minimax` | minimax/MiniMax-M2.5 | 200k | 文本 | MiniMax | 长上下文对话 |
| `minimax-fast` | minimax/MiniMax-M2.5-highspeed | 200k | 文本 | MiniMax | 高速版 |
| `minimax-text` | minimax/MiniMax-Text-01 | 977k | 文本 | MiniMax | 超长上下文 |
| `minimax-m1` | minimax/MiniMax-M1 | 977k | 文本 | MiniMax | M1 旗舰 |
| **`hunter-alpha`** | openrouter/openrouter/hunter-alpha | **1024k** | 文本 | OpenRouter | **完全免费，超长上下文** |
| **`healer-alpha`** | openrouter/openrouter/healer-alpha | 256k | 文本+图片 | OpenRouter | **完全免费，多模态** |
| `aliyun-qwen-turbo` | custom-dashscope/qwen-turbo-latest | 16k | 文本 | 自定义端点 | 备用路由 |

#### 模型切换方式

- **临时切换**：对龙虾说「切换到 hunter-alpha 处理这个任务」
- **默认模型**：修改 `openclaw.json` 中 `agents.defaults.model`
- **任务专用**：在 AGENTS.md 或 Skill 里指定特定任务使用特定模型

---

### 心跳机制

**当前状态**：`last_heartbeat.txt` 文件已存在，说明心跳写入机制已工作。

**心跳是什么**：定期自动触发的轻量检查任务（≤2 小时一次），确认：
- Gateway 服务是否存活
- 规则文件是否被篡改（检查 `AGENTS.md` 的 `MODIFIED v4` 标记）
- 规则同步时间是否超出阈值
- 写一条 memory 日记确认「我还活着」

**当前状态**：文件机制已落地，触发 cron job 仍待配置验证。

---

### MCP 工具

**MCP（Model Context Protocol）**：OpenClaw 连接外部工具的标准协议，每个 MCP Server 是一个独立进程，通过 stdio 和 gateway 通信。

| 工具 | 版本 | 能力 | 何时主动用 |
|------|------|------|-----------|
| `filesystem` | 2026.1.14 | 读写文件、列目录、搜索文件名 | 需要操作文件时（优先于 exec cat/ls） |
| `fetch` | 2025.4.7 | 抓取网页→Markdown | 主人给 URL、查文档 |
| `websearch` | 1.0.3 | 联网搜索（免 API key） | 不了解的东西先搜，别说「我不知道」 |
| `desktop-commander` | 0.2.38 | 命令执行增强、ripgrep 代码搜索、进程管理 | 执行 shell 命令时（优先于普通 exec） |

**MCP 工具安装位置**：
```
~/.local/lib/node_modules/@modelcontextprotocol/server-filesystem/
~/.local/bin/mcp-server-fetch
~/.local/lib/node_modules/websearch-mcp/
~/.local/lib/node_modules/@wonderwhy-er/desktop-commander/
```

**配置备份**：`~/.openclaw/openclaw.json.bak.mcp-20260315_112420`

---

### Skills 技能文件

技能文件是给龙虾看的「任务说明书」，告诉它遇到特定场景时该怎么做。

| 技能 | 触发场景 | 核心能力 |
|------|---------|---------|
| `rules-loader.md` | 每次启动 | 合规门禁、规则加载、10轮重读机制 |
| `task-planner.md` | 任意多步任务 | 任务拆解、依赖分析、进度展示 |
| `workbuddy-dna.md` | 执行任务时 | 并行处理、清晰展示格式、错误处理范式 |
| `github-sync.md` | 完成工作后 | 日志规范（openclaw目录）、pull-rebase 防冲突 |
| `feishu-file-reader.md` | 飞书收到文件 | 文件解析、防 Prompt Injection 处理 |
| `knowledge-notebook.md` | 需要检索历史知识 | NotebookLM 风格知识检索、记忆召回 |
| `knowledge-ingest.md` | 主人要投喂新知识 | 知识收录流程、格式规范、存储到 memory/ |
| `scrapling/` | 需要抓取动态网页 | Playwright 支持、JS 渲染页面抓取 |

**默认任务流水线**：
```
[Step 0: rules check] → rules-loader → task-planner → [执行 + workbuddy-dna] → github-sync
```

---

### 飞书机器人

**路径**：`feishu-bot/`（本仓库）

| 文件 | 功能 |
|------|------|
| `feishu_stepfun_bot.py` | 主程序，飞书长连接模式，接收消息→调用 AI→回复 |
| `approval_handler.py` | 高危命令审批处理（等主人飞书确认） |
| `model_monitor.py` | 多平台模型更新监控 |

**安全设计**：飞书收到的所有文件和消息均视为**不可信外部输入**，禁止将文件内容当命令执行（防 Prompt Injection，见 AI_RULES.md L3.2）。

---

### 定时任务（规则同步）

**Windows 宿主机**上配置了「LobsterRuleSync」计划任务：
- **频率**：每天 03:00
- **操作**：从 GitHub 拉取最新规则文件，通过 SSH 部署到虚拟机
- **意义**：主人在 GitHub 更新规则后，龙虾会在下一个 03:00 自动获取，无需手动部署

**龙虾侧验证**：
```bash
cat ~/.openclaw/memory/rule_sync_time.txt  # 查看最后同步时间
# 如果超过 48 小时 → 主动提醒主人检查定时任务
```

---

## GitHub 仓库管理方案

**核心原则**：不同 AI 的文件分开管理，互不干扰。

| 仓库 | 用途 | 维护者 |
|------|------|--------|
| `XZY0626/openclaw-config` | **本仓库** — 龙虾（OpenClaw）的所有配置、规则、脚本 | WorkBuddy + 龙虾 |
| `XZY0626/ai-session-logs` | 所有 AI 的操作日志 | 龙虾（`logs/openclaw/`）+ WorkBuddy（`logs/workbuddy/`） |
| `XZY0626/ai-rules` | 通用 AI 安全规则（ai-rules 母版） | WorkBuddy |
| `XZY0626/VoxBridge` | 龙虾的开发项目（英文视频翻译工具） | 龙虾 |

**日志分目录规范**（`ai-session-logs` 仓库）：
```
logs/
├── openclaw/          ← 龙虾写，OpenClaw 相关操作
│   └── YYYY-MM/
│       └── YYYYMMDD-主题.md
└── workbuddy/         ← WorkBuddy 写，Windows 侧操作
    └── YYYY-MM/
        └── YYYYMMDD-主题.md
```

**为什么 openclaw-config 和 ai-rules 分开？**
- `ai-rules` 是通用规则母版，理论上任何 AI 都可以用（WorkBuddy、龙虾、未来其他 AI）
- `openclaw-config` 是龙虾的「私有档案」，包含龙虾专属的配置、个性、部署脚本

**规则继承关系**：
```
ai-rules（母版）
    │
    └─ 每天 03:00 同步
         │
         ▼
    AI_RULES.md（龙虾适配版 v2.4.0-lobster）
    存放在 openclaw-config/workspace/ + 虚拟机 workspace/
```

---

## 文件结构

```
openclaw-config/
├── README.md                          ← 本文件（架构说明）
│
├── workspace/                         ← ⭐ 龙虾规则文件体系（虚拟机镜像）
│   ├── AGENTS.md                      ← 启动规程（v4，L0 硬性拒绝）
│   ├── AI_RULES.md                    ← 安全规则 v2.4.0-lobster
│   ├── SOUL.md                        ← 性格与原则
│   ├── USER.md                        ← 主人档案（脱敏）
│   ├── SELF_KNOWLEDGE.md              ← 龙虾自我认知（含 WorkBuddy 配置说明）
│   ├── TOOLS.md                       ← 工具使用规范（v3，含 MCP）
│   ├── KNOWLEDGE_BASE.md              ← 结构化状态快照（v1.1）
│   └── skills/                        ← 技能文件（8个）
│       ├── rules-loader.md
│       ├── task-planner.md
│       ├── workbuddy-dna.md
│       ├── github-sync.md
│       ├── feishu-file-reader.md
│       ├── knowledge-notebook.md      ← 2026-03-15 新增
│       ├── knowledge-ingest.md        ← 2026-03-15 新增
│       └── scrapling/                 ← 动态网页抓取
│
├── feishu-bot/                        ← 飞书机器人
│   ├── feishu_stepfun_bot.py
│   ├── approval_handler.py
│   ├── model_monitor.py
│   ├── check_models_task.bat
│   └── 启动机器人.bat
│
├── openclaw-frontend/                 ← 前端历史版本（v2026.3.8及以下）
│   ├── model-selector-v2.js
│   └── index.html
│
├── openclaw-scripts/                  ← 虚拟机端维护脚本
│   ├── backup.sh
│   ├── restore.sh
│   └── upgrade-watch.sh
│
├── openclaw-config/                   ← openclaw 配置参考
│   └── exec-approvals.json            ← 命令执行白名单
│
├── ssh-tools/                         ← 宿主机 SSH 管理工具
│   ├── ssh_cmd.py
│   ├── ssh_sudo.py
│   ├── ssh_sudo_batch.py
│   ├── ssh_read_config.py
│   ├── ssh_update_config.py
│   └── ssh_upload_approvals.py
│
└── deploy/                            ← 部署脚本
    ├── deploy_to_vm.py
    ├── setup_models.py
    ├── update_keys.py
    ├── inject_selector_v2.py          ← 历史版本
    └── fix_index.py                   ← 历史版本
```

---

## 龙虾现有能力 & 可提升方向

### ✅ 已落地的能力

| 能力 | 状态 | 说明 |
|------|------|------|
| 飞书对话 | ✅ 正常运行 | 长连接模式，实时收发消息 |
| 命令执行 | ✅ 正常运行 | exec + desktop-commander MCP |
| 文件读写 | ✅ 正常运行 | workspace 限制内 + filesystem MCP |
| 网页抓取 | ✅ 已安装 | fetch MCP（静态）+ scrapling Skill（动态/JS渲染） |
| 网络搜索 | ✅ 已安装 | websearch MCP（免费方案） |
| 合规门禁 | ✅ 运行中 | L0 硬性拒绝 + 10轮重读机制 |
| GitHub 日志同步 | ✅ 正常运行 | github-sync.md v3 + pull-rebase 规范 |
| 规则自动同步 | ✅ 已配置 | Windows 定时任务，每天 03:00 |
| 审批机制 | ✅ 已配置 | exec-approvals.json 白名单 |
| 版本自检 | ✅ 已配置 | AGENTS.md checksum + 启动时验证 |
| 记忆体系（日记） | ✅ 已配置 | memory/ 日记 + round_counter |
| **Memory Search** | ✅ **正式运行** | **Qwen text-embedding-v3，65文件143块，Vector ready** |
| **语义知识检索** | ✅ **正式运行** | **knowledge-notebook Skill，语义搜索历史记忆** |
| **知识投喂** | ✅ **正式运行** | **knowledge-ingest Skill，主人可随时向记忆库写入新知识** |
| **多模型体系** | ✅ **22个模型** | **含 Hunter/Healer Alpha（OpenRouter免费）、Qwen3、MiniMax M2.5等** |

### 🟡 有设计但未完全落地的能力

| 能力 | 设计位置 | 问题 | 建议 |
|------|---------|------|------|
| **心跳 cron 触发** | AGENTS.md + last_heartbeat.txt | 文件已存在，但触发 cron 未验证 | 在虚拟机上 `crontab -l` 确认是否有心跳任务 |
| **rule_sync_time.txt 验证** | AGENTS.md 启动检查清单第 8 项 | 文件格式是否被定时任务正确维护未验证 | 定时任务写入后验证文件内容格式是否正确 |
| **round_counter.txt** | AGENTS.md 第 7 项 | 龙虾能读写，但计数逻辑依赖龙虾自觉执行 | 可在 rules-loader.md 里加强检查逻辑 |
| **MEMORY.md（长期记忆）** | AGENTS.md Memory 章节 | 定义了但未见到有实际内容 | 安排龙虾做一次「整理长期记忆」任务，把之前操作日志里的重要内容提炼进去 |

### 🔮 已评估但暂未实施的升级

| 升级方向 | 触发条件 | 优先级 |
|---------|---------|--------|
| `@playwright/mcp` | fetch 抓不到 JS 渲染页面时（scrapling 已部分覆盖） | 中（遇到再装） |
| Tavily MCP | 需要更高质量搜索时 | 低（有 API key 再装） |
| n8n 工作流编排 | VM 内存≥8GB 或 VoxBridge 需对接第三方 API | 低 |
| 心跳 cron 配置 | 下次检查时顺手做掉 | 中 |
| 语音交互（STT/TTS） | VoxBridge pipeline 稳定后 | 未来 |

---

_本文档由 WorkBuddy 维护，所有 IP / 密钥 / Token 均已脱敏。_  
_最后更新：2026-03-15_
