# OpenClaw 网关断连修复 & 登录指南

## 版本：v1.1.0 (2026-03-10)

---

## 问题描述

虚拟机中 OpenClaw 网页端显示"已断开与网关的连接"，宿主机通过 `?token=` 方式可正常访问。

## 问题原因

通过分析 Gateway 日志 (`/tmp/openclaw/openclaw-2026-03-10.log`) 发现两个失败原因：

1. **`device-required`**：OpenClaw 2026.3.8 版本升级后，`gateway install --force` 重新生成了 service 文件，导致旧的 `OPENCLAW_GATEWAY_TOKEN` 嵌入 service 配置与 `openclaw.json` 中的 token 不一致。
2. **`token_mismatch`**：虚拟机本地 Firefox 浏览器缓存了旧 token 或未携带 token 访问。

## 修复步骤

### 1. 修复 Gateway Service 配置过期问题
```bash
# doctor 诊断发现 service 嵌入了旧 token
openclaw doctor

# 重新安装 service（清除嵌入的旧 token）
openclaw gateway install --force

# 重启生效
openclaw gateway restart
```

### 2. 确保 ControlUI 配置正确
```bash
openclaw config set gateway.controlUi.dangerouslyDisableDeviceAuth true
openclaw config set gateway.controlUi.allowInsecureAuth true
openclaw config set gateway.controlUi.allowedOrigins '["http://192.168.1.100:18789","http://localhost:18789","http://127.0.0.1:18789"]'
```

### 3. 重启 Gateway
```bash
openclaw gateway restart
```

---

## OpenClaw 登录方式汇总

### 方式一：宿主机浏览器（推荐）

在宿主机浏览器地址栏输入：
```
http://192.168.1.100:18789/?token=57056649c9bb83aa7eac7bbaf203b62ff728471ec009d6da
```

- 首次访问带 `?token=` 参数后，浏览器会保存认证状态
- 后续访问 `http://192.168.1.100:18789/` 即可自动登录
- 如果提示需要认证，重新带 `?token=` 访问即可

### 方式二：虚拟机本地浏览器（Firefox）

在虚拟机 Firefox 地址栏输入：
```
http://localhost:18789/?token=57056649c9bb83aa7eac7bbaf203b62ff728471ec009d6da
```

或：
```
http://127.0.0.1:18789/?token=57056649c9bb83aa7eac7bbaf203b62ff728471ec009d6da
```

**如果仍然显示断连**：
1. 按 `Ctrl+Shift+Delete` 清除浏览器缓存
2. 关闭所有 OpenClaw 标签页
3. 重新打开并访问带 `?token=` 的完整 URL

### 方式三：命令行直接对话

在虚拟机终端中直接使用 CLI：
```bash
# 直接对话
openclaw agent

# 指定模型对话
openclaw agent --model qwen-max
```

### 方式四：飞书机器人

在飞书中搜索并私聊 OpenClaw 机器人（AppID: `cli_a9247ccfec341cb5`），直接发消息即可。

---

## 当前配置状态

| 配置项 | 值 | 说明 |
|--------|-----|------|
| Gateway端口 | 18789 | HTTP + WebSocket 共用 |
| 绑定地址 | 0.0.0.0 (lan) | 局域网可访问 |
| 认证模式 | token | 需要 token 认证 |
| Token | `57056649c9bb83aa7eac7bbaf203b62ff728471ec009d6da` | 访问密钥 |
| 设备认证 | 已禁用 | `dangerouslyDisableDeviceAuth: true` |
| 防火墙 | UFW 已启用 | 仅允许 SSH(22) + 局域网18789 |

## 安全提醒

- Token 相当于访问密码，请勿泄露
- 当前 Gateway 绑定 `0.0.0.0`，局域网内所有设备可访问，已通过 UFW 防火墙限制仅 `192.168.1.0/24` 网段可达
- 建议定期更换 Token：`openclaw config set gateway.auth.token <新token>`
