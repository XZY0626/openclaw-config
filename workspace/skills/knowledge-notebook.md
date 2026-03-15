---
name: knowledge-notebook
description: >
  Intelligent knowledge notebook for OpenClaw. Activate when the user wants to
  query past work logs, search historical memory, ask questions about previous
  sessions, retrieve stored knowledge, or get answers from the knowledge base.
  Trigger phrases: "查一下之前", "历史记录", "之前做过什么", "帮我找找记忆",
  "recall", "search my notes", "what did we do about", "knowledge base query".
activation: explicit
version: "1.0"
---

# knowledge-notebook — 智能知识库技能 v1.0

> **灵感来源**：Google NotebookLM 的核心工作方式
> **作者**：WorkBuddy（代 XZY0626 创建）
> **创建日期**：2026-03-15
> **适用 OpenClaw 版本**：v2026.3.x

---

## 💡 这个技能是做什么的？

NotebookLM 的精华是：**上传文档 → 自动建立语义索引 → 基于文档回答（不瞎编）→ 生成结构化摘要**。

这个技能把同样的能力带到你的 OpenClaw 龙虾身上：

- 📥 **收录**：把任何内容（文件、链接、飞书文档、手写笔记）存入知识库
- 🔍 **检索**：基于语义向量搜索找到相关内容（不是关键词匹配）
- 📝 **引用回答**：回答时标注出处，不瞎编不混淆
- 📊 **摘要生成**：一键生成文档大纲、要点提取、问答摘要
- 🗂️ **分类管理**：按来源/话题分组，方便归档

---

## 🛠️ 技术基础

| 组件 | 实现 |
|------|------|
| 向量检索 | OpenClaw Memory Search（sqlite-vec） |
| Embedding 模型 | 阿里云 Qwen `text-embedding-v3`（OpenAI 兼容接口） |
| 备选 Embedding | OpenAI `text-embedding-3-small` / 本地 Ollama `nomic-embed-text` |
| 存储 | `~/.openclaw/workspace/memory/` 目录下的 `.md` 文件 |
| 全文检索 | SQLite FTS5（自动与向量检索联合） |

---

## 📋 使用说明

### 收录文档

主人发出以下任意指令时，龙虾应执行收录流程：

- "把这段内容存入知识库"
- "记住这个文档"
- "把 [来源] 加入我的笔记本"
- "学习这个"
- 发送文件/链接 + "存起来" / "收录"

**收录流程**：

1. 提取内容（读取文件 / 下载链接 / 读飞书文档）
2. 在 `~/.openclaw/workspace/memory/` 下创建 `.md` 文件，格式见下方
3. 运行 `~/.local/bin/openclaw memory index --force` 重建索引
4. 确认收录成功，报告文件路径和 chunk 数量

**知识库文件命名规则**：

```
memory/
├── {YYYY-MM-DD}-{来源类型}-{简短标题}.md
│
├── 示例:
├── 2026-03-15-feishu-产品需求文档v2.md
├── 2026-03-15-url-openclaw官方文档.md
├── 2026-03-15-note-项目背景说明.md
└── 2026-03-15-file-技术方案设计.md
```

**文件格式模板**：

```markdown
---
source: feishu|url|file|note|manual
url: https://... (如有)
title: 文档标题
date: YYYY-MM-DD
tags: [标签1, 标签2]
---

# 文档标题

[正文内容...]
```

---

### 检索查询

主人提问时，龙虾应：

1. **先搜索**：`~/.local/bin/openclaw memory search --query "问题关键词" --max-results 5`
2. **评估相关性**：查看搜索结果，判断是否有足够相关内容
3. **有相关内容**：基于搜索结果回答，在回答末尾标注 `📚 来源: [文件名]`
4. **无相关内容**：明确告知"知识库中没有找到相关信息"，**不要凭空编造**

触发检索的问题关键词：
- "根据我的资料..."
- "我之前存过..."
- "知识库里..."
- "查一下..."（非网络搜索场景）

---

### 生成摘要

主人发出以下指令时：

- "总结一下知识库里关于 [话题] 的内容"
- "给我列出 [文档] 的要点"
- "知识库里有哪些关于 [话题] 的资料？"

**摘要流程**：

1. 搜索相关 chunks：`openclaw memory search --query "[话题]" --max-results 10`
2. 读取相关文件完整内容
3. 生成结构化摘要，格式：
   - 📌 核心观点（3-5条）
   - 📝 详细要点
   - 🔗 来源文件列表

---

### 知识库管理

| 指令 | 操作 |
|------|------|
| "列出知识库" / "我有哪些笔记" | `ls ~/.openclaw/workspace/memory/` |
| "删除 [文档]" | 删除对应 .md 文件 + `openclaw memory index --force` |
| "更新 [文档]" | 修改对应 .md 文件 + 重建索引 |
| "知识库状态" | `openclaw memory status` |
| "重建索引" | `openclaw memory index --force` |

---

## ⚙️ Embedding Provider 切换指南

当前使用**阿里云 Qwen text-embedding-v3**（推荐，中文效果最好）。

如需切换：

### 切换到 OpenAI 原生

```bash
# 修改 openclaw.json
# agents.defaults.memorySearch.remote.baseUrl → 删除（使用默认 api.openai.com）
# agents.defaults.memorySearch.model → "text-embedding-3-small"
# agents.defaults.memorySearch.remote.apiKey → OpenAI API Key
openclaw memory index --force
```

### 切换到本地 Ollama（完全免费离线）

```bash
# 1. 安装 Ollama 和 nomic-embed-text 模型
# ollama pull nomic-embed-text
# 2. 修改配置
# agents.defaults.memorySearch.provider → "ollama"
# agents.defaults.memorySearch.model → "nomic-embed-text"
# （无需 remote 字段）
openclaw memory index --force
```

### 切换到 Gemini（免费额度大）

```bash
# agents.defaults.memorySearch.provider → "gemini"
# agents.defaults.memorySearch.model → "text-embedding-004"
# agents.defaults.memorySearch.remote.apiKey → Google API Key
openclaw memory index --force
```

---

## 🔒 安全规则

1. **不读取 C 盘文件**（遵守 AI_RULES.md L0.1）
2. **API Key 不输出**：memory 配置中的 apiKey 不得在对话中显示明文
3. **收录前确认**：收录外部链接内容前，告知主人将保存的内容摘要
4. **知识库内容不外传**：memory 目录内容不推送到任何 GitHub 仓库
5. **收录大文件需分块**：单个文件超过 50KB 时，自动按章节拆分收录

---

## 🐛 故障排查

| 症状 | 原因 | 解决方案 |
|------|------|---------|
| `Memory index failed: fetch failed` | baseUrl 未配置，请求打到 api.openai.com | 检查 `agents.defaults.memorySearch.remote.baseUrl` |
| `Embeddings: unavailable` | API Key 未设置或格式错误 | 检查 `agents.defaults.memorySearch.remote.apiKey` |
| `Indexed: 0/X files · 0 chunks` | 索引 dirty，未实际建立向量 | 运行 `openclaw memory index --force` |
| `auth-profiles.json not found` | 文件不存在或路径错误 | 路径：`~/.openclaw/agents/main/agent/auth-profiles.json` |
| 搜索无结果 | 知识库为空或关键词偏差 | 先确认 `memory status` 显示 indexed > 0，再换不同关键词 |

---

## 📌 与 NotebookLM 的功能对比

| 功能 | NotebookLM | 龙虾 knowledge-notebook |
|------|-----------|------------------------|
| 文档上传 | ✅ Web UI | ✅ 对话指令 / 飞书发送 |
| 语义搜索 | ✅ Google 向量 | ✅ sqlite-vec + Qwen embedding |
| 基于文档回答 | ✅ 自动引用 | ✅ 手动标注来源 |
| 生成摘要 | ✅ Audio Overview | ✅ 文字摘要/要点提取 |
| 多来源支持 | ✅ PDF/Doc/网页 | ✅ 文件/链接/飞书/手写 |
| 私有部署 | ❌ 必须用 Google | ✅ 完全本地，数据不出虚拟机 |
| 费用 | 免费/付费 | 极低（Qwen embedding 约 ¥0.0007/千token） |
