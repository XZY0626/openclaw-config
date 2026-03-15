---
name: knowledge-ingest
description: >
  Knowledge ingestion skill for OpenClaw. Activate when the user wants to
  teach the agent new knowledge, send documents for the agent to learn,
  feed reference material, or update the agent's knowledge base.
  Trigger phrases: "让龙虾学习", "给龙虾发文案", "投喂知识", "存入记忆",
  "learn this", "save this knowledge", "remember this document".
activation: explicit
---

# knowledge-ingest Skill

## 功能说明

这个 Skill 让你轻松把任何内容投喂给龙虾，让她永久记住并能用语义搜索找到。

## 知识的存储位置

所有知识笔记存放在：`~/.openclaw/workspace/memory/`

文件命名规范：`YYYY-MM-DD-[主题简称].md`

Memory Search 会自动索引这个目录（实时监听，无需手动刷新）。

---

## 方式一：直接粘贴内容（最快）

**适合**：你复制了一段文字、截图文字、网页内容

对龙虾说：

> 把这段内容存入你的记忆库，主题是"[主题]"：
> [粘贴内容]

龙虾会自动：
1. 创建 `memory/YYYY-MM-DD-[主题].md` 文件
2. 添加 frontmatter（来源、标题、标签）
3. `openclaw memory index` 触发重建索引

---

## 方式二：飞书文档链接（推荐用于长文档）

**适合**：飞书里的技术方案、产品文档、会议记录

对龙虾说：

> 帮我把这个飞书文档收录到知识库：[飞书链接]

龙虾会用 feishu-doc Skill 读取全文，然后按 memory 格式存储。

---

## 方式三：本地文件路径

**适合**：你有 .md / .txt / .pdf 文件

对龙虾说：

> 把 /path/to/file.md 加入你的知识库

---

## 方式四：规则/原则类（直接写进 AGENTS.md）

**适合**：你想让龙虾**永远遵守**的行为规则，不只是"记住"

对龙虾说：

> 把这条规则加进你的 AGENTS.md：[规则内容]

AGENTS.md 每次对话都会被读取，适合放核心行为准则。

---

## 知识笔记格式规范

```markdown
---
source: note
title: [标题]
date: YYYY-MM-DD
tags: [标签1, 标签2, 标签3]
---

# [标题]

[内容正文]
```

`source` 字段说明：
- `note` — 手写笔记、总结
- `doc` — 外部文档（飞书、URL）
- `log` — 操作日志片段
- `rule` — 行为规则

---

## 投喂后如何验证

投喂完毕后，可以让龙虾做验证：

> 用记忆搜索找一下关于"[关键词]"的内容，看看刚才的笔记有没有被索引到

龙虾会执行 `openclaw memory search "[关键词]"` 并展示结果。

---

## 当前知识库状态

- **索引文件**：62 个（memory/ + workspace 根目录 .md 文件）
- **向量块数**：137 chunks
- **Embedding 模型**：Qwen text-embedding-v3（中文效果最佳）
- **搜索得分参考**：score > 0.5 为相关，> 0.7 为高度相关

---

## 不适合存入记忆库的内容

- 含个人隐私、密码、API Key（会进入可检索索引）
- 非常临时的草稿（用完即删的内容）
- 超大文件（建议先摘要再存入）
