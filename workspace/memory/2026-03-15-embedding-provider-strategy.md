---
source: note
title: Embedding Provider Strategy - Universal Design for Memory Search
date: 2026-03-15
tags: [openclaw, embedding, memory-search, strategy, provider]
---

# Embedding Provider 通用方案

## 核心架构说明

Memory Search 和对话模型是**完全独立**的两个组件：

```
对话模型（stepfun/step-3.5-flash）  ←→  负责理解和生成回答
        ↑
  Memory Search 检索到的相关文本段落
        ↑
Embedding 模型（Qwen text-embedding-v3）  ←→  负责把文字转成向量数字
```

两者可以任意组合，互不干扰。用什么对话模型，不影响用什么 embedding 模型。

## 当前配置（推荐保持）

- **对话模型**：openrouter/stepfun/step-3.5-flash:free
- **Embedding 模型**：Qwen text-embedding-v3（阿里云 Dashscope）
- **配置路径**：agents.defaults.memorySearch.remote.baseUrl = https://dashscope.aliyuncs.com/compatible-mode/v1
- **费用**：极低，0.0007元/千token，日常使用几乎免费

## 备选 Provider（按优先级排列）

### 方案 B：OpenAI text-embedding-3-small

适用场景：英文文档为主时，OpenAI 官方 embedding 效果好

```json
"memorySearch": {
  "enabled": true,
  "provider": "openai",
  "model": "text-embedding-3-small",
  "remote": {
    "baseUrl": "https://api.openai.com/v1",
    "apiKey": "<OPENAI_API_KEY>"
  }
}
```

费用：$0.02/百万 token

### 方案 C：Ollama 本地（完全离线）

适用场景：不想联网，或者网络不稳定时

前提：虚拟机上先安装 Ollama 并 pull nomic-embed-text

```json
"memorySearch": {
  "enabled": true,
  "provider": "openai",
  "model": "nomic-embed-text",
  "remote": {
    "baseUrl": "http://localhost:11434/v1",
    "apiKey": "ollama"
  }
}
```

费用：免费，但需要本地 GPU/CPU 资源

### 方案 D：Gemini text-embedding-004

适用场景：OpenRouter/Qwen 都挂的时候作为备份

```json
"memorySearch": {
  "enabled": true,
  "provider": "gemini",
  "model": "text-embedding-004",
  "remote": {
    "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
    "apiKey": "<GOOGLE_API_KEY>"
  }
}
```

费用：Google 有大额免费额度

## 为什么 OpenRouter 不支持 Embedding

OpenRouter 是对话模型路由，不提供 embedding API（经过测试确认，返回 0 个 embedding 模型）。  
StepFun 的 step-3.5 也只是对话模型，没有官方 embedding 端点。

**结论：当前方案（Qwen embedding + StepFun 对话）是最优搭配，无需更改。**

## 切换 Provider 的操作步骤

1. 编辑 `~/.openclaw/openclaw.json`
2. 修改 `agents.defaults.memorySearch` 块
3. 执行 `openclaw memory index --force` 重新建立向量索引（切换模型后维度可能变化）
4. 执行 `openclaw memory status` 确认 Embeddings: ready
