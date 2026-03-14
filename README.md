# OpenClaw Config 🦞

OpenClaw AI Agent 的完整配置管理仓库，包含模型配置、虚拟机脚本、多平台模型监控与飞书通知审批。

> **当前版本**：OpenClaw v2026.3.11 | **主力 AI**：WorkBuddy（腾讯云）| **接入方式**：Tailscale HTTPS

---

## 📁 文件结构

```
openclaw-config/
├── README.md                          # 本文件
│
├── feishu-bot/                        # 飞书机器人相关
│   ├── feishu_stepfun_bot.py          # 飞书机器人主程序（阶跃AI助手，长连接模式）
│   ├── approval_handler.py            # 模型审批处理模块
│   ├── model_monitor.py               # 多平台模型更新监控服务
│   ├── check_models_task.bat          # Windows计划任务调用脚本
│   └── 启动机器人.bat                  # 飞书机器人启动脚本
│
├── openclaw-frontend/                 # OpenClaw前端相关（v2026.3.8及以下适用）
│   ├── model-selector-v2.js           # 自定义模型选择器插件（历史版本）
│   └── index.html                     # 修改后的OpenClaw入口页面（历史版本）
│
├── openclaw-scripts/                  # 虚拟机端脚本
│   ├── backup.sh                      # 手动备份脚本
│   ├── restore.sh                     # 升级后恢复脚本
│   └── upgrade-watch.sh               # 版本监控钩子
│
├── openclaw-config/                   # OpenClaw配置参考
│   └── exec-approvals.json            # 执行审批白名单
│
├── ssh-tools/                         # SSH远程管理工具
│   ├── ssh_cmd.py                     # SSH命令执行工具
│   ├── ssh_sudo.py                    # SSH sudo命令工具
│   ├── ssh_sudo_batch.py              # SSH批量sudo工具
│   ├── ssh_read_config.py             # SSH读取配置工具
│   ├── ssh_update_config.py           # SSH更新配置工具
│   └── ssh_upload_approvals.py        # SSH上传审批配置工具
│
└── deploy/                            # 部署脚本
    ├── deploy_to_vm.py                # 一键部署到虚拟机
    ├── setup_models.py                # 多平台模型初始化配置
    ├── update_keys.py                 # API密钥更新脚本
    ├── inject_selector_v2.py          # 前端插件注入脚本（历史版本）
    └── fix_index.py                   # index.html修复脚本（历史版本）
```

---

## 🏗️ 架构说明

### 当前部署拓扑（v2026.3.11 + Tailscale）

```
宿主机 (Windows)                        虚拟机 (Ubuntu / VMware)
┌──────────────────────┐               ┌──────────────────────────────┐
│ WorkBuddy            │   SSH/SFTP    │ OpenClaw Gateway             │
│ (腾讯云，当前主力)    │◄─────────────►│ 端口 18789，仅绑定 loopback  │
│                      │               │                              │
│ 飞书机器人           │               │ Tailscale Serve              │
│ (阶跃AI助手)         │               │ ↑ HTTPS 对外暴露             │
│                      │               │                              │
│ 模型更新监控         │               │ 备份/恢复脚本                │
│ (每6小时)            │               │ openclaw.json 配置           │
└──────────────────────┘               └──────────────────────────────┘
         │                                         │
         ▼                                         ▼
   飞书通知/审批新模型              Tailscale HTTPS 域名对外提供访问
                                   （宿主机/飞书均通过此地址连接）
```

> **历史说明**：2026-03-10 至 2026-03-12 期间，小跃（StepFun Desktop）负责 OpenClaw 初期搭建与配置；2026-03-13 起由 WorkBuddy 全面接管运维与管理工作。

### 网络访问方式

| 访问方自 | 访问地址 | 方式 |
|---------|---------|------|
| 宿主机浏览器 | `https://[TAILSCALE域名]` | Tailscale Serve HTTPS |
| 飞书 OpenClaw 插件 | Tailscale HTTPS 域名 | Tailscale Serve HTTPS |
| 虚拟机本地 | `http://localhost:18789` | 本地直连 |

### 飞书机器人

- **阶跃AI助手**（AppID 已脱敏）：接入阶跃星辰 API 的智能对话，支持模型审批指令
- **OpenClaw机器人**（AppID 已脱敏）：OpenClaw Agent 对话频道

### 模型平台（当前接入，共 45+ 个模型）

| 平台 | Provider 前缀 | 模型数 | 说明 |
|------|-------------|--------|------|
| 阿里云百炼 (DashScope) | `dashscope-*` | 15 | 通用/编程/推理/视觉 |
| 阶跃星辰 (StepFun) | `stepfun` | 8 | — |
| 硅基流动 (SiliconFlow) | `siliconflow` | 6 | — |
| OpenRouter | `openrouter` | 12 | 聚合多家模型 |
| MiniMax | `minimax` | 4 | M1/M2/M2.5/Text-01 |

---

## 🔒 安全配置说明

### 当前安全措施

| 措施 | 状态 | 说明 |
|------|------|------|
| Gateway 绑定 loopback | ✅ 已配置 | 禁止直接局域网访问，防止公网暴露 |
| Tailscale Serve HTTPS | ✅ 已配置 | 唯一对外访问通道，自动管理证书 |
| 配置文件 chmod 600 | ✅ 已配置 | `~/.openclaw/openclaw.json` 仅 owner 可读写 |
| 日志敏感字段脱敏 | ✅ 已配置 | `logging.redact` 防止明文凭证进入日志 |
| API Key 本地存储 | ✅ 已配置 | 仅存于虚拟机配置文件，不入 GitHub |

### v2026.3.11 重要变更记录

| 变更项 | v2026.3.8 | v2026.3.11 |
|--------|-----------|------------|
| API 路径 | `/api/v1/...` | `/...` |
| 模型列表来源 | 前端 JS 文件 | 后端 openclaw.json（更稳定）|
| 认证机制 | Token 登录 | Token + 设备身份验证（需 HTTPS）|
| 前端架构 | 含独立 model-selector-v2.js | Vite 单文件打包 |

> **注意**：v2026.3.11 后，自定义前端文件（model-selector-v2.js）方式已失效，模型配置统一在 `openclaw.json` 的 `providers` 字段管理，升级不会覆盖配置文件。

---

## 🚀 常用操作

### 重启 Gateway

```bash
# 注意：进程名超15字符，必须用 -f 参数
kill $(pgrep -f openclaw-gateway) && sleep 2 && nohup openclaw gateway start > ~/openclaw.log 2>&1 &
```

### 查看 Gateway 运行状态

```bash
ps aux | grep openclaw
tail -f ~/openclaw.log
```

### 手动备份配置

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%Y%m%d)
```

### 手动检查模型更新

```bash
python feishu-bot/model_monitor.py check
```

---

## 📝 飞书审批指令

在飞书中给「阶跃AI助手」发送以下消息：

| 指令 | 说明 |
|------|------|
| `批准` / `approve` | 将待审批的新模型加入 OpenClaw |
| `拒绝` / `reject` | 忽略本次新模型通知 |
| `检查模型` / `check models` | 立即触发模型更新检查 |
| `/clear` | 清除对话记忆 |

---

## 🔄 自动化机制

| 机制 | 频率 | 运行位置 | 说明 |
|------|------|---------|------|
| 模型更新监控 | 每6小时 | 宿主机计划任务 | 扫描5个平台API，发现新模型飞书通知 |
| 配置备份 | 手动触发 | 虚拟机 | 升级前手动备份，保留30天 |

---

## ⚠️ 注意事项

1. **OpenClaw 升级后**：v2026.3.11+ 无需恢复前端注入，配置文件不会被覆盖；但需验证 API 路径、认证方式等是否有变化
2. **API 密钥安全**：所有密钥存储于虚拟机 `~/.openclaw/openclaw.json`（chmod 600），不入 GitHub
3. **Tailscale 持久化**：重启虚拟机后需确认 `tailscale serve` 是否自动恢复，必要时手动执行 `sudo tailscale serve --bg 18789`
4. **访问 HTTPS 必要性**：v2026.3.11 设备身份验证仅在 HTTPS 环境下工作，不可退回纯 HTTP 访问

## 📋 关联仓库

| 仓库 | 用途 |
|------|------|
| [ai-rules](https://github.com/XZY0626/ai-rules) | AI执行规则文件 |
| [ai-session-logs](https://github.com/XZY0626/ai-session-logs) | AI对话日志记录 |
| [openclaw-config](https://github.com/XZY0626/openclaw-config) | 本仓库 — OpenClaw配置管理 |
