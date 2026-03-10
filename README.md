# OpenClaw Config 🦞

OpenClaw AI Agent 的完整配置管理仓库，包含前端插件、模型配置、自动备份恢复、多平台模型更新监控与飞书通知审批。

## 📁 文件结构

```
openclaw-config/
├── README.md                          # 本文件
│
├── feishu-bot/                        # 飞书机器人相关
│   ├── feishu_stepfun_bot.py          # 飞书机器人主程序（阶跃AI助手，长连接模式）
│   ├── approval_handler.py            # 模型审批处理模块（集成到飞书机器人）
│   ├── model_monitor.py               # 多平台模型更新监控服务
│   ├── check_models_task.bat          # Windows计划任务调用脚本
│   └── 启动机器人.bat                  # 飞书机器人启动脚本
│
├── openclaw-frontend/                 # OpenClaw前端插件
│   ├── model-selector-v2.js           # 模型选择器插件（注入到聊天页面）
│   └── index.html                     # 修改后的OpenClaw入口页面（含插件引用）
│
├── openclaw-scripts/                  # 虚拟机端脚本
│   ├── backup.sh                      # 自动备份脚本
│   ├── restore.sh                     # 升级后自动恢复脚本
│   └── upgrade-watch.sh               # 版本监控钩子（crontab每5分钟）
│
├── openclaw-config/                   # OpenClaw配置文件
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
    ├── inject_selector_v2.py          # 前端插件注入脚本
    └── fix_index.py                   # index.html修复脚本
```

## 🏗️ 架构说明

### 部署拓扑
```
宿主机 (Windows)                     虚拟机 (Ubuntu)
┌─────────────────────┐              ┌─────────────────────┐
│ 飞书机器人           │   SSH/SFTP   │ OpenClaw Gateway     │
│ (阶跃AI助手)         │◄────────────►│ (端口18789)          │
│                     │              │                     │
│ 模型更新监控         │              │ 备份/恢复脚本        │
│ (每6小时)            │              │ 版本监控钩子         │
│                     │              │ (每5分钟)            │
└─────────────────────┘              └─────────────────────┘
         │                                    │
         ▼                                    ▼
   飞书通知用户                          自动恢复前端注入
   (新模型审批)                         (升级后自动触发)
```

### 飞书机器人
- **阶跃AI助手**（AppID: `cli_a9251e97b1399cd6`）：接入阶跃星辰API的智能对话
- **OpenClaw机器人**（AppID: `cli_a9247ccfec341cb5`）：OpenClaw Agent对话

### 模型平台
已接入4个平台，共40+个模型：
| 平台 | Provider前缀 | 模型数 |
|------|-------------|--------|
| 阿里云百炼 (DashScope) | `dashscope-*` | 15 |
| 阶跃星辰 (StepFun) | `stepfun` | 8 |
| 硅基流动 (SiliconFlow) | `siliconflow` | 6 |
| OpenRouter | `openrouter` | 11 |

### 安全措施
- UFW防火墙：仅允许SSH(22)和局域网访问OpenClaw(18789)
- 配置文件权限：`chmod 600`，仅owner可读写
- 执行审批白名单：限制OpenClaw可执行的命令

## 🚀 快速开始

### 1. 部署到虚拟机
```bash
python deploy/deploy_to_vm.py
```

### 2. 启动飞书机器人
```bash
双击 feishu-bot/启动机器人.bat
```

### 3. 手动检查模型更新
```bash
python feishu-bot/model_monitor.py check
```

### 4. 手动备份OpenClaw
```bash
# SSH到虚拟机后
bash ~/.openclaw/scripts/backup.sh
```

### 5. 升级后手动恢复
```bash
# SSH到虚拟机后
bash ~/.openclaw/scripts/restore.sh
openclaw gateway restart
```

## 🔄 自动化机制

| 机制 | 频率 | 位置 | 说明 |
|------|------|------|------|
| 版本监控 | 每5分钟 | 虚拟机crontab | 检测OpenClaw升级，自动恢复前端注入 |
| 模型更新监控 | 每6小时 | 宿主机计划任务 | 扫描4个平台API，发现新模型飞书通知 |
| 自动备份 | 升级时触发 | 虚拟机 | 升级前自动备份，保留30天 |

## 📝 飞书审批指令

在飞书中给"阶跃AI助手"发送以下消息：
- `批准` / `approve` — 将待审批的新模型加入OpenClaw
- `拒绝` / `reject` — 忽略本次新模型
- `检查模型` / `check models` — 立即触发模型更新检查
- `/clear` — 清除对话记忆

## ⚠️ 注意事项

1. **OpenClaw升级**后前端注入会被覆盖，`upgrade-watch.sh`会自动恢复（每5分钟检查）
2. **API密钥**存储在配置文件中，已设置`chmod 600`保护，请勿公开
3. 本仓库中的配置文件**不包含真实API密钥**（已在.gitignore中排除敏感文件）
