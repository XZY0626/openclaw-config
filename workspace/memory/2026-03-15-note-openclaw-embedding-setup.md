---
source: note
title: OpenClaw Embedding Configuration Guide
date: 2026-03-15
tags: [openclaw, embedding, memory-search, qwen, configuration]
---

# OpenClaw Embedding Configuration Guide

## Core Config Path

Memory Search config must be placed under agents.defaults.memorySearch in openclaw.json, NOT at the top level.

Correct configuration example:
- provider: openai (Aliyun Qwen uses OpenAI-compatible API)
- model: text-embedding-v3
- remote.baseUrl: https://dashscope.aliyuncs.com/compatible-mode/v1
- remote.apiKey: stored in auth-profiles.json

## Supported Providers

| Provider | Model | Use Case |
|----------|-------|----------|
| openai | text-embedding-v3 (Qwen) | Primary, best for Chinese |
| openai | text-embedding-3-small | Native English |
| local/ollama | nomic-embed-text | Fully offline |
| gemini | text-embedding-004 | Large free quota |

## Common Issues

- fetch failed: remote.baseUrl not configured, request hits api.openai.com by default
- Embeddings unavailable: API Key not set or wrong format
- 0 chunks indexed: need to run memory index --force

## NotebookLM Features Implemented

- Document ingestion: store any content to ~/.openclaw/workspace/memory/
- Semantic search: vector + FTS dual engine via sqlite-vec
- Source-attributed answers: always cite the source file
- Summary generation: structured key points extraction
- Multi-source support: files, links, Feishu docs, manual notes
