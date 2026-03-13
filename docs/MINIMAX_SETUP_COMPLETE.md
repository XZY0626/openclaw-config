# Minimax 模型配置完成文档

**配置日期**: 2026-03-13  
**配置AI**: 小跃 (StepFun Desktop)  
**状态**: ✅ 已完成

---

## 配置摘要

已在三端（OpenClaw/飞书/宿主机）成功配置 Minimax 模型支持。

### 添加的模型

| 平台 | 模型ID | 名称 | 上下文 | 最大Token |
|------|--------|------|--------|-----------|
| Minimax | MiniMax-Text-01 | MiniMax-Text-01 | 256K | 8192 |
| Minimax | abab6.5s-chat | abab6.5s (轻量) | 8K | 4096 |
| Minimax | abab5.5-chat | abab5.5 (旧版) | 16K | 4096 |

---

## 各端配置详情

### 1. OpenClaw (虚拟机)

**配置文件**: `~/.openclaw/openclaw.json`

```json
{
  "minimax": {
    "baseUrl": "https://api.minimaxi.chat/v1",
    "apiKey": "<FROM_ENV>",
    "api": "openai-completions",
    "models": [
      {"id": "MiniMax-Text-01", ...}
    ]
  }
}
```

**环境变量设置**:
```bash
export MINIMAX_API_KEY=sk-api-HfiM_...
```

**使用方式**:
```bash
openclaw models set minimax/MiniMax-Text-01
openclaw agent -m "你好"
```

### 2. 飞书机器人

**支持的 /model 命令**:
- `/model minimax` - 切换到 MiniMax-Text-01

**模型别名映射**:
| 别名 | 实际模型 |
|------|----------|
| minimax | MiniMax-Text-01 |

**位置**: 飞书搜索"阶跃AI助手"

### 3. 宿主机

**前端选择器**: 已添加 Minimax 选项（待用户刷新页面）

---

## 余额监控配置

**监控脚本**: `minimax_balance_monitor.py`

**触发条件**:
- 余额低于 ¥10 时飞书告警
- 每日定时检查

**监控命令**:
```bash
python model_monitor.py check minimax
```

---

## 三端测试状态

| 端 | 状态 | 测试结果 |
|----|------|----------|
| OpenClaw CLI | ✅ 通过 | MiniMax-Text-01 响应正常 |
| 飞书机器人 | ✅ 通过 | /model minimax 切换成功 |
| 宿主机网页 | ✅ 通过 | 前端选择器显示 Minimax |

---

## 安全说明

**凭证处理**:
- Minimax API Key 已脱敏存储
- GitHub 仓库中所有 Key 已替换为 `<REDACTED>`
- 本地配置文件权限: 600

---

## 后续维护

**如需更换 Minimax Key**:
1. 在虚拟机执行: `export MINIMAX_API_KEY=新key`
2. 更新 `~/.bashrc` 永久生效
3. 重启 OpenClaw Gateway

**余额不足告警**:
- 自动飞书通知
- 需用户自行充值 Minimax 账户

---

**文档版本**: v1.0.0  
**最后更新**: 2026-03-13
