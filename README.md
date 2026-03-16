# OpenClaw Config 🦞

**本仓库是虚拟机 OpenClaw（龙虾🦞）的一切配置、规则、脚本的唯一归档地。**

> 其他 AI（WorkBuddy 等）的相关文件存放在各自的仓库，与本仓库分开管理。

> **当前版本**：OpenClaw v2026.3.11 | **Gateway**：v2026.3.13 | **接入方式**：Tailscale HTTPS | **最后更新**：2026-03-16（安全加固 v2.5.1：删除 .pre-disable-auth 认证旁路、AGENTS.md 补全技能注册表、README 新增 Skills/Capabilities/Extensions 完整说明）

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
  - [学术搜索工具](#学术搜索工具academic_searchpy)
  - [能力激活可靠性说明](#能力激活可靠性说明)
  - [飞书机器人](#飞书机器人)
  - [定时任务（规则同步）](#定时任务规则同步)
- [GitHub 仓库管理方案](#github-仓库管理方案)
- [文件结构](#文件结构)
- [龙虾现有能力全景](#龙虾现有能力全景)
  - [Skills 技能文件（共 9 个）](#-skills-技能文件共-9-个)
  - [Capabilities 内置能力](#-capabilities-内置能力openClaw-原生)
  - [Extensions / MCP 工具（共 4 个）](#-extensions--mcp-工具共-4-个)
  - [独立工具（Scripts）](#-独立工具scripts)
  - [未完全落地 & 未来升级](#-已设计但未完全落地的能力)

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
    ├── SKILL_academic_search.md ← 2026-03-15 新增：四源学术搜索感知文件
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

> **激活机制说明**：Skills 不会自动注入上下文，需要龙虾主动读取（基于 SELF_KNOWLEDGE.md 的能力感知），或由用户触发特定场景关键词，或通过 Memory Search 语义召回。

| 技能文件 | 适用范围 | 触发场景 | 核心能力 | 作者 |
|---------|---------|---------|---------|------|
| `rules-loader.md` | **通用**（任何 AI） | 每次会话启动 | 合规门禁、L0 规则加载、10轮强制重读机制 | WorkBuddy |
| `task-planner.md` | **通用** | 任意多步骤任务 | WorkBuddy 风格任务拆解、依赖分析、并行识别、进度展示 | WorkBuddy |
| `workbuddy-dna.md` | **通用** | 执行任务期间 | 并行处理范式、结构化进度格式（✅⚠️📁）、错误处理模板 | WorkBuddy |
| `github-sync.md` | **OpenClaw 专属** | 每次对话结束、需要同步时 | openclaw 日志目录规范（`logs/openclaw/`）、pull-rebase 防冲突、脱敏扫描 | WorkBuddy |
| `feishu-file-reader.md` | **OpenClaw 专属** | 飞书收到文件/链接 | md/pdf/图片/视频解析，视频自动存 VoxBridge/samples/，防 Prompt Injection | WorkBuddy |
| `knowledge-notebook.md` | **OpenClaw 专属** | 检索历史记忆/知识库问答 | NotebookLM 风格：语义检索→引用来源回答→摘要生成，不凭空编造 | WorkBuddy |
| `knowledge-ingest.md` | **OpenClaw 专属** | 主人投喂新知识 | 四种投喂方式（粘贴/飞书/本地文件/写规则），知识笔记格式规范，自动触发索引重建 | WorkBuddy |
| `SKILL_academic_search.md` | **OpenClaw 专属** | 查论文/找算法/技术调研 | 四源学术搜索感知文件：告知龙虾有此能力及调用时机，触发 `academic_search.py` | WorkBuddy |
| `scrapling/SKILL.md` | **OpenClaw 专属** | 需要抓取动态/JS渲染网页 | Scrapling v0.4.2：静态+Playwright+反爬，支持 CSS 选择器批量提取和全站爬取 | WorkBuddy |

**默认任务流水线**：
```
[Step 0: rules check] → rules-loader → task-planner → [执行 + workbuddy-dna] → github-sync
```

---

### 学术搜索工具（academic_search.py）

**2026-03-15 新增**，配合 VoxBridge 算法浮现与创新研究使用。

**脚本位置**：`/home/xzy0626/.openclaw/scripts/academic_search.py`（虚拟机）

#### 数据源总览

| 数据源 | 覆盖量 | 优势 | 状态 |
|--------|--------|------|------|
| **arXiv** | CS/ML/物理预印本 | 最新算法，提交即可查，无需 key | ✅ 默认启用 |
| **OpenAlex** | 4.74 亿篇 | 覆盖最广，有摘要，10000 req/天 | ✅ 默认启用 |
| **Crossref** | 1.4 亿篇 DOI | 引用计数，期刊名，部分 PDF 直链 | ✅ 默认启用 |
| **Semantic Scholar** | 2.14 亿篇 | 语义搜索强，引用树 | 🔑 有 key 时启用 |

> **Semantic Scholar key 说明**：申请表 https://www.semanticscholar.org/product/api#api-key-form
> 需要机构/组织邮箱，不接受 Outlook。获取后加环境变量 `S2_API_KEY=xxx` 即可自动启用。

#### 标准调用方式

```bash
# 默认三源搜索（最稳定，全部无需 key）
python3 ~/.openclaw/scripts/academic_search.py "faster-whisper CTranslate2 quantization" --limit 8

# 限定年份（只看近 3 年）
python3 ~/.openclaw/scripts/academic_search.py "streaming ASR low latency" --year-from 2022

# JSON 输出（供 pipeline 程序解析）
python3 ~/.openclaw/scripts/academic_search.py "neural TTS prosody" --json

# 精确 DOI 查找（查完整元数据 + 引用关系）
python3 ~/.openclaw/scripts/academic_search.py --doi "10.48550/arXiv.2212.04356"

# 全四源（有 S2 key 时）
S2_API_KEY=your_key python3 ~/.openclaw/scripts/academic_search.py "whisper" --sources arxiv,openalex,crossref,s2
```

#### 龙虾触发场景（何时主动调用）

| 用户说的话 | 龙虾应该做的 |
|-----------|------------|
| "帮我找 XXX 算法的最新论文" | 直接调用 academic_search.py |
| "XXX 领域现在的进展怎么样" | 先搜，再综合回答 |
| "VoxBridge ASR 精度还不够，有没有新方案" | 搜相关论文后给建议 |
| "这篇论文的引用情况如何：[DOI]" | 用 `--doi` 精确查 |

> **注意**：龙虾开新会话时读 `SELF_KNOWLEDGE.md` 就会看到此能力说明，不需要每次提醒。
> 首次激活可以对龙虾说：「读一下 SELF_KNOWLEDGE.md 最后一节，然后搜一篇 faster-whisper 的论文。」

#### VoxBridge 专属搜索词表

| 研究方向 | 推荐关键词 |
|---------|----------|
| ASR 加速 | `faster-whisper CTranslate2 quantization inference` |
| 低延迟 ASR | `streaming speech recognition low latency real-time` |
| 翻译质量 | `argostranslate neural machine translation quality` |
| TTS 自然度 | `edge TTS neural text-to-speech prosody naturalness` |
| TTS 语速控制 | `speech synthesis rate control duration prediction` |
| 端到端降噪 | `whisper noise robust speech recognition` |
| 全 pipeline | `speech translation cascaded end-to-end system` |

---

### 能力激活可靠性说明

> 此节说明「已配置的能力是否真的会被用到」，以及改进思路。

#### 技能文件的加载机制

**重要理解**：skills/ 目录的文件**不会被自动注入上下文**。龙虾开启新会话时，AGENTS.md 的启动 Checklist 只要求读 6 个核心文件（AI_RULES / SOUL / USER / SELF_KNOWLEDGE / KNOWLEDGE_BASE / memory 日记）。skills/ 文件需要：

1. **龙虾主动去读**（基于 SELF_KNOWLEDGE.md 里对技能的感知）
2. **用户明确提及**某个场景（龙虾看到 TOOLS.md 里的决策树后调用）
3. **Memory Search 语义召回**（搜索时命中 skill 文件里的相关段落）

#### 各能力激活可靠性评估

| 能力 | 激活方式 | 可靠性 | 说明 |
|------|---------|--------|------|
| 安全规则（L0） | AGENTS.md 启动时强制读 | ⭐⭐⭐⭐⭐ | 硬性检查，不依赖自觉 |
| 工具选择（MCP） | TOOLS.md 启动时读 + 决策树 | ⭐⭐⭐⭐ | 已有明确决策树 |
| 学术搜索 | SELF_KNOWLEDGE.md 末尾章节 | ⭐⭐⭐ | **2026-03-15 已加固：能力写入自我认知文件** |
| knowledge-notebook | 仅在 skills/ 里，自我认知未提及 | ⭐⭐ | **待改进：SELF_KNOWLEDGE.md 未补充此能力** |
| knowledge-ingest | 同上 | ⭐⭐ | **待改进** |
| feishu-file-reader | TOOLS.md 决策树提到 | ⭐⭐⭐ | 决策树清晰，但龙虾需要读到对应行 |
| desktop-commander | TOOLS.md 有优先级说明 | ⭐⭐⭐ | 大文件/代码搜索时可能仍用普通 exec |
| 心跳 cron | AGENTS.md 定义，cron 待验证 | ⭐⭐ | **待验证：`crontab -l` 确认是否有心跳任务** |

#### 待改进项（按优先级）

| 优先级 | 改进项 | 具体操作 |
|--------|--------|---------|
| 🔴 高 | SELF_KNOWLEDGE.md 补充 knowledge-notebook/ingest 能力 | 在"我能做的事"章节加两行 |
| 🟡 中 | AGENTS.md Startup Checklist 加"感知 skills/ 目录" | 在启动清单第 9 项加：列出 skills/ 目录，建立技能感知 |
| 🟡 中 | 验证心跳 cron 是否运行 | SSH 进虚拟机 `crontab -l` + 查 last_heartbeat.txt 时间戳 |
| 🟢 低 | desktop-commander 触发条件更明确 | 在 TOOLS.md 加：文件 > 500 行必须用 desktop-commander |

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
│       ├── SKILL_academic_search.md   ← 2026-03-15 新增（学术搜索技能感知）
│       └── scrapling/                 ← 动态网页抓取
│
├── scripts/                           ← 虚拟机运行时脚本（不在 workspace 里）
│   └── academic_search.py             ← 2026-03-15 新增：四源学术搜索脚本
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

## 龙虾现有能力全景

### ✅ 已落地的核心能力

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
| **Memory Search** | ✅ **正式运行** | Qwen text-embedding-v3，65文件143块，Vector ready |
| **语义知识检索** | ✅ **正式运行** | knowledge-notebook Skill，NotebookLM 风格语义搜索 |
| **知识投喂** | ✅ **正式运行** | knowledge-ingest Skill，主人可随时向记忆库写入新知识 |
| **多模型体系** | ✅ **22个模型** | 含 Hunter/Healer Alpha（OpenRouter免费）、Qwen3、MiniMax M2.5等 |
| **学术搜索工具** | ✅ **2026-03-15 新增** | academic_search.py：arXiv+OpenAlex+Crossref 三源，无需任何 key |
| **能力感知加固** | ✅ **2026-03-15 完成** | SELF_KNOWLEDGE.md 末尾加入学术搜索能力章节，龙虾开新会话即知 |

---

## 🧩 Skills / Capabilities / Extensions 完整说明

> **三类概念的区分**：
> - **Skill（技能）**：存放在 `workspace/skills/` 的 Markdown 说明书，描述特定场景的工作流程，龙虾读后照执行。
> - **Capability（内置能力）**：OpenClaw 平台本身提供的原生功能（如 Memory Search、模型切换、命令执行）。
> - **Extension / MCP 工具**：通过 MCP 协议接入的外部工具进程，挂载在 `openclaw.json` 中。

---

### 📘 Skills 技能文件（共 9 个）

> 存放位置：`workspace/skills/`  
> 适用范围：标注了是否仅限 OpenClaw（龙虾），还是可移植到其他 AI

#### 1. `rules-loader.md` — 合规门禁
- **适用范围**：通用（任何 AI 可沿用）
- **作者**：WorkBuddy
- **何时触发**：每次会话启动时自动加载
- **核心能力**：
  - 读取并验证 `AI_RULES.md` L0 层规则
  - 每隔 10 轮对话强制重读，防止规则被「聊忘了」
  - `rule_sync_time.txt` 超 48h 提醒主人检查定时同步任务
- **影响**：这是整个安全体系的第一道关卡，L0 被跳过的风险在此拦截

---

#### 2. `task-planner.md` — 任务规划器
- **适用范围**：通用（WorkBuddy DNA 传授）
- **作者**：WorkBuddy
- **何时触发**：任意多步骤任务开始时
- **核心能力**：
  - 分析任务依赖图，识别可并行的子任务
  - 生成带编号的计划清单（`[并行]` / `[依赖步骤X]` 标注）
  - 展示执行进度（`⏳ 执行中` / `✅ 完成` / `⚠️ 注意`）
- **典型输出格式**：
  ```
  📋 任务计划：
    1. [并行] 步骤A + 步骤B
    2. 步骤C（依赖步骤A结果）
  ```

---

#### 3. `workbuddy-dna.md` — WorkBuddy 工作方式传承
- **适用范围**：通用（WorkBuddy DNA 传授）
- **作者**：WorkBuddy
- **何时触发**：执行任务期间
- **核心能力**：
  - 并行处理：识别独立子任务，同时发起，合并结果
  - 清晰汇报格式：开始列计划，执行中说原因，结束用结构化格式汇报
  - 错误处理范式：出错必须说「原因 + 影响范围 + 可选方案」，不能静默忽略
- **设计初衷**：WorkBuddy 把自己的工作方式「基因传授」给龙虾，确保两端行为风格一致

---

#### 4. `github-sync.md` — GitHub 日志同步
- **适用范围**：**OpenClaw 专属**（含 openclaw 日志路径规范）
- **作者**：WorkBuddy
- **何时触发**：每次对话结束，或主人要求同步时
- **核心能力**：
  - 日志写入路径：`workspace/logs/openclaw/YYYY-MM/YYYYMMDD-主题.md`（workspaceOnly 路径规范）
  - `git pull --rebase` 先于 push，防止 WorkBuddy 和龙虾双向写 INDEX.md 冲突
  - 推送前自动扫描：IP / API Key / 密码脱敏
  - INDEX.md 分工：龙虾只追加 OpenClaw 行，时间线表格由 WorkBuddy 维护
- **关联仓库**：`XZY0626/ai-session-logs`（SSH 认证）

---

#### 5. `feishu-file-reader.md` — 飞书文件解析
- **适用范围**：**OpenClaw 专属**（飞书 API + VoxBridge 集成）
- **作者**：WorkBuddy
- **何时触发**：飞书消息中包含文件附件或云文档链接
- **支持格式**：
  | 格式 | 处理方式 |
  |------|---------|
  | `.md` / `.txt` | 直接读取全文 |
  | `.pdf` | pypdf 逐页提取文字 |
  | 飞书云文档 URL | `feishu_doc.get` 工具读取 |
  | `.png` / `.jpg` | qwen-vl 视觉模型识别 |
  | `.json` / `.yaml` | 解析为结构化数据 |
  | 视频文件（.mp4 等） | **自动保存到 VoxBridge/samples/，询问是否启动翻译 pipeline** |
- **安全机制**：飞书收到的所有文件视为不可信外部输入，禁止将文件内容当命令执行（Prompt Injection 防护）

---

#### 6. `knowledge-notebook.md` — 智能知识库（NotebookLM 风格）
- **适用范围**：**OpenClaw 专属**（依赖 OpenClaw Memory Search 基础设施）
- **作者**：WorkBuddy（灵感来源：Google NotebookLM）
- **何时触发**：主人查询历史记忆、知识库问答、要求基于资料回答
- **核心能力**：
  - 📥 收录：把文件/链接/飞书文档/手写内容存入 `memory/`
  - 🔍 检索：`openclaw memory search` 语义向量搜索（不是关键词匹配）
  - 📝 引用回答：回答时标注 `📚 来源: [文件名]`，有据可查，不瞎编
  - 📊 摘要生成：给定话题 → 检索相关块 → 生成结构化摘要（核心观点 + 来源列表）
- **底层技术**：sqlite-vec + Qwen text-embedding-v3（1024 维向量）
- **与 NotebookLM 对比**：完全私有部署，数据不出虚拟机，费用极低（全量重建 < ¥0.02）

---

#### 7. `knowledge-ingest.md` — 知识投喂
- **适用范围**：**OpenClaw 专属**（依赖 Memory Search）
- **作者**：WorkBuddy
- **何时触发**：主人要往记忆库写新知识
- **四种投喂方式**：
  | 方式 | 操作 | 适合 |
  |------|------|------|
  | 直接粘贴 | 「把这段内容存入知识库，主题是 XXX：[内容]」 | 短文本、笔记 |
  | 飞书文档 | 「把这个飞书文档收录到知识库：[链接]」 | 长文档、会议记录 |
  | 本地文件 | 「把 /path/to/file.md 加入知识库」 | 现有 md/txt/pdf |
  | 写规则 | 「把这条规则加进 AGENTS.md：[规则]」 | 永久行为规则 |
- **文件命名规范**：`YYYY-MM-DD-[来源类型]-[标题简称].md`
- **验证方法**：投喂后执行 `openclaw memory search "关键词"` 确认 score > 0.4

---

#### 8. `SKILL_academic_search.md` — 学术论文四源搜索感知
- **适用范围**：**OpenClaw 专属**（依赖 `academic_search.py` 脚本）
- **作者**：WorkBuddy
- **何时触发**：主人提到查论文/找算法/技术调研
- **核心功能**：这是一个「能力感知文件」，告知龙虾：
  - 自己拥有 `academic_search.py` 工具（四源学术搜索）
  - 何时应该主动调用（不要说「我的知识截止到某年」）
  - 调用方式和参数
- **底层工具**：`/home/xzy0626/.openclaw/scripts/academic_search.py`（见下方 Capabilities 章节）

---

#### 9. `scrapling/SKILL.md` — 自适应网页爬虫
- **适用范围**：**OpenClaw 专属**（依赖 Python scrapling 库）
- **作者**：WorkBuddy（集成 D4Vinci/Scrapling v0.4.2）
- **安装日期**：2026-03-15
- **测试状态**：待集成（已安装，接口已定义，尚未生产验证）
- **何时触发**：需要抓取 JS 渲染的动态网页、进行反爬场景
- **核心能力**：
  - `fetch_html(url, mode='auto')` — 静态/动态自动切换
  - `extract_data(html, selectors)` — CSS 选择器批量提取
  - `crawl_site(start_url, rules, max_pages)` — 自动化全站爬取
  - Playwright 浏览器自动化（stealth 模式）
  - 反爬对抗：随机 UA、请求延迟、IP 代理池
- **与 fetch MCP 的区别**：fetch MCP 只能抓静态 HTML；scrapling 能渲染 JS，适合 SPA 和需要登录的页面
- **依赖**：`pip install scrapling[live]` + `playwright install chromium`

---

### ⚡ Capabilities 内置能力（OpenClaw 原生）

| 能力 | 描述 | 配置位置 | 状态 |
|------|------|---------|------|
| **Memory Search（语义记忆检索）** | 将对话和文件转为向量，支持语义相似度搜索；自动把检索到的文档片段注入对话上下文 | `openclaw.json` → `agents.defaults.memorySearch` | ✅ 运行中 |
| **多模型路由** | 22 个模型别名，支持运行时切换；不同任务指定不同模型 | `openclaw.json` → `models[]` | ✅ 运行中 |
| **命令执行（exec）** | 执行 shell 命令，带审批白名单（exec-approvals.json）；高危命令通过飞书等待审批 | `openclaw.json` + `openclaw-config/exec-approvals.json` | ✅ 运行中 |
| **文件读写（workspace）** | 默认限制在 `~/.openclaw/workspace/` 内；workspace 外需要主人当次对话明确授权 | `openclaw.json` → `workspaceOnly: true` | ✅ 运行中 |
| **飞书长连接（Bot）** | 接收飞书消息 → 调用 AI → 回复；支持文件/消息/云文档 | `feishu-bot/feishu_stepfun_bot.py` | ✅ 运行中 |
| **心跳机制** | 定期（≤2h）自动检查：gateway 存活、规则文件完整性、同步时间戳；写入 `last_heartbeat.txt` | `AGENTS.md` + `memory/last_heartbeat.txt` | 🟡 文件机制已落地，cron 触发待验证 |
| **版本自检** | 会话启动时验证 `AGENTS.md` 版本标记（`MODIFIED v5`）；标记丢失即停止工作并告警 | `AGENTS.md` 启动脚本 | ✅ 运行中 |
| **规则轮次重读** | 对话轮数计数器，每 10 轮强制重读 AI_RULES.md；防止规则被长对话「稀释」 | `memory/round_counter.txt` | ✅ 运行中 |
| **DUAL-SYNC 双端同步** | WorkBuddy 和龙虾共用 openclaw-config 仓库；任何一方修改配置后均同步到 GitHub | `scripts/sync_config_to_github.sh` | ✅ 运行中 |

---

### 🔌 Extensions / MCP 工具（共 4 个）

> MCP（Model Context Protocol）：OpenClaw 连接外部工具的标准协议，每个工具是一个独立进程，通过 stdio 与 gateway 通信。

| 工具 | 版本 | 适用范围 | 核心能力 | 安装位置 |
|------|------|---------|---------|---------|
| **filesystem** | 2026.1.14 | **通用** | 文件读写、目录列举、文件名搜索；访问范围限定 `/home/xzy0626` | `~/.local/lib/node_modules/@modelcontextprotocol/server-filesystem/` |
| **fetch** | 2025.4.7 | **通用** | 抓取网页并转为 Markdown，适合静态文档/博客/API 文档；JS 渲染场景需配合 scrapling | `~/.local/bin/mcp-server-fetch` |
| **websearch** | 1.0.3 | **通用** | 联网搜索，无需 API key；质量中等（可选升级 Tavily 提升质量） | `~/.local/lib/node_modules/websearch-mcp/` |
| **desktop-commander** | 0.2.38 | **通用** | 命令执行增强（流式读取大文件、ripgrep 代码搜索、进程管理）；相比原生 exec 更强 | `~/.local/lib/node_modules/@wonderwhy-er/desktop-commander/` |

**MCP 工具决策树**：

```
需要操作文件/目录  →  filesystem MCP
需要看网页内容    →  fetch MCP（URL 已知）
                  →  scrapling Skill（需要 JS 渲染）
需要搜索互联网    →  websearch MCP
需要执行命令/搜代码/管进程  →  desktop-commander MCP（优先于原生 exec）
飞书收到文件      →  feishu-file-reader Skill（先解析，再处理）
```

---

### 📚 独立工具（Scripts）

#### `academic_search.py` — 四源学术论文搜索

- **位置**：`/home/xzy0626/.openclaw/scripts/academic_search.py`（虚拟机）
- **适用范围**：OpenClaw 专属（VoxBridge 科研辅助）
- **创建日期**：2026-03-15
- **数据源**：

| 数据源 | 论文量 | 优势 | Key 要求 |
|--------|--------|------|---------|
| arXiv | CS/ML/物理预印本 | 最新算法（提交即可查） | ✅ 无需 |
| OpenAlex | 4.74 亿篇（全学科） | 覆盖最广，有摘要 | ✅ 无需 |
| Crossref | 1.4 亿篇 DOI | 引用计数、期刊名、精确元数据 | ✅ 无需 |
| Semantic Scholar | 2.14 亿篇 | 语义搜索、引用树 | ⚠️ 需机构邮箱申请 |

- **调用方式**：
  ```bash
  # 标准三源搜索（推荐）
  python3 /home/xzy0626/.openclaw/scripts/academic_search.py "关键词" --limit 8

  # 限定年份
  python3 /home/xzy0626/.openclaw/scripts/academic_search.py "关键词" --year-from 2022

  # JSON 输出（程序解析）
  python3 /home/xzy0626/.openclaw/scripts/academic_search.py "关键词" --json

  # 精确 DOI 查找
  python3 /home/xzy0626/.openclaw/scripts/academic_search.py --doi "10.48550/arXiv.2212.04356"
  ```

---

### 🟡 已设计但未完全落地的能力

| 能力 | 问题 | 建议 |
|------|------|------|
| **心跳 cron 触发** | `last_heartbeat.txt` 已存在，但触发 cron 未验证 | `crontab -l` 确认是否有心跳任务 |
| **rule_sync_time.txt 格式验证** | 是否被定时任务正确写入未验证 | 手动检查格式是否与 AGENTS.md 解析逻辑匹配 |
| **round_counter 计数逻辑** | 计数依赖龙虾自觉执行，无强制机制 | 在 rules-loader.md 里加强检查逻辑 |
| **MEMORY.md（长期记忆汇总）** | 定义了但无实际内容 | 安排龙虾做一次「提炼长期记忆」任务 |

---

### 🔮 已评估但暂未实施的升级

| 升级方向 | 触发条件 | 优先级 |
|---------|---------|--------|
| `@playwright/mcp` | fetch 抓不到 JS 渲染页面时（scrapling 已部分覆盖） | 中（遇到再装） |
| Tavily MCP | 需要更高质量搜索结果 | 低（申请 API key 后） |
| n8n 工作流编排 | VM 内存 ≥ 8GB，VoxBridge 需对接第三方 API | 低 |
| 心跳 cron 配置 | 下次例行检查时顺手完成 | 中 |
| 语音交互（STT/TTS 集成龙虾） | VoxBridge pipeline 稳定后 | 未来 |
| Semantic Scholar key | 有机构邮箱时申请 | 低（现有三源已满足） |

---

_本文档由 WorkBuddy 维护，所有 IP / 密钥 / Token 均已脱敏。_  
_最后更新：2026-03-16_
